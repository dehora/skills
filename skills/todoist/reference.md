# todoist-cli Command Reference

Full command reference for [todoist-cli](https://github.com/nichochar/todoist-cli) (`td`), the official Doist CLI for Todoist.

## Installation

```bash
fnm use default
npm install -g @doist/todoist-cli
```

## Authentication

### login
Authenticate with Todoist via OAuth (opens browser).
```bash
td auth login
```

### token
Save an API token directly (manual authentication).
```bash
td auth token
td auth token "{token}"
```

### status
Show current authentication status.
```bash
td auth status
```

### logout
Remove saved authentication token.
```bash
td auth logout
```

**Environment variable:** Set `TODOIST_API_TOKEN` to authenticate without storing a token in the config file.

## Quick Add

Add a task using Todoist's natural language parsing. Supports dates, priorities (`p1`–`p4`), projects (`#Project`), and labels (`@label`) inline.

```bash
td add "{text}"
td add "Buy milk tomorrow p1 #Shopping"
td add "Meeting with @team every Monday at 10am"
```

**Flags:**
- `--assignee <ref>` — Assign to a user (name, email, `id:xxx`, or `"me"`)

**Note for agents:** Use `td task add` with structured flags instead of `td add` for unambiguous task creation.

## Task Views

### today
Show tasks due today and overdue.
```bash
td today
td today --json
td today --show-urls
```

**Flags:**
- `--limit <n>` — Limit results (default: 300)
- `--cursor <cursor>` — Continue from cursor
- `--all` — Fetch all results
- `--any-assignee` — Show tasks assigned to anyone
- `--workspace <name>` — Filter to workspace
- `--personal` — Filter to personal projects
- `--json` — JSON output
- `--ndjson` — Newline-delimited JSON output
- `--full` — Include all fields in JSON
- `--raw` — Disable markdown rendering
- `--show-urls` — Show web app URLs

### upcoming
Show tasks due in the next N days (default: 7).
```bash
td upcoming
td upcoming 14
td upcoming --json
```

**Flags:** Same as `today`.

### inbox
List tasks in Inbox.
```bash
td inbox
td inbox --priority p1
td inbox --json
```

**Flags:**
- `--priority <p1-p4>` — Filter by priority
- `--due <date>` — Filter by due date
- `--limit <n>` — Limit results (default: 300)
- `--cursor <cursor>` — Continue from cursor
- `--all` — Fetch all results
- `--json` / `--ndjson` / `--full` / `--raw` / `--show-urls`

### completed
Show completed tasks.
```bash
td completed
td completed --since 2025-01-01 --until 2025-01-31
td completed --project "Work"
```

**Flags:**
- `--since <date>` — Start date (YYYY-MM-DD, default: today)
- `--until <date>` — End date (YYYY-MM-DD, default: tomorrow)
- `--project <name>` — Filter by project
- `--limit <n>` / `--cursor` / `--all` / `--json` / `--ndjson` / `--full` / `--show-urls`

## Task Operations

### task list
List tasks with filters.
```bash
td task list
td task list --project "Work"
td task list --label "urgent"
td task list --priority p1
td task list --due today
td task list --filter "overdue & #Work"
td task list --json
```

**Flags:**
- `--project <name>` — Filter by project name or `id:xxx`
- `--parent <ref>` — Filter subtasks of a parent
- `--label <name>` — Filter by label (comma-separated)
- `--priority <p1-p4>` — Filter by priority
- `--due <date>` — Filter by due date (`today`, `overdue`, or YYYY-MM-DD)
- `--filter <query>` — Raw Todoist filter query
- `--assignee <ref>` — Filter by assignee (`me` or `id:xxx`)
- `--unassigned` — Only unassigned tasks
- `--workspace <name>` — Filter to workspace
- `--personal` — Filter to personal projects
- `--limit <n>` / `--cursor` / `--all` / `--json` / `--ndjson` / `--full` / `--raw` / `--show-urls`

### task view
View task details.
```bash
td task view "{ref}"
td task view "Buy milk"
td task view "id:123456"
td task view --json
```

**Flags:**
- `--json` — JSON output
- `--full` — Include all fields
- `--raw` — Disable markdown rendering

### task add
Add a task with structured flags.
```bash
td task add "Write report"
td task add "Write report" --due "next friday" --priority p2
td task add "Deploy" --project "Work" --labels "ops,release" --description "v2.0 release"
td task add "Sub-item" --parent "Parent task"
```

**Flags:**
- `--due <date>` — Due date (natural language or YYYY-MM-DD)
- `--deadline <date>` — Deadline date (YYYY-MM-DD)
- `--priority <p1-p4>` — Priority level
- `--project <name>` — Project name or `id:xxx`
- `--section <ref>` — Section (name with `--project`, or `id:xxx`)
- `--labels <a,b>` — Comma-separated labels
- `--parent <ref>` — Parent task reference
- `--description <text>` — Task description
- `--assignee <ref>` — Assign to user
- `--duration <time>` — Duration (e.g., `30m`, `1h`, `2h15m`)

### task complete
Complete a task.
```bash
td task complete "{ref}"
td task complete "Buy milk"
td task complete "Weekly standup" --forever
```

**Flags:**
- `--forever` — Complete recurring task permanently (stops recurrence)

### task uncomplete
Reopen a completed task (requires `id:xxx`).
```bash
td task uncomplete "id:123456"
```

### task update
Update a task.
```bash
td task update "{ref}" --due "tomorrow"
td task update "{ref}" --priority p1
td task update "{ref}" --content "New task name"
```

### task move
Move a task to a different project, section, or parent.
```bash
td task move "{ref}" --project "Work"
td task move "{ref}" --section "In Progress" --project "Work"
td task move "{ref}" --parent "Parent task"
```

### task delete
Delete a task.
```bash
td task delete "{ref}"
```

### task browse
Open a task in the browser.
```bash
td task browse "{ref}"
```

## Project Operations

### project list
List all projects.
```bash
td project list
td project list --json
```

### project view
View project details and tasks.
```bash
td project view "Work"
td project view "Work" --json
```

### project create
Create a new project.
```bash
td project create --name "New Project"
```

### project delete
Delete a project (must have no uncompleted tasks).
```bash
td project delete "Old Project"
```

### project archive / unarchive
```bash
td project archive "Done Project"
td project unarchive "Done Project"
```

### project browse
Open project in browser.
```bash
td project browse "Work"
```

## Label Operations

### label list
List all labels.
```bash
td label list
td label list --json
```

### label create
```bash
td label create --name "urgent"
```

### label delete
```bash
td label delete "urgent"
```

### label view
View label details and associated tasks.
```bash
td label view "urgent"
```

## Comment Operations

### comment list
List comments on a task.
```bash
td comment list "{task-ref}"
td comment list --project "Work"
```

### comment add
Add a comment to a task.
```bash
td comment add "{task-ref}" --content "Updated the requirements"
td comment add --project "Work" --content "Sprint goal updated"
```

### comment delete / update / view
```bash
td comment delete "id:xxx"
td comment update "id:xxx" --content "Updated text"
td comment view "id:xxx"
```

## Global Flags

These flags are available on most commands:

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |
| `--ndjson` | Output as newline-delimited JSON |
| `--full` | Include all fields in JSON output |
| `--raw` | Disable markdown rendering |
| `--show-urls` | Show web app URLs for each task |
| `--no-spinner` | Disable loading animations |
| `--verbose` / `-v` | Increase output verbosity (up to `-vvvv`) |
| `--help` / `-h` | Show help for any command |
