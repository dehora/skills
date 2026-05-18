---
name: werk-init
description: Use when the user invokes /werk-init to scaffold a new werk-series project (src layout, CLAUDE.md, pyproject, lessons/, examples/, tests/, .claude/settings.local.json) following the modelwerk/policywerk convention.
user-invocable: true
argument-hint: <project-name> [--pkg <python-package-name>] [--tagline "<one-line description>"]
allowed-tools: Bash, Read, Write, Edit, Glob
---

## What this skill does

Scaffolds a new werk-series project in the current working directory. Werk projects are educational, lesson-driven codebases that share a strict shape: standard-library only code, compositional L0→L7 layering, and a runnable `lessons/NN_name.py` paired with an annotated `examples/NN_name.md`.

## Arguments

Parse `$ARGUMENTS`:

- **`<project-name>`** (required, positional) — directory + project name. Must be lowercase letters/digits/hyphens, end in `werk` by convention but not enforced.
- **`--pkg <python-package-name>`** (optional) — the Python package name under `src/`. Must be a valid Python identifier (lowercase, underscores allowed). Defaults to `project-name` with hyphens converted to underscores.
- **`--tagline "<one-line description>"`** (optional) — tagline for the CLAUDE.md and pyproject description. Defaults to a placeholder the user fills in later.

If `$ARGUMENTS` is empty, print:
```
Usage: /werk-init <project-name> [--pkg <python-package-name>] [--tagline "<one-line description>"]

Example: /werk-init bayeswerk --pkg bayeswerk --tagline "Bayesian inference from scratch — Bayes' rule to VAEs"
```
and stop.

## Preflight

1. Confirm the current working directory is empty (allow only `.git`, `.venv`, `README.md`, `CLAUDE.md`, dotfiles). If not empty, list the offending entries and stop.
2. Confirm `uv` is on PATH (`uv --version`).

## Scaffold

Create the following layout under the current directory (read templates from `templates/` next to this SKILL.md and substitute `{{project_name}}`, `{{pkg}}`, `{{tagline}}`):

```
./
├── CLAUDE.md                       # from templates/CLAUDE.md
├── README.md                       # from templates/README.md (short)
├── pyproject.toml                  # from templates/pyproject.toml
├── .gitignore                      # from templates/gitignore
├── .python-version                 # contains "3.12"
├── .claude/
│   └── settings.local.json         # from templates/settings.local.json
├── src/
│   └── {{pkg}}/
│       ├── __init__.py             # empty
│       ├── primitives/__init__.py
│       ├── building_blocks/__init__.py
│       ├── models/__init__.py
│       ├── data/__init__.py
│       └── viz/__init__.py
├── lessons/
│   └── .gitkeep
├── examples/
│   ├── .gitkeep
│   └── img/
│       └── .gitkeep
├── tests/
│   ├── __init__.py
│   └── .gitkeep
├── data/.gitkeep
└── output/.gitkeep
```

Use `Write` for each file. Do NOT run `uv sync` or `git init`.

## Finish

Print a final message:

```
Scaffolded {{project_name}} (package {{pkg}}).

Next steps:
  uv sync
  git init && git add . && git commit -m "Adds {{project_name}} project scaffolding"
  /new-lesson 01 first_lesson --title "Your first lesson"

Edit CLAUDE.md to tighten the layer breakdown for this project (e.g. policywerk uses L0–L3 with world/ and actors/ instead of models/).
```

## Notes

- Templates are based on modelwerk. The `models/` directory is a generic name — werk projects sometimes use `actors/` (policywerk) or domain-specific names. The user can `git mv` after init.
- `.claude/settings.local.json` ships with a small, safe permission set. The user will grow it organically.
- The `models/` placeholder dir is created so the L0→L2 import discipline is trivially testable by `/check-layering` from day one.
