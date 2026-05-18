"""Run a werk lesson, capture stdout/stderr, and collect generated plots.

Usage:
    uv run python <path>/run_lesson.py lessons/NN_slug.py

Prints a JSON manifest to stdout:
    {"stdout_path": "...", "plots": ["..."], "exit_code": N, "stderr_tail": "..."}

The lesson runs with cwd at the project root (the parent of `lessons/`). Any
PNG or SVG produced during the run in the project root, `output/`, or
`examples/` is moved into `examples/img/NN_slug/`. Pre-existing files
(detected via mtime taken before the run) are left alone.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


PLOT_EXTS = (".png", ".svg", ".jpg", ".jpeg", ".gif")
SCAN_DIRS = (".", "output", "examples")


def find_project_root(lesson_path: Path) -> Path:
    """Walk up from the lesson file until we find a pyproject.toml."""
    p = lesson_path.resolve().parent
    while p != p.parent:
        if (p / "pyproject.toml").exists():
            return p
        p = p.parent
    raise SystemExit(f"No pyproject.toml found above {lesson_path}")


def snapshot_plots(root: Path) -> dict[Path, float]:
    """Return mtimes of all plot files under root's SCAN_DIRS, recursively."""
    snap: dict[Path, float] = {}
    for d in SCAN_DIRS:
        base = root / d
        if not base.exists():
            continue
        for ext in PLOT_EXTS:
            for f in base.rglob(f"*{ext}"):
                # Skip files already in examples/img/<lesson>/ — those are committed.
                rel = f.relative_to(root)
                if rel.parts[:2] == ("examples", "img"):
                    continue
                try:
                    snap[f] = f.stat().st_mtime
                except OSError:
                    pass
    return snap


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: run_lesson.py <lessons/NN_slug.py>", file=sys.stderr)
        return 2

    lesson = Path(argv[1])
    if not lesson.exists():
        print(f"Lesson not found: {lesson}", file=sys.stderr)
        return 2

    root = find_project_root(lesson)
    rel_lesson = lesson.resolve().relative_to(root)
    stem = lesson.stem  # NN_slug

    transcript_dir = root / ".lesson-transcript"
    transcript_dir.mkdir(exist_ok=True)
    stdout_path = transcript_dir / f"{stem}.stdout"

    img_dir = root / "examples" / "img" / stem
    img_dir.mkdir(parents=True, exist_ok=True)

    before = snapshot_plots(root)
    before_time = time.time()

    # Run the lesson via uv. We capture combined stdout+stderr so output order is preserved.
    proc = subprocess.run(
        ["uv", "run", "python", str(rel_lesson)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    stdout_path.write_text(proc.stdout)
    stderr_tail = "\n".join(proc.stderr.splitlines()[-20:])

    after = snapshot_plots(root)
    captured: list[str] = []
    for path, mtime in after.items():
        prior = before.get(path)
        is_new = prior is None or mtime > prior or mtime >= before_time - 1e-3
        if not is_new:
            continue
        dest = img_dir / path.name
        # Avoid clobbering: if same destination already exists from earlier in this run, leave.
        if dest.resolve() == path.resolve():
            continue
        try:
            shutil.move(str(path), str(dest))
            captured.append(str(dest.relative_to(root)))
        except OSError as e:
            print(f"warn: could not move {path} -> {dest}: {e}", file=sys.stderr)

    captured.sort()

    manifest = {
        "stdout_path": str(stdout_path.relative_to(root)),
        "plots": captured,
        "exit_code": proc.returncode,
        "stderr_tail": stderr_tail,
    }
    print(json.dumps(manifest, indent=2))
    return 0 if proc.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
