---
name: audit
description: Use when the user invokes /audit to surface open roborev findings on the current branch and action them per the standing policy (auto-fix Critical+High, ask on Medium, skip Low/Info). Closes the manual filter loop.
user-invocable: true
argument-hint: "[--branch <name>] [--include-low] [--dry-run] [--max-iterations <N>] [--repo <path>]"
allowed-tools: Bash, Read, Write, Edit
---

## What this skill does

Catches up on open roborev reviews—findings the daemon has produced but I haven't responded to yet—and actions them per the policy below. Companion to `/roborev` (on-demand, read-only) and `/ship` (per-commit audit step). Use `/audit` when the user wants to drain the backlog without re-committing.

### Standing policy

| Severity | Action |
|---|---|
| Critical | Auto-fix. Edit the cited files, run targeted tests if available, commit via `/ship`, close the review with a `roborev comment` + `roborev close`. |
| High | Same as Critical. |
| Medium | Surface to the user with my proposed action; wait for y/n/skip. On y, do the fix loop. On n/skip, `roborev comment <id> "Not addressing this round: <reason>"` and leave open. |
| Low / Info | List one line each. Don't action. Override with `--include-low` to promote to Medium handling. |

### Memory veto

A Critical/High finding that *would* be auto-actioned but conflicts with a memory entry in this project (`feedback_*.md`) is **demoted to Medium**. Examples:

- Roborev says "extract this helper" but [[feedback_code_structure]] says "keep training loops in one function" → demote, ask.
- Roborev's suggested fix would introduce spaced em dashes in prose → demote, ask.
- Roborev contradicts a `feedback_lesson_review` finding from a recent review the user closed deliberately → demote, ask.

Memory wins. Always cite the conflicting memory entry in the proposed-action text.

## Arguments

- `--branch <name>`—limit to one branch. Default: current branch.
- `--repo <path>`—limit to one repo. Default: current cwd.
- `--include-low`—surface Low and Info findings as Medium (ask before action).
- `--dry-run`—list and group findings; never edit, never commit, never call `roborev close`.
- `--max-iterations <N>`—fix loop bound (default 3). After each round of fixes, the post-commit hook enqueues new reviews; `/audit` waits for them and re-runs the policy until either zero open or `N` passes.

## Preflight

1. `roborev status` exits 0 and reports daemon running. If not, print the same hint as `/roborev` and stop.
2. `git rev-parse --is-inside-work-tree` succeeds (in `--repo` if set, else cwd).
3. Repo is roborev-registered (`roborev repo list` includes the path). If not, suggest `roborev init` and stop.
4. Determine the target branch:
   ```bash
   BRANCH="${1:-$(git -C "$REPO" symbolic-ref --short HEAD)}"
   ```

## Run

Print the iteration banner each pass:

```
audit pass 1/N—branch <name>, repo <path>
```

### Step 1—fetch open findings

```bash
python3 <SKILL_DIR>/scripts/roborev_query.py open --branch "$BRANCH" --repo "$REPO"
```

(Where `<SKILL_DIR>` is `/Users/bill/projects/dehora/skills/skills/roborev`—the query helper lives next to the `/roborev` skill, not under `/audit`. Both skills share it.)

Parse the JSON list. For each entry, also call `parse <job_id> --job` to get structured findings.

Print the histogram:

```
audit: <N> open job(s), <M> findings total—<C>C / <H>H / <Med>M / <L>L / <I>I
```

If `N == 0`, print `audit: nothing open on <branch>.` and exit 0.

### Step 2—process Tier 1 (Critical + High)

For each Critical/High finding:

1. **Memory check.** Read every `feedback_*.md` in this project's memory dir (`~/.claude/projects/-Users-bill-projects-dehora-<repo-slug>/memory/`) and consider whether the finding's proposed fix violates any rule. If so, demote to Tier 2 with a note: `Demoted to Medium: conflicts with feedback_<X>.md—<one-line reason>`.
2. **Read the cited files.** Use the locations array; read each file.
3. **Plan and apply.** Compose the diff in-head, apply via `Edit`. Don't re-architect; do the minimum the finding asks for.
4. **Test (best-effort, non-blocking).** If `pyproject.toml` and a sensible test module exist for the changed file, run `uv run pytest -q tests/test_<module>.py`. If tests fail, abort the fix for this finding, leave the edit reverted, demote to Tier 2 with `tests failing`.
5. **Stage.** `git add` the files touched for this finding.

After all Tier 1 fixes are staged:

6. **Commit via /ship.** Run `/ship "Addresses roborev findings: <short list of severities+files>" --no-audit`. The `--no-audit` matters: `/ship` would otherwise trigger another audit and recurse. Per-commit audit happens via the post-commit hook + this skill's loop.
7. **Close reviews.** For each finding that was actioned, run:
   ```bash
   roborev comment <job_id> -m "Addressed in $(git rev-parse --short HEAD): <one-line note>"
   roborev close <job_id>
   ```

### Step 3—process Tier 2 (Medium + demoted findings)

For each Medium finding (or demoted Critical/High):

1. Print the proposed-action block:
   ```
   [Medium] <title>
     Location:  file.py:line, ...
     Problem:   <verbatim>
     Fix:       <verbatim>
     I would:   <one paragraph—what I'd change, files I'd touch, why>
     Conflicts: <memory entry, if demoted>
   ```
2. Use `AskUserQuestion` to collect y/n/skip per finding. If more than 3 findings, batch into a single `multiSelect: true` "Which to action?" question to avoid prompt fatigue.
3. For each `y`: do the fix loop (read → edit → test → stage). After all y-answered findings are staged, commit via `/ship "Addresses roborev Medium findings: <list>" --no-audit`, then comment/close per finding.
4. For each `n` or `skip`: `roborev comment <job_id> -m "Not addressing this round: <user-supplied reason or 'deferred'>"` and leave the review open.

### Step 4—Tier 3 (Low + Info)

Print one line per finding:

```
[low] file.py:line—short problem text (first sentence)
```

If `--include-low` is set, promote each to Tier 2 instead.

### Step 5—iterate

After Tier 1 and Tier 2 fixes commit, the roborev post-commit hook enqueues new reviews on the new HEAD. To wait for them:

```bash
roborev wait HEAD
```

`roborev wait` blocks until the new job(s) complete. Exit code 0 = PASS, exit 1 = FAIL or error. Either way, re-run the Step 1–4 loop. Stop when:

- Step 1 reports zero open findings on the branch, OR
- iteration count reaches `--max-iterations` (default 3), OR
- two consecutive passes produce the same finding set (stall detection).

## Finish

Print a summary:

```
audit: 0 open / N actioned / M deferred. <iterations> pass(es). Branch <name>.
```

Exit 0 if zero open, 1 otherwise.

## --dry-run mode

Steps 1, 2-without-fixing, 3-without-asking, 4. Print everything but never call `Edit`, `Write`, `/ship`, `roborev close`, or `roborev comment`. Always exits 0.

## Notes

- The "test best-effort" rule is intentionally loose. The goal is to catch obvious regressions, not enforce CI-grade discipline inside the skill. If a project has a test command beyond `uv run pytest`, the user should run their own checks after `/audit` finishes.
- `roborev close` is *only* called for findings that were actually fixed in the current commit. Skipped findings stay open; that's the persistence channel for "I saw this and chose not to act."
- The memory-veto rule is the load-bearing safety mechanism. Without it, auto-fix could quietly contradict a documented preference. Always cite the conflicting memory file in the demotion note so the user can spot bad demotions.
- A per-finding commit is rarely worth it—group all Tier 1 fixes into one commit, then all Tier 2 (user-approved) fixes into a second commit. Two commits per audit pass is the target shape.
- This skill does NOT use `roborev refine` (the built-in fix loop). That tool delegates fixes to a fresh agent without project memory; `/audit` keeps the loop inside the current Claude session for memory-aware decisions.
