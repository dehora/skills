---
name: new-lesson
description: Use when the user invokes /new-lesson to create a matched lesson pair — lessons/NN_name.py and examples/NN_name.md — with the standard werk-series headers.
user-invocable: true
argument-hint: <NN> <slug> [--title "Pretty Title"] [--paper "Author, Year"]
allowed-tools: Bash, Read, Write, Glob
---

## What this skill does

Creates a matched lesson pair in the current werk project:

- `lessons/NN_<slug>.py` — runnable Python with the standard header docstring and `if __name__ == "__main__"` stub
- `examples/NN_<slug>.md` — annotated transcript scaffold with title, Run section, Output placeholder, and Plots section

## Preflight

1. Verify the cwd is a werk-shaped project: `lessons/` and `examples/` directories exist and `pyproject.toml` is present.
2. Read `pyproject.toml` to find the python package name (`packages = ["src/<pkg>"]`). Use it for import stubs in the lesson template. If not found, fall back to `<pkg>` literal and warn.
3. Parse `$ARGUMENTS`:
   - **`<NN>`** (required) — exactly two digits, matches `^[0-9]{2}$`.
   - **`<slug>`** (required) — matches `^[a-z][a-z0-9_]*$` (lowercase letters, digits, underscores; must start with a letter).
   - **`--title "Pretty Title"`** (optional) — defaults to the slug with underscores → spaces and title-cased.
   - **`--paper "Author, Year"`** (optional) — defaults to `TODO: paper reference` placeholder.
4. Refuse if `lessons/NN_<slug>.py` or `examples/NN_<slug>.md` already exists. List the conflicting paths and stop.

If `$ARGUMENTS` is empty or malformed, print:
```
Usage: /new-lesson <NN> <slug> [--title "Pretty Title"] [--paper "Author, Year"]

Examples:
  /new-lesson 01 bayes_rule --title "Bayes' Rule" --paper "Bayes, 1763"
  /new-lesson 02 beta_bernoulli
```
and stop.

## Write the lesson file

`lessons/<NN>_<slug>.py`:

```python
"""Lesson <NN>: <Title> (<Paper>).

<TODO: one-paragraph motivation — what this lesson teaches and why it matters.>

Run: uv run python lessons/<NN>_<slug>.py
"""

import os

# from <pkg>.primitives.random import create_rng
# from <pkg>.building_blocks import ...
# from <pkg>.models import ...

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    # TODO: implement the lesson body.
    print("Lesson <NN>: <Title>")


if __name__ == "__main__":
    main()
```

Substitute `<NN>`, `<slug>`, `<Title>`, `<Paper>`, `<pkg>` with the parsed values.

## Write the examples file

`examples/<NN>_<slug>.md`:

```markdown
# Lesson <NN>: <Title> (<Paper>)

<TODO: opening narrative — what the lesson covers, why it matters, the key intuition.>

## Run

```bash
uv run python lessons/<NN>_<slug>.py
```

## Output

```
<TODO: paste annotated stdout here, or run /lesson-transcript <NN> to refresh automatically.>
```

## Plots

<TODO: link figures from `examples/img/<NN>_<slug>/`.>
```

## Finish

Print:

```
Created lessons/<NN>_<slug>.py and examples/<NN>_<slug>.md.

Next: implement the lesson body, then run:
  uv run python lessons/<NN>_<slug>.py
  /lesson-transcript <NN>
```
