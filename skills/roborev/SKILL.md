---
name: roborev
description: Use when the user invokes /roborev to get an external code review (codex CLI or equivalent) on the current branch's diff against a base ref. Returns a carol-style structured findings report. Local only—not a CI step.
user-invocable: true
argument-hint: [--base <ref, default main>] [--reviewer codex|claude] [--scope diff|files]
allowed-tools: Bash, Read
---

## What this skill does

Runs an external reviewer against the current branch's diff and surfaces its findings inside this Claude Code session, formatted the same way as `~/.claude/agents/carol.md` (`[SEVERITY] Title / Location / Evidence / Recommendation / Effort`). The point is to bring an out-of-loop review step into the in-loop workflow.

Important: this is local only. It does not push, comment on PRs, or talk to any remote system. The external reviewer runs against the local diff.

## Arguments

- `--base <ref>`—base ref to diff against. Defaults to `main`. Falls back to `master` if `main` doesn't exist.
- `--reviewer codex|claude`—which external CLI to invoke. Defaults to `codex`.
- `--scope diff|files`—`diff` (default) pipes the unified diff to the reviewer; `files` lists the changed file paths and lets the reviewer read them.

## Preflight

1. Verify cwd is a git repo (`git rev-parse --is-inside-work-tree`).
2. Determine the base ref:
   - If `--base` is provided, use it.
   - Else use `main` if `git rev-parse --verify main` succeeds, otherwise `master`.
   - If neither exists, stop and tell the user to pass `--base`.
3. Compute the changed range:
   ```bash
   git rev-parse --abbrev-ref HEAD
   git log --oneline <base>..HEAD
   git diff --stat <base>..HEAD
   ```
4. Refuse if working tree is dirty (`git status --porcelain` non-empty)—the reviewer should look at committed changes, not in-progress edits. Tell the user to stash or commit first.
5. Check that the selected reviewer CLI is on PATH:
   - `codex` → `command -v codex`
   - `claude` → `command -v claude` (any `claude` CLI)

   If the binary is missing, print a clearly-marked install hint block (see "Reviewer setup" below) and stop without invoking anything.

## Invoke the reviewer

> NOTE: The exact `codex` invocation is not pinned upstream. Treat the block below as a starting point and confirm against the codex CLI version on the user's system before relying on it in scripts.

For `--reviewer codex --scope diff`:

```bash
git diff <base>..HEAD | codex exec --quiet \
  "You are a senior staff engineer doing a focused code review. Read the following unified diff and report findings in this exact format, one per finding:

  [SEVERITY] Title
  - Location: <file>:<line>
  - Category: <category>
  - Evidence: <quoted snippet or short description>
  - Recommendation: <how to fix>
  - Effort: Low|Medium|High

  Severity levels: Critical, High, Medium, Low, Info.
  End with an 'Already handled' section noting controls that look correct.
  Do not invent issues—if there are no findings at a level, say so."
```

For `--scope files`: list changed files via `git diff --name-only <base>..HEAD` and pass them as `--cd` / context hints depending on what the reviewer supports.

For `--reviewer claude`: substitute the `claude -p ...` non-interactive form.

## Parse and present

The external reviewer is expected to return prose in the `[SEVERITY] ...` format above. Do not try to reformat or summarize aggressively—pass the findings through verbatim, but:

- Re-emit each finding as a Markdown block with bold severity tag.
- Group findings under H3s by severity: Critical, High, Medium, Low, Info.
- Show the "Already handled" section last.
- If the reviewer's output doesn't fit the format (e.g. plain prose), wrap it under a single `### Reviewer output` block and warn the user inline.

End with a one-line summary:
```
roborev: <reviewer> reviewed <N> files (<M> findings: <crit>C/<high>H/<med>M/<low>L/<info>I).
```

## Reviewer setup (printed on missing CLI)

```
roborev requires an external reviewer CLI. Detected: <missing>.

To install codex:
  https://github.com/openai/codex          # check upstream for current install steps

Once installed, verify with:
  codex --version

Alternatively, run /roborev --reviewer claude to use a local claude CLI.
```

## Notes

- This skill does NOT add `Co-Authored-By:` trailers or modify any files. It is read-only beyond the reviewer process.
- The diff is piped through stdin to the reviewer—no diff file is written to disk.
- If the user wants ongoing review, run this skill once per significant push, not per commit.
