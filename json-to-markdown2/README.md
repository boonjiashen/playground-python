# json-to-markdown2

Converts **nested** JSON into a Markdown table — using existing, maintained
libraries so there's **no conversion code to maintain**:

- [**pandas**](https://pandas.pydata.org/) `json_normalize` does all the
  flattening (nested lists are exploded into rows, nested objects become dotted
  columns).
- [**tabulate**](https://pypi.org/project/tabulate/) (via
  `DataFrame.to_markdown()`) does all the Markdown rendering.

The whole project is managed with the [uv](https://docs.astral.sh/uv/)
environment manager.

The sample `data.json` models a school department: a list of teachers, each
with a `name`, `email`, and a nested list of `students`; each student has a
`name`, `email`, and a nested `scores` object. Every item at a given level
shares the same shape.

## Run it

```bash
./convert.sh                       # data.json  -> data.md
./convert.sh input.json            # input.json -> input.md
./convert.sh input.json output.md  # explicit output path
```

`convert.sh` uses `uv run`, which transparently creates/syncs the project
environment (installing pandas + tabulate from `pyproject.toml`) and then runs
the converter. You can also call it directly:

```bash
uv run python json_to_markdown.py data.json data.md
```

## Adapting it to your own data

There is no parsing logic to edit — only a few field names at the top of
`json_to_markdown.py`:

| Setting | Meaning |
|---------|---------|
| `TOP_LEVEL_LIST` | The key holding the list of records (`"teachers"`). |
| `RECORD_PATH` | The nested list to expand into one row each (`"students"`). |
| `META` | Parent fields to carry down onto every row (`["name", "email"]`). |
| `RECORD_PREFIX` | Prefix for the expanded record's columns so they don't collide with `META`. |

pandas supports deeper nesting too — e.g. `record_path=["students", "grades"]`
to expand a list-within-a-list. See the
[`json_normalize` docs](https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html).
