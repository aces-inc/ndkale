# Key Commands
- Install runtime deps: `uv pip install .`
- Install dev/test deps: `uv sync --group dev --extra test`
- Run full test suite: `KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest discover -s kale/tests -p "test_*.py" -v`
- Run specific tests: `KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest kale.tests.test_worker -v`
- Example ElasticMQ workflow (from `example/`): `./run_elasticmq.sh`, `./run_worker.sh`, `./run_publisher.sh 7`.