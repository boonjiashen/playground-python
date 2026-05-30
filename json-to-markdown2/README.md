# json-to-markdown2

A small, dependency-free Python tool that converts **nested** JSON documents
into readable Markdown. It's managed with the [uv](https://docs.astral.sh/uv/)
environment manager.

The sample data (`data.json`) models a school department: a list of teachers,
each with a `name`, `email`, and a nested list of `students` — and each student
in turn has a nested list of `grades`. Every item at a given level shares the
same shape, but the structure is genuinely nested rather than a single flat
dictionary.

## Run it

```bash
./convert.sh                       # data.json  -> data.md
./convert.sh input.json            # input.json -> input.md
./convert.sh input.json output.md  # explicit output path
```

`convert.sh` uses `uv run`, which transparently creates/syncs the project
environment defined in `pyproject.toml` and then runs the converter.

You can also invoke the script directly:

```bash
uv run python json_to_markdown.py data.json data.md
```

## How the conversion works

The converter (`json_to_markdown.py`) walks the JSON recursively:

- A list of objects whose values are all scalars (e.g. `grades`) becomes a
  Markdown **table**.
- A list of objects that contain further nesting (e.g. `teachers`, `students`)
  becomes a series of **headed sections**, labelled by each item's `name`.
- A dictionary's scalar fields become `**key:** value` bullet lines, and its
  complex fields recurse under sub-headings.
