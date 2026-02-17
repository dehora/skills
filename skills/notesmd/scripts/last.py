#!/usr/bin/env python3
"""List the most recently modified notes in the default Obsidian vault."""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE_DIRS = {".obsidian", ".trash"}
DEFAULT_COUNT = 10


def get_vault_path() -> Path:
    result = subprocess.run(
        ["notesmd-cli", "print-default", "--path-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def find_recent_notes(vault: Path, count: int) -> list[tuple[Path, float]]:
    notes = []
    for md in vault.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in md.relative_to(vault).parts):
            continue
        notes.append((md, md.stat().st_mtime))
    notes.sort(key=lambda x: x[1], reverse=True)
    return notes[:count]


def main() -> None:
    count = DEFAULT_COUNT
    if len(sys.argv) > 1:
        count = int(sys.argv[1])

    vault = get_vault_path()
    notes = find_recent_notes(vault, count)

    for path, mtime in notes:
        rel = path.relative_to(vault).with_suffix("")
        modified = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone()
        print(f"{modified:%Y-%m-%d %H:%M}  {rel}")


if __name__ == "__main__":
    main()
