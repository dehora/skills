---
name: ship
description: Use when the user invokes /ship to commit and push staged work with a present-tense subject and a Claude co-author trailer. Runs GPG and SSH preflight, fails loudly if either is unlocked, never bypasses signing.
user-invocable: true
argument-hint: "<commit subject>" [--paths <p1> <p2> ...] [--no-push] [--no-audit]
allowed-tools: Bash, Read
---

## What this skill does

Turns the "check GPG, check SSH, stage, commit with present-tense subject and Claude co-author, push to upstream" routine into a single command. The point is determinism: every commit follows the same shape, with the same preflight, so the user never has to ask "did you check GPG first?"

This skill is read-only against the working tree apart from `git add` and `git commit`. It never amends, never force-pushes, never bypasses signing.

## Arguments

Parse `$ARGUMENTS`:

- **`<commit subject>`** (required, positional, in quotes). Must be present tense ("Adds X", "Fixes Y", "Removes Z", "Renames A to B"). If the first word is past tense ("Added", "Fixed", "Removed") or progressive ("Adding"), warn and stop—ask the user to rephrase.
- **`--paths <p1> <p2> ...`** (optional). Paths to stage with `git add`. If omitted, the skill stages nothing on its own and uses what's already in the index. Refuses if both the index and the working tree have nothing to commit.
- **`--no-push`** (optional). Stop after commit; don't push. Default is to push to the current branch's upstream.
- **`--no-audit`** (optional). Skip the post-push roborev audit step. Default is to enqueue (or wait for the post-commit-hook-enqueued) review of HEAD and surface findings inline, per the Audit section below.

If `$ARGUMENTS` is empty or the subject is missing, print:

```
Usage: /ship "<commit subject>" [--paths <p1> <p2> ...] [--no-push] [--no-audit]

Examples:
  /ship "Adds bayeswerk lesson 01 scaffold" --paths lessons/01_bayes_rule.py examples/01_bayes_rule.md
  /ship "Fixes em-dash spacing across docs"
  /ship "Removes deprecated helper" --no-push
  /ship "WIP checkpoint" --no-audit
```

and stop.

## Preflight

1. **Working directory is a git repo.** `git rev-parse --is-inside-work-tree` succeeds, or stop with a clear message.
2. **GPG unlocked.** Run `echo "test" | gpg --clearsign >/dev/null 2>&1`. If the exit code is non-zero, stop with:
   ```
   GPG agent is locked. Unlock with:
     ! echo "test" | gpg --clearsign
   Then re-run /ship.
   ```
   Do not attempt to disable signing.
3. **SSH agent has identities.** `ssh-add -l 2>/dev/null | grep -q .`. If not:
   ```
   SSH agent has no identities. Load your key with:
     ! ssh-add --apple-use-keychain
   Then re-run /ship.
   ```
   (Only required if push will happen; skip this check when `--no-push` is set.)
4. **Subject sanity-check.** Strip outer quotes from `<commit subject>`. First word must match `^[A-Z][a-z]+s$` (Adds / Fixes / Removes / Renames / Updates / Refactors / Moves) OR be one of the small set of allowed verbs that don't fit the regex (e.g. "Splits", "Drops", "Bumps"). If the first word ends in "ed" or "ing", stop and ask the user to use present tense.

## Stage and review

If `--paths` was provided, run `git add <paths>` (no `-A`, no `.`).

Then show the user a quick diffstat:

```
=== staged for commit ===
$(git diff --cached --stat)
=== branch ===
$(git rev-parse --abbrev-ref HEAD)
```

If the index is empty after staging, stop with "Nothing staged for commit. Use --paths or stage with `git add` first."

## Commit

Build the commit message with a HEREDOC pattern (matches the existing skills/werk-kit commit style):

```bash
git commit -m "$(cat <<'EOF'
<commit subject>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

If the commit fails because of a pre-commit hook, do not retry, do not amend. Surface the hook output and stop. The user will fix and re-run.

## Push

Unless `--no-push` is set:

1. Check the current branch has an upstream: `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null`. If no upstream, stop and tell the user to set one explicitly (don't silently `--set-upstream` to a guess).
2. **Refuse to push to `main` or `master`** with this skill if the upstream branch matches `(.*/)?\b(main|master)$`. Print:
   ```
   /ship refuses to push directly to main/master. Push manually after a review or open a PR.
   ```
3. Otherwise: `git push`. Surface the last 5 lines of the push output.

## Audit (default on)

Unless `--no-audit` is set, run a roborev audit pass against the new HEAD before printing the Finish line.

1. **Preflight skip.** If any of these are false, print a one-line note (`audit: skipped—<reason>`) and continue to Finish without surfacing findings:
   - `roborev status` exits 0 and reports daemon running.
   - `roborev repo list 2>&1 | grep -q "$(pwd -P)"` (repo is registered with the daemon).
   - The post-commit hook is plausibly handling this—i.e. either `.git/hooks/post-commit` exists and references `roborev`, OR `roborev list --json --limit 1` shows a job for the just-shipped commit within the last 30 seconds.

   The audit step is best-effort. Daemon down or repo not registered is never a hard failure for `/ship`.

2. **Find the job.** If the post-commit hook fired automatically:
   ```bash
   roborev wait HEAD          # blocks until the job for HEAD completes (or returns immediately if done)
   ```
   If no job appears for HEAD within 5 seconds (`roborev list --json --limit 5` doesn't include the new SHA), enqueue one manually:
   ```bash
   roborev review HEAD --wait
   ```

   `roborev wait` exit code is the verdict: 0 = PASS (no findings to action), 1 = FAIL (findings exist) or job error.

3. **PASS path.** Exit code 0 + verdict P → print `audit: clean (job <id>).` and continue to Finish.

4. **FAIL path.** Exit code 1 → fetch the structured findings for the HEAD job:
   ```bash
   JOB=$(roborev list --json --limit 1 | python3 -c "import json,sys; d=json.load(sys.stdin) or []; print(d[0]['id']) if d else ''")
   python3 /Users/bill/projects/dehora/skills/skills/roborev/scripts/roborev_query.py parse "$JOB" --job
   ```

   Then apply the same Tier 1/2/3 policy as `/audit`:
   - **Critical / High** → auto-fix (subject to the memory-veto rule documented in [[audit]]/SKILL.md), then commit the follow-up via `/ship "Addresses roborev findings: <list>" --no-audit` (the `--no-audit` matters—prevents recursion), then `roborev comment <job_id> -m "Addressed in <new-sha>: <note>"` + `roborev close <job_id>`.
   - **Medium** → present proposed-action blocks, `AskUserQuestion` for y/n/skip per finding, action the y's the same way.
   - **Low / Info** → one-line summary each, don't action.

   Bound the iteration: `/ship`'s audit step runs at most one fix pass. After the follow-up `--no-audit` commit, surface what was done and stop. If more passes are needed, the user runs `/audit` explicitly.

5. **Cite memory.** If a Tier-1 finding gets demoted to Tier 2 because it conflicts with a memory entry, name the entry inline so the user can spot a bad demotion.

## Finish

Print a single line summarizing what happened. The shape depends on which paths ran:

```
shipped: <short-sha> <commit subject> → <upstream> [audit: clean | audit: <N> findings actioned | audit: skipped]
```

or, with `--no-push`:

```
committed (not pushed): <short-sha> <commit subject>
```

When the Audit step actioned findings and emitted a follow-up commit, the final line names *both* shas:

```
shipped: <sha-1> <subject> → <upstream> + <sha-2> <follow-up subject> (audit: <N> actioned)
```

## Notes

- Never amends. To revise a commit, the user makes a new one (per Bill's git workflow convention).
- Never uses `--no-verify`, `--no-gpg-sign`, or `--force`. If you're tempted to add a flag like that, the answer is no.
- The HEREDOC pattern is required so embedded `$()` and special chars in the subject don't shell-escape badly.
- The "no push to main/master" guard is the only opinionated piece; if a project legitimately ships to `main` directly, the user can `git push` by hand or pass `--no-push` and push manually.
