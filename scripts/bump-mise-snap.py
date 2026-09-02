#!/usr/bin/env python3
"""Update the pinned mise Snap Store revision for every published architecture."""

import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
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
    }
    if not releases:
        raise ValueError(f"no latest/stable releases found for {STORE_URL}")
    if len({version for version, _ in releases.values()}) != 1:
        raise ValueError(f"latest/stable versions differ by architecture: {releases}")
    return releases


def write_hook(releases: dict[str, tuple[str, int]]) -> None:
    version = next(iter(releases.values()))[0]
    arch_cases = "\n".join(
        f"    {arch}) revision={revision} ;;"
        for arch, (_, revision) in sorted(releases.items())
    )
    block = (
        'case "$(dpkg --print-architecture)" in\n'
        f"    # pinned mise {version} (latest/stable)\n"
        f"{arch_cases}\n"
        "    *)\n"
        '        echo "mise SDK does not support this architecture" >&2\n'
        "        exit 1\n"
        "        ;;\n"
        "esac"
    )
    path = ROOT / "hooks/setup-base"
    content = path.read_text()
    content, count = re.subn(
        r'case "\$\(dpkg --print-architecture\)" in\n.*?\nesac',
        block,
        content,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError(f"could not find the architecture case block in {path}")
    path.write_text(content)


def main() -> None:
    releases = store_releases()
    write_hook(releases)
    version = next(iter(releases.values()))[0]
    print(
        f"mise {version}: "
        + ", ".join(
            f"{arch} revision {revision}"
            for arch, (_, revision) in sorted(releases.items())
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError) as error:
        sys.exit(f"error: {error}")