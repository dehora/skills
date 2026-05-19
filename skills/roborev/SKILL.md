---
name: roborev
description: Use when the user invokes /roborev to run an on-demand code review via the local roborev daemon, against HEAD or uncommitted changes. Surfaces structured findings inline. Companion to /ship (commit-time audit) and /audit (catch-up).
user-invocable: true
argument-hint: "[--ref HEAD|<sha>] [--dirty] [--agent codex|claude-code|...] [--type security|design]"
allowed-tools: Bash, Read
---

## What this skill does

Asks the local roborev daemon to review either HEAD or the current uncommitted changes, waits for the result, and surfaces findings inline. This is the on-demand entry point. For per-commit audit see `/ship`; for catch-up over open findings on the branch see `/audit`.

The skill never auto-applies fixes. It reads, summarizes, and stops. To address findings, the user (or `/audit` in a separate invocation) drives the response.

## Arguments

- `--ref <sha>` (optional) — review a specific commit. Default is HEAD.
- `--dirty` (optional) — review uncommitted changes instead of a commit. Useful before staging.
- `--agent <name>` (optional) — override the default agent (`codex` per daemon config). Accepts `codex`, `claude-code`, `gemini`, `copilot`, `opencode`, `cursor`, `kiro`, `kilo`, `pi`.
- `--type <kind>` (optional) — `security` or `design` switches the system prompt. Default is the general review prompt.

If `--ref` and `--dirty` are both passed, refuse and ask which is intended.

## Preflight

1. **Daemon running.** `roborev status` exits 0 and reports `Daemon: running`. If not, print:
   ```
   roborev daemon is not running. Start with: roborev daemon start
   Then re-run /roborev.
   ```
   and stop.
2. **In a git repo.** `git rev-parse --is-inside-work-tree` succeeds.
3. **Repo is roborev-init'd.** `roborev repo list 2>&1 | grep -q "$(pwd)"` or the daemon will reject the review. If not, suggest:
   ```
   This repo is not registered with roborev. Initialize with:
     cd "$(pwd)" && roborev init
   Then re-run /roborev.
   ```

## Run

Build the `roborev review` invocation:

- `--dirty` → `roborev review --dirty --wait`
- otherwise → `roborev review <ref> --wait` (default ref: HEAD)
- Pass `--agent <name>` and/or `--type <kind>` through if provided.

`--wait` makes the call synchronous; capture stdout (which usually echoes the job header) and the exit code.

Then fetch and parse the structured form:

```bash
# Get the job id of the most recently completed review for this ref.
JOB=$(roborev list --json --limit 1 | python3 -c "import json,sys; d=json.load(sys.stdin) or []; print(d[0]['id']) if d else ''")
python3 <SKILL_DIR>/scripts/roborev_query.py parse "$JOB" --job
```

(`<SKILL_DIR>` resolves to this skill's directory at runtime; in practice substitute `/Users/bill/projects/dehora/skills/skills/roborev`.)

## Surface

Render the parsed output inline. Format mirrors `~/.claude/agents/carol.md` so output is visually consistent with `/audit` and the staff-engineer / applied-scientist reviewers.

```
roborev: <agent> reviewed <sha> on <branch> (<repo>). Verdict: PASS|FAIL.

### Critical
(none)

### High
(none)

### Medium
**[Medium] <short title from the problem first sentence>**
- **Location:** `file.py:line`, `file.py:line`
- **Problem:** <verbatim problem text>
- **Fix:** <verbatim fix text>

### Low
(none)

### Summary
<verdict-level summary from the review>
```

Severity sections are omitted entirely if empty; never print "(none)" five times. If the review is `No issues found.`, print:

```
roborev: <agent> reviewed <sha> on <branch> (<repo>). Verdict: PASS.
No issues found. <summary>
```

## Notes

- This skill never closes the review (`roborev close`) and never adds a comment. It is read-only. `/audit` is the right entry point when the goal is to address findings.
- The daemon's default reasoning level is `thorough` (~1–3 minutes per review). With `--agent claude-code` or `--type security` the time can be longer; `--fast` (passed through if needed) trades depth for speed.
- The post-commit hook (if installed in the repo via `roborev install-hook`) already enqueues a review for every commit. `/roborev` is the right tool when you want one *now* without committing, or to re-read an existing review of HEAD without re-enqueuing.
