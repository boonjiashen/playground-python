#!/usr/bin/env bash
#
# Convert a JSON file into Markdown using uv to manage the Python environment.
#
# Usage:
#   ./convert.sh                       # data.json -> data.md
#   ./convert.sh input.json            # input.json -> input.md
#   ./convert.sh input.json output.md  # explicit output path
#
set -euo pipefail

# Run from the directory this script lives in so relative paths work.
cd "$(dirname "$0")"

INPUT="${1:-data.json}"
OUTPUT="${2:-${INPUT%.json}.md}"

# `uv run` resolves the project environment (pyproject.toml) and executes the
# converter without you having to create/activate a virtualenv yourself.
uv run python json_to_markdown.py "$INPUT" "$OUTPUT"
