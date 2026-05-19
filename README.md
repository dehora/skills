# Skills

A collection of general-purpose [Claude Code](https://claude.ai/code) skills—`.md` prompt files with optional scripting support.

## Structure

```
skills/
└── skills/             # User-invocable slash commands
    └── <skill-name>/
        ├── SKILL.md    # Entrypoint with YAML frontmatter
        ├── reference.md
        └── scripts/
```

## Available skills

- **notesmd**—Manage Obsidian vault notes via [notesmd-cli](https://github.com/yakitrak/notesmd-cli).
- **todoist**—Manage Todoist tasks via the official `@doist/todoist-cli`.
- **roborev**—Run an external reviewer (codex/claude CLI) against the current branch diff and surface findings inline.

## Installation

```bash
mkdir -p ~/.claude/skills
ln -s $(pwd)/skills/<skill-name> ~/.claude/skills/<skill-name>
```

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
uv run ruff check scripts/
uv run pytest
```

## Related

For werk-series tooling—project scaffolding, lesson scaffolds, layer checks, reviewer agents, pre-commit hooks, and cron/launchd schedule recipes for [`modelwerk`](https://github.com/dehora/modelwerk) / [`policywerk`](https://github.com/dehora/policywerk) / [`bayeswerk`](https://github.com/dehora/bayeswerk)—see [`dehora/werk-kit`](https://github.com/dehora/werk-kit).
