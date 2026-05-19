---
name: new-skill
description: Use when the user invokes /new-skill to scaffold a fresh SKILL.md, reference.md, and scripts/ directory under skills/<name>/. Checks for naming collisions against the available-skills list before writing.
user-invocable: true
argument-hint: <name> --description "<one-line description>" [--repo <path>] [--allowed-tools "Tool1, Tool2"] [--no-reference] [--scripts]
allowed-tools: Bash, Read, Write
---

## What this skill does

Creates a new skill directory with the canonical layout used across `dehora/skills` and `dehora/werk-kit`:

```
skills/<name>/
├── SKILL.md           # YAML frontmatter + body stub
├── reference.md       # optional supporting docs (--no-reference to skip)
└── scripts/           # optional helper scripts dir (--scripts to include)
```

Before writing, it runs the two reflexes I keep skipping by hand: collision check against the built-in and user-invocable skills, and a stage-only-the-files-I-create discipline.

## Arguments

- **`<name>`** (required, positional). Must match `^[a-z][a-z0-9-]*$`. Refused if the name already exists as a skill (in any source repo) or collides with a built-in (`init`, `review`, `security-review`, `simplify`, `loop`, `schedule`, `claude-api`, `update-config`, `keybindings-help`, `fewer-permission-prompts`, plus anything currently visible in the harness's available-skills list).
- **`--description "<one-line description>"`** (required). Goes verbatim into the frontmatter `description:` field. Should start with "Use when the user invokes /<name> to ..." per the convention in `dehora/skills/CLAUDE.md`.
- **`--repo <path>`** (optional). Target repo root. Defaults to `/Users/bill/projects/dehora/skills`. Pass `/Users/bill/projects/dehora/werk-kit` for werk-specific skills.
- **`--allowed-tools "Tool1, Tool2"`** (optional). Frontmatter `allowed-tools` value. Defaults to `Bash, Read`.
- **`--no-reference`** (optional). Skip creating `reference.md`.
- **`--scripts`** (optional). Create an empty `scripts/.gitkeep` to anchor the scripts dir.

If `<name>` or `--description` is missing, print:

```
Usage: /new-skill <name> --description "<one-line description>" [--repo <path>] [--allowed-tools "..."] [--no-reference] [--scripts]

Example:
  /new-skill papers --description "Use when the user invokes /papers to fetch an arxiv or openreview paper into the Obsidian vault." --allowed-tools "Bash, Read, WebFetch"
```

and stop.

## Preflight

1. **Collision check.** Refuse if `<name>` is in the built-in list (above) OR if `<repo>/skills/<name>/` already exists OR if any other configured source (default sources: `dehora/skills`, `dehora/werk-kit`) already has a `skills/<name>/SKILL.md`. Print all collisions found.
2. **Repo exists.** Verify `<repo>/skills/` exists. Refuse otherwise.

## Write

Create:

- `<repo>/skills/<name>/SKILL.md` with the canonical frontmatter:
  ```yaml
  ---
  name: <name>
  description: <description>
  user-invocable: true
  argument-hint: "TODO: usage hint"
  allowed-tools: <allowed-tools>
  ---

  ## What this skill does

  TODO: one paragraph on what this skill does and why it exists.

  ## Arguments

  TODO: list and describe each argument; what happens when none are supplied.

  ## Preflight

  TODO: invariants to check before doing real work.

  ## Run

  TODO: the steps the skill takes.

  ## Notes

  TODO: edge cases, non-goals.
  ```
- `<repo>/skills/<name>/reference.md` unless `--no-reference` was passed:
  ```markdown
  # <name> reference

  TODO: supporting docs that are too long for SKILL.md (config locations, edge-case command-line examples, troubleshooting).
  ```
- `<repo>/skills/<name>/scripts/.gitkeep` if `--scripts` was passed.

Never overwrites. Refuses if any target file exists.

## Finish

Print:

```
Created <repo>/skills/<name>/{SKILL.md[, reference.md][, scripts/]}

Next:
  1. Edit SKILL.md — fill in argument-hint, body sections.
  2. /sync-skills --fix    # link into ~/.claude/skills/
  3. Verify the new skill appears in the harness's available-skills list on the next session start.
```

## Notes

- Don't write tests as part of scaffolding — the surrounding skills pattern (notesmd, todoist, roborev) doesn't ship tests, and a `.gitkeep` in `tests/` would lie about coverage. Add tests deliberately when the skill grows enough to need them.
- The collision check list is hand-maintained. If a new built-in skill ships in Claude Code, add it. The cost of a missed collision is a silent shadow at the slash-command layer—worth the small list-maintenance overhead.
