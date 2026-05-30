"""Convert a JSON document into readable Markdown.

The converter is recursive so it copes with arbitrarily nested data, not just a
single flat dictionary. The heuristics are:

* A *list of objects that share the same shape* (same set of keys) whose values
  are all scalars is rendered as a Markdown table.
* Any other list of objects becomes a sequence of headed sections (so nested
  lists/objects can recurse cleanly), labelled by each item's name/title/id.
* A *dictionary* becomes ``key: value`` bullet lines for its scalar fields and
  nested headed sections for its complex fields.
* Scalars are rendered inline.

Run it via ``uv`` (see ``convert.sh``) or directly:

    python json_to_markdown.py data.json [output.md]
"""

from __future__ import annotations

import json
import sys
from typing import Any


def _is_scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _scalar_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _same_shape_scalar_columns(items: list[Any]) -> list[str] | None:
    """Return the ordered column names if ``items`` is a list of dicts that all
    share the same keys and whose values are all scalars, else ``None``."""
    if not items or not all(isinstance(item, dict) for item in items):
        return None
    columns = list(items[0].keys())
    key_set = set(columns)
    for item in items:
        if set(item.keys()) != key_set:
            return None
        if not all(_is_scalar(v) for v in item.values()):
            return None
    return columns


def _render_table(items: list[dict[str, Any]], columns: list[str]) -> list[str]:
    def escape(text: str) -> str:
        return text.replace("|", "\\|").replace("\n", " ")

    lines = ["| " + " | ".join(escape(c) for c in columns) + " |"]
    lines.append("| " + " | ".join("---" for _ in columns) + " |")
    for item in items:
        cells = [escape(_scalar_str(item.get(col))) for col in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def _render(value: Any, level: int, lines: list[str]) -> None:
    """Render ``value`` into ``lines``. ``level`` controls heading depth."""
    heading_prefix = "#" * min(level, 6)

    if isinstance(value, dict):
        scalar_items = {k: v for k, v in value.items() if _is_scalar(v)}
        complex_items = {k: v for k, v in value.items() if not _is_scalar(v)}

        for key, val in scalar_items.items():
            lines.append(f"- **{key}:** {_scalar_str(val)}")
        if scalar_items and complex_items:
            lines.append("")

        for key, val in complex_items.items():
            lines.append(f"{heading_prefix} {key}")
            lines.append("")
            _render(val, level + 1, lines)
            lines.append("")
        return

    if isinstance(value, list):
        columns = _same_shape_scalar_columns(value)
        if columns is not None:
            lines.extend(_render_table(value, columns))
            lines.append("")
            return

        for index, item in enumerate(value, start=1):
            if isinstance(item, dict):
                # Prefer a human label (name/title/id) if present.
                label = (
                    item.get("name")
                    or item.get("title")
                    or item.get("id")
                    or f"Item {index}"
                )
                lines.append(f"{heading_prefix} {label}")
                lines.append("")
                _render(item, level + 1, lines)
            elif _is_scalar(item):
                lines.append(f"- {_scalar_str(item)}")
            else:
                lines.append(f"{heading_prefix} Item {index}")
                lines.append("")
                _render(item, level + 1, lines)
            lines.append("")
        return

    lines.append(_scalar_str(value))


def convert(data: Any, title: str = "JSON Document") -> str:
    lines: list[str] = [f"# {title}", ""]
    _render(data, 2, lines)
    # Collapse runs of blank lines and trim trailing whitespace.
    out: list[str] = []
    for line in lines:
        if line == "" and out and out[-1] == "":
            continue
        out.append(line)
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv if argv is None else argv)
    if len(argv) < 2:
        print("usage: json_to_markdown.py <input.json> [output.md]", file=sys.stderr)
        return 2

    input_path = argv[1]
    with open(input_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    markdown = convert(data, title="Springfield High — Science Department")

    if len(argv) >= 3:
        with open(argv[2], "w", encoding="utf-8") as handle:
            handle.write(markdown)
        print(f"Wrote {argv[2]}")
    else:
        sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
