# Skills

A collection of [Claude Code](https://claude.ai/code) skills and agent personas — `.md` prompt files with optional scripting support.

## Structure

```
skills/
├── skills/             # User-invocable slash commands
│   └── <skill-name>/
│       ├── SKILL.md    # Entrypoint with YAML frontmatter
│       ├── reference.md
│       └── scripts/
└── agents/             # Persona files loaded by ~/.claude/commands/agent.md
    └── <name>.md
```

## Available skills

- **notesmd** — Manage Obsidian vault notes via [notesmd-cli](https://github.com/yakitrak/notesmd-cli).
- **todoist** — Manage Todoist tasks via the official `@doist/todoist-cli`.
- **werk-init** — Scaffold a new werk-series project (modelwerk/policywerk/bayeswerk shape).
- **new-lesson** — Create a matched `lessons/NN_*.py` + `examples/NN_*.md` pair.
- **lesson-transcript** — Run a lesson, capture stdout and plots, refresh the annotated transcript.
- **check-layering** — Verify L0–L7 import discipline in a werk `src/` tree.
- **roborev** — Run an external reviewer (codex/claude CLI) against the current branch diff and surface findings inline.

## Available agents

- **staff-engineer** — Senior code reviewer for werk lessons (layering, scope, tests, numerics, narrative drift).

(`carol` — security auditor — lives directly in `~/.claude/agents/carol.md` for now.)

## Installation

Skills:

```bash
mkdir -p ~/.claude/skills
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

Agents (loaded by the `/agent --name=<name> <task>` command at `~/.claude/commands/agent.md`):

```bash
mkdir -p ~/.claude/agents
ln -s $(pwd)/agents/<name>.md ~/.claude/agents/<name>.md
```

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uv run ruff check scripts/
uv run pytest
```
