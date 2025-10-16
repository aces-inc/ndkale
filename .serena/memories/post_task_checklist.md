# Post-Task Checklist
- Run unit tests with `KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest discover -s kale/tests -p "test_*.py" -v` when Python code changes.
- Update README/docs (`README.md`, `docs/`) if CLI usage, install steps, or badges change.
- Ensure packaging metadata in `pyproject.toml` stays in sync with documentation.
- Verify example scripts still operate if worker/publisher interfaces are touched.