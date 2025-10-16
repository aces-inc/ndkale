# Style & Conventions
- Codebase is classic Python package; follow existing module patterns in `kale/` (snake_case modules, CamelCase classes).
- Tests use `unittest`-style cases under `kale/tests/`; maintain naming `test_*.py` and class-based `Test*` patterns.
- Version is dynamic via `kale/version/__version__`; avoid hardcoding version strings elsewhere.
- Packaging relies on setuptools via `pyproject.toml`; keep metadata consistent with README.
- README and docs use Markdown/Sphinx; keep badges and install instructions current.