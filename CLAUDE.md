# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A collection of Claude Code skills (`.md` prompt files) with Python scripting support. Skills follow the Anthropic Claude Code skill format and are designed to be installed into `~/.claude/skills/` or a project's `.claude/skills/` directory.

## Skill Format

Each skill is a directory under `skills/` containing a `SKILL.md` entrypoint:

```
skills/<skill-name>/
├── SKILL.md           # Required — main instructions with YAML frontmatter
├── reference.md       # Optional — supporting docs
├── examples/          # Optional — example outputs
└── scripts/           # Optional — executables
```

### SKILL.md Frontmatter

```yaml
---
name: skill-name                     # Lowercase, hyphens, max 64 chars
description: What this skill does    # Claude uses this to decide when to invoke
allowed-tools: Read, Grep, Bash      # Tools available without permission prompt
---
```

Optional frontmatter fields: `disable-model-invocation`, `user-invocable`, `model`, `context`, `agent`, `argument-hint`.

## Commands

```bash
# Python setup
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Lint (line-length 100 per pyproject.toml)
ruff check scripts/

# Tests
pytest
pytest tests/test_foo.py::test_bar   # single test

# Install a skill locally (symlink into personal skills)
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

## Structure

- `skills/` — Skill directories, each with a `SKILL.md` entrypoint
- `scripts/` — Python helper scripts used by skills or for skill management
