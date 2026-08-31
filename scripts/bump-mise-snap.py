#!/usr/bin/env python3
"""Update the pinned mise Snap Store version and revisions."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURES = ("amd64", "arm64")
STORE_URL = "https://api.snapcraft.io/v2/snaps/info/mise"


def store_releases() -> dict[str, tuple[str, int]]:
    request = Request(STORE_URL, headers={"Snap-Device-Series": "16"})
    with urlopen(request) as response:  # noqa: S310 - fixed Snap Store endpoint
        channels = json.load(response)["channel-map"]

    releases = {
        entry["channel"]["architecture"]: (entry["version"], entry["revision"])
        for entry in channels
        if entry["channel"]["track"] == "latest"
        and entry["channel"]["risk"] == "stable"
        and entry["channel"]["architecture"] in ARCHITECTURES
    }
    if set(releases) != set(ARCHITECTURES):
        raise ValueError(f"latest/stable missing architectures: {ARCHITECTURES}")
    if len({version for version, _ in releases.values()}) != 1:
        raise ValueError(f"latest/stable versions differ by architecture: {releases}")
    return releases


def update_version(version: str) -> None:
    subprocess.run(
        [
            "yq",
            "--inplace",
            '.version = strenv(VERSION) | .version style="double"',
            ROOT / "sdkcraft.yaml",
        ],
        check=True,
        env={**os.environ, "VERSION": version},
    )


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    content = path.read_text()
    content, count = re.subn(pattern, replacement, content, count=1, flags=re.MULTILINE)
    if count != 1:
        raise ValueError(f"expected one match for {pattern!r} in {path}")
    path.write_text(content)


def main() -> None:
    releases = store_releases()
    version = releases["amd64"][0]
    update_version(version)
    for architecture, (_, revision) in releases.items():
        replace_once(
            ROOT / "hooks/setup-base",
            rf"^    {architecture}\) revision=\d+ ;;$",
            f"    {architecture}) revision={revision} ;;",
        )
    print(
        f"mise {version}: "
        + ", ".join(
            f"{architecture} revision {releases[architecture][1]}"
            for architecture in ARCHITECTURES
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError) as error:
        sys.exit(f"error: {error}")
