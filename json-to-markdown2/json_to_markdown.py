"""Convert a nested JSON document into a Markdown table.

There is intentionally **no hand-written conversion logic** here: pandas does
all the flattening (nested lists are exploded into rows, nested objects become
dotted columns) and ``DataFrame.to_markdown()`` (backed by ``tabulate``) does
all the Markdown rendering.

The only data-specific configuration lives in ``RECORD_PATH`` / ``META`` below.
For the sample ``data.json`` the shape is::

    teachers[]            -> name, email, students[]
        students[]        -> name, email, scores{}
            scores{}      -> midterm, final

``pd.json_normalize`` expands ``students`` into one row per student, carries the
parent ``teacher`` fields down via ``meta``, and flattens ``scores`` into
``student_scores.midterm`` / ``student_scores.final`` columns.

Usage:
    python json_to_markdown.py data.json [output.md]
"""

from __future__ import annotations

import json
import sys

import pandas as pd

# The top-level key holding the list of same-shape records.
TOP_LEVEL_LIST = "teachers"
# The nested list to expand into one row each (pandas explodes it for us).
RECORD_PATH = "students"
# Parent fields to carry down onto every exploded row.
META = ["name", "email"]
# Prefix for the exploded record's own columns, so they don't collide with META.
RECORD_PREFIX = "student_"


def to_markdown(data: dict) -> str:
    df = pd.json_normalize(
        data[TOP_LEVEL_LIST],
        record_path=RECORD_PATH,
        meta=META,
        record_prefix=RECORD_PREFIX,
    )
    return df.to_markdown(index=False) + "\n"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: json_to_markdown.py <input.json> [output.md]", file=sys.stderr)
        return 2

    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        data = json.load(handle)

    markdown = to_markdown(data)

    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as handle:
            handle.write(markdown)
        print(f"Wrote {sys.argv[2]}")
    else:
        sys.stdout.write(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
