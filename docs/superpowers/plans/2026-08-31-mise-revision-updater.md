# Mise Revision Updater Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep the SDK metadata and architecture-specific pinned mise snap revisions aligned with the Snap Store's `latest/stable` release.

**Architecture:** A stdlib-only Python script fetches the public Snap Store v2 response once, selects `latest/stable` records for the SDK's `amd64` and `arm64` platforms, and rejects mismatched versions. It rewrites only the SDK version and revisions embedded in the setup hook. The setup hook detects the current Debian architecture and installs its matching pinned revision.

**Tech Stack:** Python 3 standard library, POSIX shell, Snap Store v2 API, ShellCheck.

---

### Task 1: Add a Store metadata updater

**Files:**
- Create: `scripts/bump-mise-snap.py`
- Modify: `sdkcraft.yaml:4`
- Modify: `hooks/setup-base:4-11`

- [ ] **Step 1: Write the updater**

```python
#!/usr/bin/env python3
"""Update the pinned mise Snap Store version and revisions."""
```

Fetch `https://api.snapcraft.io/v2/snaps/info/mise` with `Snap-Device-Series: 16`, extract the `latest/stable` records for `amd64` and `arm64`, require one shared version, then replace the `version:` value in `sdkcraft.yaml` and each architecture revision in `hooks/setup-base`.

- [ ] **Step 2: Pin the hook by detected architecture**

```sh
case "$(dpkg --print-architecture)" in
    amd64) revision=207 ;;
    arm64) revision=208 ;;
    *) echo "unsupported architecture" >&2; exit 1 ;;
esac
snap install mise --classic --revision="$revision"
```

- [ ] **Step 3: Exercise the updater**

Run: `python3 scripts/bump-mise-snap.py`

Expected: reports `mise 2026.8.16: amd64 revision 207, arm64 revision 208` and leaves those values in the two project files.

### Task 2: Record the architecture invariant

**Files:**
- Modify: `README.md:45-46`

- [ ] **Step 1: Document exact pinning behavior**

Add text that the SDK pins one Store revision per architecture, and `scripts/bump-mise-snap.py` updates both from the shared `latest/stable` version.

- [ ] **Step 2: Validate edited inputs**

Run: `yq '.' sdkcraft.yaml >/dev/null && shellcheck hooks/setup-base`

Expected: both commands exit zero.
