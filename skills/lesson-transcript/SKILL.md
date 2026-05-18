---
name: lesson-transcript
description: Use when the user invokes /lesson-transcript to run a werk lesson, capture its stdout and generated plots, and refresh the Output / Plots sections of examples/NN_name.md while preserving the human-written narrative.
user-invocable: true
argument-hint: <NN | path/to/lessons/NN_slug.py> [--no-run]
allowed-tools: Bash, Read, Write, Edit, Glob
---

## What this skill does

Refreshes the generated portions of a lesson's annotated transcript:

1. Runs the lesson via `uv run python lessons/NN_slug.py`, capturing stdout/stderr.
2. Collects any PNG/SVG files produced by the lesson (matplotlib `savefig`) and moves them into `examples/img/NN_slug/`.
3. Edits `examples/NN_slug.md`:
   - Replaces the content between `<!-- BEGIN OUTPUT -->` and `<!-- END OUTPUT -->` with the fresh stdout (fenced as a code block).
   - Replaces the content between `<!-- BEGIN PLOTS -->` and `<!-- END PLOTS -->` with one image link per captured plot.
   - Inserts the markers around an existing `## Output` / `## Plots` heading if they're not present yet (one-time migration).
   - Leaves all other content — narrative, headings, in-line annotations — untouched.

Narrative sections OUTSIDE the markers are never modified.

## Preflight

1. Verify cwd is a werk project (`lessons/`, `examples/`, `pyproject.toml` exist).
2. Parse `$ARGUMENTS`:
   - First arg is either two digits (`NN`, in which case glob `lessons/NN_*.py` and require exactly one match) or a path to a `.py` file under `lessons/`.
   - `--no-run` (optional): skip the run step; only resync from a previously written `.transcript-<slug>.stdout` cache file. Useful when the lesson is slow.
3. Derive `slug` from the matched filename, and the target markdown path `examples/<NN>_<slug>.md`. If the markdown file doesn't exist, suggest `/new-lesson <NN> <slug>` first and stop.

## Run

Invoke the capture script from this skill's `scripts/` directory:

```bash
uv run python <path-to-this-skill>/scripts/run_lesson.py lessons/<NN>_<slug>.py
```

The script:
- Runs the lesson with `cwd` at the project root.
- Captures stdout + stderr to `.lesson-transcript/<NN>_<slug>.stdout`.
- Detects every PNG/SVG file written into the project root, `output/`, or `examples/` during the run (mtime check before/after) and moves them into `examples/img/<NN>_<slug>/`.
- Prints a small JSON manifest on its own stdout: `{"stdout_path": "...", "plots": ["..."], "exit_code": N}`.

If `--no-run` is passed, skip invoking the script and read `.lesson-transcript/<NN>_<slug>.stdout` and `examples/img/<NN>_<slug>/` directly.

## Update the markdown

Read `examples/<NN>_<slug>.md`. Apply edits in this order:

1. **One-time migration:** If the `<!-- BEGIN OUTPUT -->` marker is missing, look for a `## Output` heading and insert markers immediately after it (before the next H2). Same for `## Plots` / `<!-- BEGIN PLOTS -->`. If neither heading exists, append both at the end of the file. Save.
2. **Refresh Output block:** Replace everything between `<!-- BEGIN OUTPUT -->` and `<!-- END OUTPUT -->` with:
   ````
   <!-- BEGIN OUTPUT -->
   ```
   <stdout contents>
   ```
   <!-- END OUTPUT -->
   ````
3. **Refresh Plots block:** Replace everything between `<!-- BEGIN PLOTS -->` and `<!-- END PLOTS -->` with one Markdown image per captured plot, in filename order:
   ```
   <!-- BEGIN PLOTS -->
   ![<basename without ext>](img/<NN>_<slug>/<filename>)
   ...
   <!-- END PLOTS -->
   ```

Use the `Edit` tool with sufficiently unique `old_string` (include both markers) to make each replacement deterministic.

## Finish

Print a one-line summary:
```
Refreshed examples/<NN>_<slug>.md — captured <N> lines of stdout, <M> plots. Exit code: <N>.
```

If exit code is non-zero, surface the last 20 lines of stderr and stop without committing further edits.

## Notes

- The `.lesson-transcript/` directory is meant to be gitignored; add it to `.gitignore` if not already present (one-line append, idempotent).
- Plots already inside `examples/img/<NN>_<slug>/` from prior runs are listed alongside newly captured ones (we union by filename, newest mtime wins).
- The narrative-preservation contract is: anything between the markers is regenerated; everything else is treated as user-authored.
