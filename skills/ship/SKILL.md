---
name: ship
description: Use when the user invokes /ship to commit and push staged work with a present-tense subject and a Claude co-author trailer. Runs GPG and SSH preflight, fails loudly if either is unlocked, never bypasses signing.
user-invocable: true
argument-hint: "<commit subject>" [--paths <p1> <p2> ...] [--no-push]
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

If `$ARGUMENTS` is empty or the subject is missing, print:

```
Usage: /ship "<commit subject>" [--paths <p1> <p2> ...] [--no-push]

Examples:
  /ship "Adds bayeswerk lesson 01 scaffold" --paths lessons/01_bayes_rule.py examples/01_bayes_rule.md
  /ship "Fixes em-dash spacing across docs"
  /ship "Removes deprecated helper" --no-push
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

## Finish

Print a single line:

```
shipped: <short-sha> <commit subject> → <upstream>
```

or, with `--no-push`:

```
committed (not pushed): <short-sha> <commit subject>
```

## Notes

- Never amends. To revise a commit, the user makes a new one (per Bill's git workflow convention).
- Never uses `--no-verify`, `--no-gpg-sign`, or `--force`. If you're tempted to add a flag like that, the answer is no.
- The HEREDOC pattern is required so embedded `$()` and special chars in the subject don't shell-escape badly.
- The "no push to main/master" guard is the only opinionated piece; if a project legitimately ships to `main` directly, the user can `git push` by hand or pass `--no-push` and push manually.
