# {{project_name}}

{{tagline}}

## Rules

- **Python standard library only** — no numpy, torch, tensorflow, or any ML/data framework
- **matplotlib is the sole exception** — allowed for visualization only (in `src/{{pkg}}/viz/`)
- **Compositional layering** — each level imports only from levels below:
  - L0: `primitives/` — scalar, vector, matrix ops, activations, losses, random
  - L1: `building_blocks/` — reusable composite pieces built from primitives
  - L2: `models/` — complete architectures or algorithms
  - `data/` and `viz/` are utilities available to lessons
- Types: `list[float]` for vectors, `list[list[float]]` for matrices, dataclasses for structured objects
- All randomness goes through `src/{{pkg}}/primitives/random.py` with explicit seeds

## Running

- `uv run python lessons/01_*.py` — run a lesson
- `uv run pytest tests/` — run tests

## Structure

- `src/{{pkg}}/primitives/` — L0 ops
- `src/{{pkg}}/building_blocks/` — L1 composites
- `src/{{pkg}}/models/` — L2 architectures
- `src/{{pkg}}/data/` — dataset generation and loading
- `src/{{pkg}}/viz/` — matplotlib visualizations
- `lessons/` — runnable scripts, one per topic, with narrative explanations
- `examples/` — annotated transcripts of lesson output; plots under `examples/img/`
