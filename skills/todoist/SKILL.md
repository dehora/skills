---
name: todoist
description: Use when the user invokes /todoist to manage Todoist tasks — adding tasks, reviewing today's agenda, listing by project, completing tasks, and managing projects and labels.
user-invocable: true
argument-hint: "<action and details, e.g. 'add Buy milk tomorrow p1 #Shopping'>"
allowed-tools: Bash
---

# todoist-cli Assistant

You are a CLI assistant for **todoist-cli** (`td`), the official Doist CLI for managing Todoist. All operations use the `td` command. The tool must already be installed (`fnm use default && npm install -g @doist/todoist-cli`).

Consult `reference.md` in this skill directory for the full command reference with all flags and examples.

## Key Commands

| Command | Purpose |
|---------|---------|
| `td auth status` | Check authentication status |
| `td add "{text}"` | Quick-add task with natural language |
| `td task add "{content}"` | Add task with structured flags (`--due`, `--priority`, `--project`) |
| `td today` | Show tasks due today and overdue |
| `td upcoming [days]` | Show tasks due in the next N days (default 7) |
| `td inbox` | List tasks in Inbox |
| `td completed` | Show completed tasks |
| `td task list` | List tasks with filters (`--project`, `--label`, `--priority`) |
| `td task view "{ref}"` | View task details |
| `td task complete "{ref}"` | Complete a task |
| `td project list` | List all projects |
| `td label list` | List all labels |

## Workflow Guidance

1. **Check auth first.** Run `td auth status` before other commands to confirm authentication is active. If not authenticated, prompt the user to run `td auth login`.

2. **Use `td add` for quick natural language input.** It supports Todoist's natural language parsing: dates, priorities (`p1`–`p4`), projects (`#Project`), and labels (`@label`) inline.

3. **Use `td task add` for structured input.** When you need explicit control over fields, use `td task add` with flags like `--due`, `--priority`, `--project`, `--labels`, `--description`.

4. **Use `--json` for programmatic output.** When chaining commands or parsing results, add `--json` for machine-readable output. Add `--full` to include all fields.

5. **Task references** can be a task name, a task URL, or `id:xxx`. When ambiguous, use `td task list` to find the exact task first.

6. **Filter by project** to narrow results: `td task list --project "Work"` or `td today --workspace "Work"`.

## Common Patterns

### Quick-add tasks
```bash
# Natural language with date, priority, project
td add "Buy milk tomorrow p1 #Shopping"
# Simple task
td add "Review PR"
```

### Structured task creation
```bash
# Task with explicit flags
td task add "Write quarterly report" --due "next friday" --priority p2 --project "Work" --labels "writing"
# Task with description
td task add "Deploy v2.0" --due "2025-03-01" --description "Release includes auth refactor and new dashboard"
```

### Review today's tasks
```bash
# See what's due today
td today
# Show URLs for opening in browser
td today --show-urls
```

### List and filter tasks
```bash
# All tasks in a project
td task list --project "Work"
# High priority tasks
td task list --priority p1
# Tasks with a specific label
td task list --label "urgent"
# Raw Todoist filter query
td task list --filter "overdue & #Work"
```

### Complete tasks
```bash
# Complete by name or reference
td task complete "Buy milk"
# Stop a recurring task permanently
td task complete "Weekly standup" --forever
```

### Browse projects
```bash
# List all projects
td project list
# View a project's tasks
td project view "Work"
```
