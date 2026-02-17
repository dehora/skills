# Skills

A collection of [Claude Code](https://claude.ai/code) skills — `.md` prompt files with optional scripting support.

## Structure

```
skills/<skill-name>/
├── SKILL.md           # Entrypoint with YAML frontmatter
├── reference.md       # Supporting docs
└── scripts/           # Helper scripts
```

## Available Skills

- **notesmd** — Manage Obsidian vault notes from Claude Code using [notesmd-cli](https://github.com/yakitrak/notesmd-cli)

## Installation

Symlink a skill into your personal skills directory:

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
