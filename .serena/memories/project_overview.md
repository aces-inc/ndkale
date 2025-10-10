# Project Overview
- ndkale is a Python library providing a distributed task worker built on Amazon SQS with priority queue support.
- Primary modules live under `kale/` (task, worker, publisher, consumer, queue selector, message handling).
- Tests are located in `kale/tests/` using Python's `unittest`/nose-compatible structure.
- Docs (Sphinx) live under `docs/`. Example scripts live under `example/`.
- Python packaging managed via `pyproject.toml` (setuptools build backend) with Python >=3.9.