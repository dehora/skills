#!/usr/bin/env bash
# Pre-commit: fail (or warn) when committing changes to lessons/NN_*.py
# without refreshing the matching examples/NN_*.md transcript.
#
# Detection: any staged change under lessons/NN_<slug>.py whose matching
# examples/NN_<slug>.md exists and has an older mtime than the lesson.
#
# Bypass with: WERK_HOOKS_SKIP=1 git commit ...
# Downgrade to warning with: WERK_STALE_WARN_ONLY=1 git commit ...

set -euo pipefail

if [[ "${WERK_HOOKS_SKIP:-0}" == "1" ]]; then
  exit 0
fi

staged="$(git diff --cached --name-only --diff-filter=ACMR || true)"

if [[ -z "$staged" ]]; then
  exit 0
fi

stale=()
while IFS= read -r path; do
  [[ "$path" =~ ^lessons/([0-9]{2}_[a-z0-9_]+)\.py$ ]] || continue
  stem="${BASH_REMATCH[1]}"
  md="examples/${stem}.md"
  if [[ ! -f "$md" ]]; then
    continue
  fi
  # Compare mtimes using stat. Cross-platform-ish: try GNU first, fall back to BSD.
  py_mtime="$(stat -c %Y "$path" 2>/dev/null || stat -f %m "$path")"
  md_mtime="$(stat -c %Y "$md"   2>/dev/null || stat -f %m "$md")"
  if (( py_mtime > md_mtime )); then
    stale+=("$path -> $md")
  fi
done <<< "$staged"

if (( ${#stale[@]} == 0 )); then
  exit 0
fi

echo "werk-stale-transcript: staged lesson(s) newer than their transcript:" >&2
for s in "${stale[@]}"; do
  echo "  $s" >&2
done

if [[ "${WERK_STALE_WARN_ONLY:-0}" == "1" ]]; then
  echo "werk-stale-transcript: WARN ONLY (WERK_STALE_WARN_ONLY=1) — commit proceeds." >&2
  exit 0
fi

cat >&2 <<EOF

Refresh the transcript with /lesson-transcript, or set
WERK_STALE_WARN_ONLY=1 to downgrade this to a warning,
or WERK_HOOKS_SKIP=1 to bypass entirely.
EOF
exit 1
