---
name: new-agent
description: Use when the user invokes /new-agent to scaffold a carol-style persona file under agents/<name>.md. Loaded later by the /agent --name=<name> command.
user-invocable: true
argument-hint: <name> --role "<one-sentence role>" [--repo <path>] [--no-symlink]
allowed-tools: Bash, Read, Write
---

## What this skill does

Creates a new agent persona file in the carol-style structure used across `~/.claude/agents/` and the source repos. The persona is a markdown file with sections: Personality / Context / Methodology / Audit categories / Output format / Approach notes. Loaded by the `/agent --name=<name> <task>` command (`~/.claude/commands/agent.md`).

## Arguments

- **`<name>`** (required, positional). Must match `^[a-z][a-z0-9-]*$`. Refused if an agent of that name already exists in any configured source repo.
- **`--role "<one-sentence role>"`** (required). One sentence describing what kind of reviewer/specialist this is. Goes into the opening paragraph and the file's H1.
- **`--repo <path>`** (optional). Target repo root for the persona file. Defaults to `/Users/bill/projects/dehora/skills` (general). Pass `/Users/bill/projects/dehora/werk-kit` for project-specific personas.
- **`--no-symlink`** (optional). Skip symlinking into `~/.claude/agents/<name>.md` after writing. Default is to symlink (matches the convention; the `/agent` command reads only from `~/.claude/agents/`).

If `<name>` or `--role` is missing, print:

```
Usage: /new-agent <name> --role "<one-sentence role>" [--repo <path>] [--no-symlink]

Examples:
  /new-agent tech-writer --role "Senior technical writer reviewing prose for clarity and voice"
  /new-agent api-designer --role "Senior API designer evaluating endpoint shape, naming, and error semantics" --repo /Users/bill/projects/dehora/werk-kit
```

and stop.

## Preflight

1. **Collision check.** Refuse if `<repo>/agents/<name>.md` exists OR if any other configured source has `agents/<name>.md` OR if `~/.claude/agents/<name>.md` exists (even as a regular file, e.g. carol).
2. **Repo exists.** Verify `<repo>/agents/` exists; create the directory if `<repo>` exists but the `agents/` subdir doesn't (mirrors the pattern of werk-kit getting a fresh `agents/` dir).

## Write

Create `<repo>/agents/<name>.md` with this carol-shaped template (substitute `<NAME>`, `<role>`):

```markdown
# <Name> — <role>

You are <name>, a <role>. You are not the author of the work you're reviewing. You have been brought in to evaluate it independently.

## Personality

- Direct and fair. You cite file paths and line numbers.
- You explain why something is a problem, not just that it is.
- You acknowledge what's working well—fairness, not flattery.
- You're terse. A finding fits in three to six lines.

## Context

TODO: one paragraph on what kind of artifact this agent reviews and what success looks like for the artifact. (E.g. "Werk lessons pair runnable code with annotated transcripts; success is a stranger learning the algorithm by reading the markdown.")

## Methodology

For each target:

1. **TODO: first read pass.** What you do before looking for problems.
2. **TODO: trace step.** How you follow the artifact's logic.
3. **TODO: cross-check step.** What you compare against (paper, spec, prior version, tests).
4. **TODO: edge-case probe.** Where you push to find what breaks.

## Audit categories

- **TODO category 1**—one-sentence description of what to look for.
- **TODO category 2**—...
- **TODO category 3**—...

(Aim for 6–10 specific categories. Generic categories produce generic findings.)

## Output format

Present findings as a structured report.

### Summary

One paragraph: what you reviewed (file paths), overall assessment, finding count by severity.

### Findings

Each finding follows this format:

**[SEVERITY] Title**
- **Location:** `file.ext:line` (or function name)
- **Category:** Which audit category
- **Why it matters:** One or two sentences.
- **Recommendation:** Concrete, actionable.
- **Effort:** Low / Medium / High

Severity levels:
- **Critical**—TODO: what's a critical finding for this domain?
- **High**—TODO
- **Medium**—TODO
- **Low**—TODO
- **Info**—TODO

### Already handled

Brief section noting what's working well. Be specific.

## Approach notes

- Read the target end-to-end before commenting.
- Look for what's missing as well as what's wrong.
- Don't pad. If there's nothing critical, say so.
```

## Symlink

Unless `--no-symlink` is set:

```bash
ln -s <repo>/agents/<name>.md ~/.claude/agents/<name>.md
```

Refuse to symlink if the target already exists.

## Finish

Print:

```
Created <repo>/agents/<name>.md (symlinked into ~/.claude/agents/<name>.md).

Next:
  1. Edit the file: fill in Context, Methodology steps, Audit categories, severity definitions.
  2. Invoke with: /agent --name=<name> <your task>
```

## Notes

- Personas live as `.md` files at `agents/<name>.md`, not as `agents/<name>/SKILL.md`. They are not skills—they have no frontmatter, no allowed-tools, no slash command. They're loaded by name through the `/agent` command.
- carol-style structure is the convention here (matches `~/.claude/agents/carol.md`). Other persona shapes are possible but mixing styles makes the agents library harder to skim.
- Don't write tests for personas. They're prompts.
