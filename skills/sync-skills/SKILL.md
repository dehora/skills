---
name: sync-skills
description: Use when the user invokes /sync-skills to reconcile ~/.claude/skills and ~/.claude/agents symlinks against the source repos (dehora/skills, dehora/werk-kit). Reports broken, missing, and extra links; offers to fix.
user-invocable: true
argument-hint: [--fix] [--dry-run] [--source <repo-path>...]
allowed-tools: Bash, Read
---

## What this skill does

Symlinks under `~/.claude/skills/` and `~/.claude/agents/` drift quickly when skills are added, renamed, or moved between repos. This skill walks the canonical source repos, walks the current symlinks, and surfaces three classes of issue:

- **missing** — a skill or agent exists in a source repo but isn't symlinked
- **broken** — the symlink exists but its target doesn't
- **extra** — a symlink in `~/.claude/` points at a path that isn't claimed by any configured source

By default it only reports. With `--fix`, it creates missing links, deletes broken links, and leaves extra links alone (extras are flagged for review since they might be intentional one-offs).

## Arguments

- `--fix` — apply the proposed changes after reporting them.
- `--dry-run` — print what `--fix` would do without changing anything (default behavior when `--fix` is absent; explicit `--dry-run` makes intent obvious in shared environments).
- `--source <repo-path>` (repeatable) — override the default source list. Defaults to `/Users/bill/projects/dehora/skills` and `/Users/bill/projects/dehora/werk-kit`. Each source is expected to contain `skills/<name>/SKILL.md` and/or `agents/<name>.md`.

## Run

Invoke the helper script:

```bash
uv run python <this-skill>/scripts/sync_skills.py [--fix] [--source ...]
```

The script:

1. Builds the canonical inventory by scanning each source for `skills/<dir>/SKILL.md` and `agents/<name>.md` files.
2. Reads `~/.claude/skills/*` and `~/.claude/agents/*` (`os.scandir`, follow symlinks=False to inspect link targets).
3. Classifies every entry: matched, missing, broken, extra (where `extra` means a symlink whose target doesn't point inside any configured source root).
4. If `--fix` is set, creates symlinks for missing entries and removes broken ones. Always leaves extras alone.
5. Prints a summary table grouped by class.

## Output shape

Always prints something. Examples:

```
sync-skills: 7 OK, 0 missing, 0 broken, 1 extra (no changes).
  extra  ~/.claude/skills/td -> ~/.claude/skills/todoist   (intentional alias? leaving alone)
```

```
sync-skills: 6 OK, 1 missing, 1 broken (no changes; pass --fix to apply).
  missing  ~/.claude/skills/ship           (would link to /Users/bill/projects/dehora/skills/skills/ship)
  broken   ~/.claude/agents/staff-engineer.md  (target gone: /old/path/staff-engineer.md)
```

```
sync-skills: 8 OK, 1 missing, 1 broken — fixed.
  +link  ~/.claude/skills/ship                -> /Users/bill/projects/dehora/skills/skills/ship
  -link  ~/.claude/agents/staff-engineer.md   (broken)
```

Exit codes: 0 when everything is in sync after the run, 1 otherwise.

## Notes

- The default sources cover the two dehora repos. If you add a third source of skills/agents, pass `--source <path>` (and consider adding it to the default list in this skill's body when it becomes permanent).
- "Extra" symlinks are never auto-removed because aliases (`td -> todoist`) and personal one-offs (`carol.md` lives directly in `~/.claude/agents/`, not in a repo) are legitimate. The report names them so the user can decide.
- The script never touches anything outside `~/.claude/skills/` and `~/.claude/agents/`. It does not write to source repos.
