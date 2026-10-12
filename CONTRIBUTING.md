# Contributing

Follow the [README](README.md) to install dependencies with `uv sync --locked`
and run the example locally.

Keep changes focused on making the durable-actors example easier to understand
and run. For runtime or SDK bugs, use the
[durable-actors repository](https://github.com/TerseAI/durable-actors).

Before opening a pull request, run:

```sh
uv run ruff check .
uv run ruff format --check .
```

After changing actor methods or socket types, regenerate and commit the clients:

```sh
uv run durable-actors generate src/actors.py --out-dir generated
```

Do not edit `generated/` by hand. When changing dependencies, run `uv lock` and
commit both `pyproject.toml` and `uv.lock`. Keep credentials, logs, and local chat
data out of commits and issue reports.
