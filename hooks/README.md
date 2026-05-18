# Hooks

Reusable git hook scripts for werk-series projects. Each script is standalone and idempotent — symlink it into a project's `.git/hooks/` directory or invoke it from an existing hook.

## Available hooks

- **`werk-tests.sh`** — pre-commit: runs `uv run pytest -q` if any staged change touches `src/` or `lessons/`. Blocks the commit on test failure.
- **`werk-stale-transcript.sh`** — pre-commit: warns (and fails by default) when a `lessons/NN_*.py` file is being committed but its `examples/NN_*.md` is older. Set `WERK_STALE_WARN_ONLY=1` to downgrade the failure to a warning.

## Install

In the target werk project:

```bash
# pick whichever hook(s) you want, or chain both
ln -s /Users/bill/projects/dehora/skills/hooks/werk-tests.sh         .git/hooks/pre-commit
# or, to install both, write a tiny dispatch hook:
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
set -e
/Users/bill/projects/dehora/skills/hooks/werk-tests.sh
/Users/bill/projects/dehora/skills/hooks/werk-stale-transcript.sh
EOF
chmod +x .git/hooks/pre-commit
```

Both scripts exit 0 when there's nothing to do, so they're safe to leave in place on every commit.

## Skipping

To bypass a single commit (e.g. WIP commit on a branch you'll squash later):

```bash
WERK_HOOKS_SKIP=1 git commit -m "wip"
```

Both scripts check `$WERK_HOOKS_SKIP` and exit 0 when set. This is intentional: it keeps the hooks from being load-bearing in ways that fight the user. Do not extend this to `--no-verify` patterns in commit-message advice — the explicit env var keeps the bypass deliberate.
