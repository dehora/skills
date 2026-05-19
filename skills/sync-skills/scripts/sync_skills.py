"""Reconcile ~/.claude/skills and ~/.claude/agents symlinks against source repos.

Usage:
    sync_skills.py [--fix] [--source PATH]...

Defaults to scanning /Users/bill/projects/dehora/skills and /Users/bill/projects/dehora/werk-kit
as sources. Reports four classes for each link slot:

    OK       — symlink exists and points into a configured source
    missing  — source has the artifact but no symlink in ~/.claude/
    broken   — symlink exists but its target is gone
    extra    — symlink exists, target is fine, but doesn't live under any configured source

With --fix: creates missing links, removes broken links, never touches extras.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CLAUDE_SKILLS = Path.home() / ".claude" / "skills"
CLAUDE_AGENTS = Path.home() / ".claude" / "agents"

DEFAULT_SOURCES = [
    Path("/Users/bill/projects/dehora/skills"),
    Path("/Users/bill/projects/dehora/werk-kit"),
]


def inventory_sources(sources: list[Path]) -> tuple[dict[str, Path], dict[str, Path]]:
    """Return ({skill_name: source_dir}, {agent_name: source_file}) from each source."""
    skills: dict[str, Path] = {}
    agents: dict[str, Path] = {}
    for src in sources:
        skill_root = src / "skills"
        if skill_root.is_dir():
            for entry in sorted(skill_root.iterdir()):
                if not entry.is_dir():
                    continue
                if not (entry / "SKILL.md").is_file():
                    continue
                if entry.name in skills:
                    print(
                        f"warn: skill '{entry.name}' defined in both "
                        f"{skills[entry.name].parent.parent} and {src} — using first",
                        file=sys.stderr,
                    )
                    continue
                skills[entry.name] = entry
        agent_root = src / "agents"
        if agent_root.is_dir():
            for entry in sorted(agent_root.iterdir()):
                if entry.suffix != ".md" or not entry.is_file():
                    continue
                name = entry.stem
                if name in agents:
                    print(
                        f"warn: agent '{name}' defined in both "
                        f"{agents[name].parent.parent} and {src} — using first",
                        file=sys.stderr,
                    )
                    continue
                agents[name] = entry
    return skills, agents


def is_under(path: Path, roots: list[Path]) -> bool:
    rp = path.resolve(strict=False)
    return any(rp.is_relative_to(r.resolve(strict=False)) for r in roots)


def classify_links(
    link_root: Path,
    canonical: dict[str, Path],
    sources: list[Path],
    suffix: str = "",
) -> tuple[list[str], list[tuple[str, Path]], list[str], list[tuple[str, Path]]]:
    """Return (ok, missing, broken, extra). Each item carries the link name (with suffix)
    and, where applicable, the target Path."""
    ok: list[str] = []
    missing: list[tuple[str, Path]] = []
    broken: list[str] = []
    extra: list[tuple[str, Path]] = []

    link_root.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Path] = {}
    for entry in os.scandir(link_root):
        if not entry.is_symlink():
            continue
        existing[entry.name] = Path(os.readlink(entry.path))

    canonical_link_names = {name + suffix: name for name in canonical}

    for link_name, real_name in canonical_link_names.items():
        target = canonical[real_name]
        if link_name not in existing:
            missing.append((link_name, target))
            continue
        link_target = existing[link_name]
        if not link_target.is_absolute():
            link_target = (link_root / link_target).resolve(strict=False)
        if not link_target.exists():
            broken.append(link_name)
            continue
        if link_target.resolve() == target.resolve():
            ok.append(link_name)
        else:
            extra.append((link_name, link_target))

    for link_name, link_target in existing.items():
        if link_name in canonical_link_names:
            continue
        abs_target = link_target if link_target.is_absolute() else (link_root / link_target).resolve(strict=False)
        if not abs_target.exists():
            broken.append(link_name)
        elif is_under(abs_target, sources):
            # under sources but no canonical claim (maybe renamed in source); flag as extra
            extra.append((link_name, link_target))
        else:
            extra.append((link_name, link_target))

    return sorted(set(ok)), sorted(missing), sorted(set(broken)), sorted(set(extra))


def apply_fixes(
    link_root: Path,
    missing: list[tuple[str, Path]],
    broken: list[str],
) -> list[str]:
    actions: list[str] = []
    for link_name, target in missing:
        link_path = link_root / link_name
        link_path.symlink_to(target)
        actions.append(f"+link  {link_path}  -> {target}")
    for link_name in broken:
        link_path = link_root / link_name
        try:
            link_path.unlink()
            actions.append(f"-link  {link_path}  (broken)")
        except FileNotFoundError:
            pass
    return actions


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--source", action="append", default=None)
    args = ap.parse_args(argv)

    sources = [Path(s) for s in args.source] if args.source else DEFAULT_SOURCES
    for s in sources:
        if not s.exists():
            print(f"warn: source not found, skipping: {s}", file=sys.stderr)
    sources = [s for s in sources if s.exists()]

    if not sources:
        print("no usable sources; nothing to do.", file=sys.stderr)
        return 2

    skill_canon, agent_canon = inventory_sources(sources)

    skill_ok, skill_missing, skill_broken, skill_extra = classify_links(
        CLAUDE_SKILLS, skill_canon, sources
    )
    agent_ok, agent_missing, agent_broken, agent_extra = classify_links(
        CLAUDE_AGENTS, agent_canon, sources, suffix=".md"
    )

    total_ok = len(skill_ok) + len(agent_ok)
    total_missing = len(skill_missing) + len(agent_missing)
    total_broken = len(skill_broken) + len(agent_broken)
    total_extra = len(skill_extra) + len(agent_extra)

    actions: list[str] = []
    if args.fix and not args.dry_run:
        actions += apply_fixes(CLAUDE_SKILLS, skill_missing, skill_broken)
        actions += apply_fixes(CLAUDE_AGENTS, agent_missing, agent_broken)

    suffix_msg = " — fixed." if actions else (" (no changes)." if total_missing + total_broken == 0 else " (no changes; pass --fix to apply).")
    print(
        f"sync-skills: {total_ok} OK, {total_missing} missing, {total_broken} broken"
        + (f", {total_extra} extra" if total_extra else "")
        + suffix_msg
    )

    for link_name, target in skill_missing:
        print(f"  missing  ~/.claude/skills/{link_name}            (would link to {target})")
    for link_name, target in agent_missing:
        print(f"  missing  ~/.claude/agents/{link_name}            (would link to {target})")
    for link_name in skill_broken:
        print(f"  broken   ~/.claude/skills/{link_name}")
    for link_name in agent_broken:
        print(f"  broken   ~/.claude/agents/{link_name}")
    for link_name, target in skill_extra:
        print(f"  extra    ~/.claude/skills/{link_name}  -> {target}")
    for link_name, target in agent_extra:
        print(f"  extra    ~/.claude/agents/{link_name}  -> {target}")
    for action in actions:
        print(f"  {action}")

    in_sync_after = (total_missing + total_broken) == 0 or bool(actions)
    return 0 if in_sync_after else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
