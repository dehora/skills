# notesmd-cli Command Reference

Full command reference for [notesmd-cli](https://github.com/Yakitrak/notesmd-cli).

## Installation

**Mac / Linux** (Homebrew):
```bash
brew tap yakitrak/yakitrak
brew install yakitrak/yakitrak/notesmd-cli
```

**Windows** (Scoop):
```
scoop bucket add scoop-yakitrak https://github.com/yakitrak/scoop-yakitrak.git
scoop install notesmd-cli
```

## Config Files

notesmd-cli stores its config in macOS Application Support (not dotfiles in `~`):

- **CLI preferences:** `~/Library/Application Support/notesmd-cli/preferences.json` — stores the default vault name
- **Obsidian vaults:** `~/Library/Application Support/obsidian/obsidian.json` — read by notesmd-cli to resolve vault paths

Note: These paths are not suitable for dotfile managers like chezmoi that target `~`.

## Vault Management

### set-default
Set the default vault for all commands.
```bash
notesmd-cli set-default "{vault-name}"
```

### print-default
Print the default vault name and path.
```bash
notesmd-cli print-default
notesmd-cli print-default --path-only
```

**Flags:**
- `--path-only` — Print only the vault path

## Note Operations

### open
Open a note in Obsidian.
```bash
notesmd-cli open "{note-name}"
notesmd-cli open "{note-name}" --vault "{vault-name}"
notesmd-cli open "{note-name}" --section "{heading-text}"
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault
- `--section "{heading}"` — Jump to a heading within the note

### daily
Open today's daily note in Obsidian.
```bash
notesmd-cli daily
notesmd-cli daily --vault "{vault-name}"
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault

### search
Fuzzy search for notes by name (interactive).
```bash
notesmd-cli search
notesmd-cli search --vault "{vault-name}"
notesmd-cli search --editor
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault
- `--editor` / `-e` — Open selected note in `$EDITOR` instead of Obsidian

### search-content
Search note contents for a term.
```bash
notesmd-cli search-content "{search-term}"
notesmd-cli search-content "{search-term}" --vault "{vault-name}"
notesmd-cli search-content "{search-term}" --editor
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault
- `--editor` / `-e` — Open selected note in `$EDITOR`

### list
List notes in the vault or a subfolder.
```bash
notesmd-cli list
notesmd-cli list "{subfolder}"
notesmd-cli list "{subfolder}" --vault "{vault-name}"
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault

### print
Print a note's contents to stdout.
```bash
notesmd-cli print "{note-name}"
notesmd-cli print "{note-name}" --vault "{vault-name}"
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault

### create
Create a new note, or update an existing one with `--overwrite` or `--append`.
```bash
notesmd-cli create "{note-name}"
notesmd-cli create "{note-name}" --vault "{vault-name}"
notesmd-cli create "{note-name}" --content "{text}"
notesmd-cli create "{note-name}" --content "{text}" --overwrite
notesmd-cli create "{note-name}" --content "{text}" --append
notesmd-cli create "{note-name}" --content "{text}" --open --editor
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault
- `--content "{text}"` — Note body content
- `--overwrite` — Replace existing note content
- `--append` — Append to existing note content
- `--open` — Open note after creation
- `--editor` / `-e` — Open in `$EDITOR` instead of Obsidian

### move
Move or rename a note.
```bash
notesmd-cli move "{current-path}" "{new-path}"
notesmd-cli move "{current-path}" "{new-path}" --vault "{vault-name}"
notesmd-cli move "{current-path}" "{new-path}" --open --editor
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault
- `--open` — Open note after moving
- `--editor` / `-e` — Open in `$EDITOR`

### delete
Delete a note.
```bash
notesmd-cli delete "{note-name}"
notesmd-cli delete "{note-name}" --vault "{vault-name}"
```

**Flags:**
- `--vault "{vault-name}"` — Target a specific vault

## Frontmatter

Manage YAML frontmatter. Alias: `fm`.

### Print frontmatter
```bash
notesmd-cli frontmatter "{note-name}" --print
notesmd-cli fm "{note-name}" --print --vault "{vault-name}"
```

### Edit a frontmatter field
```bash
notesmd-cli frontmatter "{note-name}" --edit --key "{field}" --value "{value}"
```

### Delete a frontmatter field
```bash
notesmd-cli frontmatter "{note-name}" --delete --key "{field}"
```

**Flags:**
- `--print` — Display frontmatter
- `--edit` — Set/update a field (requires `--key` and `--value`)
- `--delete` — Remove a field (requires `--key`)
- `--key "{field}"` — Frontmatter field name
- `--value "{value}"` — Frontmatter field value
- `--vault "{vault-name}"` — Target a specific vault

## Global Flags

These flags are available on most commands:

| Flag | Short | Description |
|------|-------|-------------|
| `--vault "{name}"` | | Target a specific vault instead of the default |
| `--editor` | `-e` | Open in `$EDITOR` (defaults to vim) instead of Obsidian |
| `--open` | | Open note after create/move operations |
| `--help` | `-h` | Show help for any command |
