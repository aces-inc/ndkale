"""Module for kale settings for unit tests."""

import os

QUEUE_CONFIG = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                            'test_queue_config.yaml')
QUEUE_CLASS = 'kale.tests.test_utils.TestQueueClass'
QUEUE_SELECTOR = 'kale.tests.test_utils.TestQueueSelector'