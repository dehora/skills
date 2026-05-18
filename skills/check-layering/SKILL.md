---
name: check-layering
description: Use when the user invokes /check-layering to verify L0–L7 import discipline in a werk project's src/ tree. Reports any module importing from a higher layer than its own.
user-invocable: true
argument-hint: [path to src/<pkg>] [--map "primitives=0,building_blocks=1,models=2,..."]
allowed-tools: Bash, Read, Glob
---

## What this skill does

Statically checks that every `.py` file under `src/<pkg>/` only imports from the same layer or a strictly lower one. The layering convention is set per project in `CLAUDE.md`; this skill applies the same convention as an AST check so violations surface immediately rather than at runtime.

Exit code is 0 when clean, 1 when violations are found — designed so it can be wired up as a pre-commit hook later.

## Preflight

1. Determine the target src tree:
   - If an explicit path is given as the first positional arg, use it.
   - Else read `pyproject.toml` in the cwd and parse `[tool.hatch.build.targets.wheel] packages = ["src/<pkg>"]`. Use `src/<pkg>`.
   - If neither resolves, print an error and stop.
2. Determine the layer map:
   - If `--map` is provided, parse comma-separated `name=level` pairs.
   - Else read the project's `CLAUDE.md` for lines under the "Compositional layering" section and try to derive layer assignments by matching `L<digit>: <dirname>` patterns.
   - Fall back to the default modelwerk map: `primitives=0, building_blocks=1, models=2, data=2, viz=2, world=2, actors=3`.

## Run

Invoke the script:

```bash
uv run python <path-to-this-skill>/scripts/check_layering.py <src-path> --map "<derived-map>"
```

The script:
- Walks every `.py` file under `<src-path>`.
- Determines each file's layer from the first path segment under `<src-path>`. Files outside the layered dirs (e.g. `src/<pkg>/__init__.py`) are layer 0 by default.
- Parses each file's `import` and `from ... import` statements with `ast`.
- For internal imports of the form `from <pkg>.<dir>...`, looks up `<dir>` in the layer map and flags if its level is strictly greater than the importer's level.
- Ignores external imports (anything that doesn't start with the project's package name).

## Output

If clean, print:
```
check-layering: <N> files, 0 violations.
```

If violations found, print one block per file:
```
[<level>] <importer-file>:<line> imports <imported-module> (level <higher-level>)
```
followed by a summary line:
```
check-layering: <N> files, <V> violations.
```
and exit with code 1.

## Notes

- This is a static check. It doesn't catch dynamic imports (`importlib`) — werk projects don't use those.
- The script lives in `scripts/check_layering.py` and has no third-party deps; uses only the stdlib.
