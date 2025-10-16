# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ndkale** is a distributed task worker library from Nextdoor that supports priority queues on Amazon SQS. It enables publishing tasks to SQS queues and consuming them with worker processes that support priority-based queue selection algorithms.

## Core Architecture

### Key Components

1. **Task (`kale/task.py`)**: Base class for all tasks. Tasks define:
   - `run_task()`: The actual work to perform (must be implemented by subclasses)
   - `queue`: Which queue to publish to (e.g., 'default', 'high_priority', 'low_priority')
   - `max_retries`: Number of retry attempts on failure
   - `time_limit`: Hard limit for task execution time (must be less than queue visibility timeout)
   - `target_runtime`: Alert threshold for task performance monitoring
   - `publish()`: Class method to enqueue tasks to SQS

2. **Worker (`kale/worker.py`)**: Main worker process that:
   - Runs an infinite loop fetching and processing tasks
   - Uses queue selection algorithms to choose which queue to poll
   - Processes batches of tasks within visibility timeout windows
   - Handles task failures, retries, and dead-letter queues
   - Monitors memory usage and gracefully exits if limits exceeded

3. **Publisher (`kale/publisher.py`)**: Publishes tasks to SQS queues
   - Validates task time limits against queue visibility timeouts
   - Encodes messages using compression and encryption
   - Supports delayed task execution via `delay_sec`

4. **Consumer (`kale/consumer.py`)**: Fetches tasks from SQS
   - Retrieves message batches with configurable batch size
   - Supports long polling to reduce empty requests
   - Handles message deletion and visibility timeout changes

5. **Message (`kale/message.py`)**: Custom message format for SQS
   - Pickles, compresses (zlib), and encrypts task payloads
   - Tracks retry counts, failure counts, and timing metadata
   - Instantiates task objects from task class paths

6. **Queue Selector (`kale/queue_selector.py`)**: Algorithm to choose queues
   - **ReducedLottery** (recommended): Lottery-based selection that excludes known empty queues
   - Other algorithms: Random, Lottery, HighestPriorityFirst, HighestPriorityLottery, LotteryLottery

### Task Lifecycle

1. Publisher calls `MyTask.publish(app_data, *args, **kwargs)`
2. Task is serialized, compressed, encrypted and sent to SQS queue
3. Worker's queue selector chooses a queue based on priority and emptiness
4. Consumer fetches a batch of messages (up to `batch_size`)
5. Worker processes tasks sequentially within the batch
6. For each task:
   - Check if time limit fits within remaining visibility timeout
   - Execute task with timeout protection
   - On success: delete from queue
   - On failure: republish with exponential backoff (if retries remain)
   - On permanent failure: send to dead-letter queue
7. Release incomplete tasks back to queue if visibility timeout approaching

### Configuration System

Settings are loaded in order (later overrides earlier):
1. `kale/default_settings.py` - Default configuration
2. Module specified by `KALE_SETTINGS_MODULE` environment variable

**Key Settings:**
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` - AWS credentials
- `MESSAGE_QUEUE_USE_PROXY`, `MESSAGE_QUEUE_PROXY_HOST`, `MESSAGE_QUEUE_PROXY_PORT` - For local ElasticMQ development
- `QUEUE_CONFIG` - Path to YAML file defining queues
- `QUEUE_SELECTOR` - Class path for queue selection algorithm
- `SQS_TASK_SIZE_LIMIT` - Maximum message size (default: 256KB)
- `DIE_ON_RESIDENT_SET_SIZE_MB` - Memory limit for worker process
- `USE_DEAD_LETTER_QUEUE`, `ENABLE_DEAD_LETTER_QUEUE` - Dead-letter queue configuration
- `ON_WORKER_STARTUP`, `ON_WORKER_SHUTDOWN` - Hooks for worker lifecycle

**Queue Config YAML:**
Each queue defines:
- `name`: Queue identifier
- `priority`: 1-100 (higher = more frequently selected)
- `batch_size`: Number of messages to fetch per iteration
- `visibility_timeout_sec`: Time budget for processing a batch
- `long_poll_time_sec`: Wait time when queue is empty
- `num_iterations`: Max iterations per queue selection

**Task SLA calculation:** `visibility_timeout_sec / batch_size` = seconds per task

## Development Commands

### Environment Setup
```bash
# Install from source
uv pip install .

# Install with test dependencies
uv sync --group dev --extra test
```

### Running Tests
```bash
# Run all tests
KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest discover -s kale/tests -p "test_*.py" -v

# Run specific test file
KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest kale.tests.test_worker -v

# Run specific test class
KALE_SETTINGS_MODULE=kale.tests.test_settings uv run python -m unittest kale.tests.test_task.TestTask -v
```

### Continuous Integration
- GitHub Actions workflow `.github/workflows/ci.yml` runs on every push (and PR) with Python 3.9, 3.10, 3.11, and 3.12.
- Workflow steps: install the package with test extras and execute the unit test suite with `KALE_SETTINGS_MODULE=kale.tests.test_settings`.

### Local Development with ElasticMQ

ElasticMQ emulates SQS locally for development. See `example/` directory:

```bash
# Start ElasticMQ container
cd example
./run_elasticmq.sh

# Run worker process (in another terminal)
./run_worker.sh

# Publish a test task
./run_publisher.sh 7
```

## Implementation Patterns

### Creating a Task

```python
from kale import task

class MyTask(task.Task):
    max_retries = 3
    time_limit = 5  # seconds
    queue = 'default'

    def run_task(self, arg1, arg2, *args, **kwargs):
        # Perform work here
        pass
```

### Publishing a Task

```python
import tasks

# First argument is app_data (can be None)
# Remaining args/kwargs match run_task signature
task_id = tasks.MyTask.publish(None, arg1, arg2)

# Publish with delay
task_id = tasks.MyTask.publish(None, arg1, arg2, delay_sec=60)
```

### Extending Worker or Task

To use `app_data` or add custom behavior:

```python
class CustomTask(task.Task):
    def __init__(self, message_body=None, *args, **kwargs):
        super().__init__(message_body, *args, **kwargs)
        # self.app_data is now available

    def _setup_task_environment(self):
        # Setup before task runs (e.g., database connections)
        pass

    def _clean_task_environment(self, task_id=None, task_name=None, exc=None):
        # Cleanup after task (exc is None on success)
        pass

    def _alert_runtime_exceeded(self):
        # Called when task exceeds target_runtime
        pass

    def _kill_runtime_exceeded(self):
        # Called when task times out
        pass

class CustomWorker(worker.Worker):
    def _on_task_succeeded(self, message, time_remaining_sec):
        # Custom success handling
        pass

    def _on_task_failed(self, message, time_remaining_sec, err, permanent_failure):
        # Custom failure handling
        pass
```

## Important Constraints

1. **Task time_limit must be less than queue visibility_timeout_sec** - Publisher will raise `InvalidTimeLimitTaskException` if violated
2. **Message size limit is 256KB by default** - Large payloads raise `ChubbyTaskException`
3. **Max delay is 900 seconds (15 minutes)** - SQS limitation
4. **Tasks must be pickleable** - All arguments and task state must serialize
5. **Queue priorities are 1-100** - Outside this range may cause selection issues
6. **Worker memory monitoring** - Workers exit gracefully at `DIE_ON_RESIDENT_SET_SIZE_MB`

## Package Management

This project uses **uv** for package management. The migration from setuptools to uv-based workflow was completed in commit `75a1a98`.

**Configuration in `pyproject.toml`:**
- Build system: `setuptools>=64` with `setuptools.build_meta` backend
- Main dependencies in `[project.dependencies]`
- Test dependencies in both `[project.optional-dependencies]` (for pip compatibility) and `[dependency-groups]` (for uv)
- Version is dynamically read from `kale/version/__version__` (current: 2.2.4)
- Python support: >=3.9 (tested with Python 3.9 through 3.12)

**Key dependencies:**
- `boto3>=1.10.36` - AWS SDK for SQS operations
- `pycryptodome>=3.6.6` - Message encryption
- `pyyaml>=5.2` - Queue configuration parsing
- Python 3専用化に伴い `six` や `future` といった互換ライブラリは不要
- `future>=0.18.2` - Python 2/3 compatibility

**Installation methods:**
```bash
# Install from local source
uv pip install .

# Install from GitHub (latest)
uv pip install git+https://github.com/Nextdoor/ndkale.git#egg=ndkale

# Install from GitHub (specific commit)
uv pip install git+https://github.com/Nextdoor/ndkale.git@<commit-hash>#egg=ndkale

# Install with development and test dependencies
uv sync --group dev --extra test
```
