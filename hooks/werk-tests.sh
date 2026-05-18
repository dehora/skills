#!/usr/bin/env bash
# Pre-commit: run pytest if any staged change touches src/ or lessons/.
# Exits 0 when there's nothing to run.
#
# Bypass with: WERK_HOOKS_SKIP=1 git commit ...

set -euo pipefail

if [[ "${WERK_HOOKS_SKIP:-0}" == "1" ]]; then
  exit 0
fi

# Only consider changes that are actually staged for this commit.
staged="$(git diff --cached --name-only --diff-filter=ACMR || true)"

if [[ -z "$staged" ]]; then
  exit 0
fi

if ! grep -qE '^(src/|lessons/)' <<< "$staged"; then
  exit 0
fi

if [[ ! -f pyproject.toml ]]; then
  echo "werk-tests: no pyproject.toml in repo root; skipping." >&2
  exit 0
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "werk-tests: uv not on PATH; skipping." >&2
  exit 0
fi

echo "werk-tests: src/ or lessons/ changed — running pytest." >&2
uv run pytest -q
