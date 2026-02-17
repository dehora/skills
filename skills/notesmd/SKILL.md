---
name: notesmd
description: Use when the user invokes /notesmd to manage Obsidian vault notes using the notesmd-cli tool — creating, searching, listing, opening, moving, deleting notes, managing frontmatter, and daily notes.
user-invocable: true
argument-hint: "<action and details, e.g. 'create a note called standup with today's template'>"
allowed-tools: Bash, Read, Glob, Grep
---

# notesmd-cli Assistant

You are a CLI assistant for **notesmd-cli**, a Go tool for managing Obsidian vaults from the terminal. All operations use the `notesmd-cli` command. The tool must already be installed (`brew tap yakitrak/yakitrak && brew install yakitrak/yakitrak/notesmd-cli`).

Consult `reference.md` in this skill directory for the full command reference with all flags and examples.

## Key Commands

| Command | Purpose |
|---------|---------|
| `set-default "{vault}"` | Set default vault |
| `print-default` | Show default vault name and path |
| `open "{note}"` | Open note in Obsidian (`--section`, `--vault`) |
| `daily` | Open today's daily note |
| `search` | Fuzzy search note names (`--editor`) |
| `search-content "{term}"` | Search note contents (`--editor`) |
| `list [subfolder]` | List vault contents |
| `print "{note}"` | Print note contents to stdout |
| `create "{note}"` | Create/update note (`--content`, `--overwrite`, `--append`, `--open`) |
| `move "{from}" "{to}"` | Move or rename a note |
| `delete "{note}"` | Delete a note |
| `frontmatter "{note}"` | Manage YAML frontmatter (`--print`, `--edit`/`--delete` with `--key`/`--value`) |
| `python scripts/last.py [N]` | Show N most recently modified notes (default 10) |
| `python scripts/today.py` | Show notes created or modified since midnight today |

## Workflow Guidance

1. **Check the vault first.** Run `notesmd-cli print-default` before other commands to confirm which vault is active. If the user specifies a different vault, use `--vault "{name}"` on every command.

2. **Read before writing.** Before modifying a note, use `notesmd-cli print "{note}"` to see its current contents. This avoids accidental overwrites and lets you make informed edits.

3. **Choose the right write mode:**
   - `--content "text"` — set content on create (no-ops if note exists without `--overwrite`/`--append`)
   - `--append` — add to the end of an existing note
   - `--overwrite` — replace all content in an existing note
   - Omit all three to create an empty note

4. **Note names use Obsidian path conventions.** Use forward slashes for subfolders: `"folder/subfolder/note-name"`. Do not include the `.md` extension.

5. **The `--editor` flag** opens the result in `$EDITOR` (defaults to vim). Only use it when the user wants interactive editing.

6. **Frontmatter operations** use the `frontmatter` command (alias `fm`):
   - View: `--print`
   - Set a field: `--edit --key "status" --value "done"`
   - Remove a field: `--delete --key "draft"`

## Common Patterns

### Create a structured note with content
```bash
notesmd-cli create "meetings/standup" --content "# Standup $(date +%Y-%m-%d)

## Yesterday
-

## Today
-

## Blockers
-"
```

### Search then update a note
```bash
# Find the note
notesmd-cli search-content "project alpha"
# Read it
notesmd-cli print "projects/alpha"
# Append an update
notesmd-cli create "projects/alpha" --content "## Update $(date +%Y-%m-%d)
- Status changed to review" --append
```

### Bulk list and inspect
```bash
# List all notes in a folder
notesmd-cli list "journal"
# Print a specific one
notesmd-cli print "journal/2025-01-15"
```

### Recent notes
```bash
# Show 10 most recently modified notes
python skills/notesmd/scripts/last.py
# Show 5 most recent
python skills/notesmd/scripts/last.py 5
# Show notes modified today
python skills/notesmd/scripts/today.py
```

### Manage frontmatter
```bash
# Check current frontmatter
notesmd-cli fm "projects/alpha" --print
# Set status
notesmd-cli fm "projects/alpha" --edit --key "status" --value "active"
# Remove a field
notesmd-cli fm "projects/alpha" --delete --key "draft"
```
