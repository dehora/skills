"""AST-based layer-discipline check for werk-series projects.

Walks every .py file under <src-path> (e.g. src/modelwerk) and reports any
import that crosses from a lower layer to a higher one. Higher-numbered
layers may import from lower-numbered layers; the reverse is a violation.

Usage:
    uv run python check_layering.py src/<pkg> [--map "primitives=0,building_blocks=1,models=2"]
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


DEFAULT_MAP = {
    "primitives": 0,
    "building_blocks": 1,
    "models": 2,
    "data": 2,
    "viz": 2,
    "world": 2,
    "actors": 3,
}


def parse_map(spec: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise SystemExit(f"Bad --map entry: {part!r}")
        name, level = part.split("=", 1)
        out[name.strip()] = int(level.strip())
    return out


def file_layer(src_root: Path, file: Path, layers: dict[str, int]) -> int:
    """Layer of a file: from its first path segment under src_root."""
    rel = file.relative_to(src_root)
    if len(rel.parts) < 2:
        return 0
    seg = rel.parts[0]
    return layers.get(seg, 0)


def package_name(src_root: Path) -> str:
    return src_root.name


def check_file(
    file: Path,
    src_root: Path,
    pkg: str,
    layers: dict[str, int],
) -> list[tuple[int, str, int, int]]:
    """Return list of (lineno, imported_module, imported_level, file_level) violations."""
    importer_level = file_layer(src_root, file, layers)
    try:
        tree = ast.parse(file.read_text(), filename=str(file))
    except SyntaxError as e:
        return [(e.lineno or 0, f"<syntax error: {e.msg}>", -1, importer_level)]

    violations: list[tuple[int, str, int, int]] = []

    def check_module(name: str | None, lineno: int) -> None:
        if not name or not name.startswith(pkg + "."):
            return
        # Strip package prefix; first segment is the layer dir.
        rest = name[len(pkg) + 1 :]
        first = rest.split(".", 1)[0]
        if first not in layers:
            return
        imported_level = layers[first]
        if imported_level > importer_level:
            violations.append((lineno, name, imported_level, importer_level))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                check_module(alias.name, node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                check_module(node.module, node.lineno)
            # Relative imports inside the package: resolve crudely against importer's dir.
            elif node.level > 0:
                rel = file.relative_to(src_root).parent.parts
                if node.level - 1 > len(rel):
                    continue
                base_parts = list(rel)
                if node.level > 1:
                    base_parts = base_parts[: -(node.level - 1)]
                base = ".".join(base_parts)
                module = node.module or ""
                full = pkg + ("." + base if base else "") + ("." + module if module else "")
                check_module(full, node.lineno)

    return violations


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="Path to src/<pkg>")
    ap.add_argument("--map", default=None, help="Comma-separated layer overrides")
    args = ap.parse_args(argv)

    src_root = Path(args.src).resolve()
    if not src_root.exists():
        print(f"src path not found: {src_root}", file=sys.stderr)
        return 2

    layers = parse_map(args.map) if args.map else dict(DEFAULT_MAP)
    pkg = package_name(src_root)

    files = sorted(src_root.rglob("*.py"))
    total_violations = 0
    for f in files:
        if "__pycache__" in f.parts:
            continue
        vs = check_file(f, src_root, pkg, layers)
        for lineno, mod, imported_level, importer_level in vs:
            rel = f.relative_to(src_root.parent.parent)
            print(
                f"[L{importer_level}] {rel}:{lineno} imports {mod} (L{imported_level})"
            )
            total_violations += 1

    real_files = [f for f in files if "__pycache__" not in f.parts]
    print(f"check-layering: {len(real_files)} files, {total_violations} violations.")
    return 0 if total_violations == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
