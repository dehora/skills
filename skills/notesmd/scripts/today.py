#!/usr/bin/env python3
"""List notes created or modified since midnight today in the default Obsidian vault."""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

EXCLUDE_DIRS = {".obsidian", ".trash"}


def get_vault_path() -> Path:
    result = subprocess.run(
        ["notesmd-cli", "print-default", "--path-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def find_today_notes(vault: Path) -> list[tuple[Path, float]]:
    midnight = datetime.now().replace(hour=0, minute=1, second=0, microsecond=0).timestamp()
    notes = []
    for md in vault.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in md.relative_to(vault).parts):
            continue
        mtime = md.stat().st_mtime
        if mtime >= midnight:
            notes.append((md, mtime))
    notes.sort(key=lambda x: x[1], reverse=True)
    return notes


def main() -> None:
    vault = get_vault_path()
    notes = find_today_notes(vault)

    if not notes:
        print("No notes modified today.")
        return

    for path, mtime in notes:
        rel = path.relative_to(vault).with_suffix("")
        modified = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone()
        print(f"{modified:%H:%M}  {rel}")


if __name__ == "__main__":
    main()
