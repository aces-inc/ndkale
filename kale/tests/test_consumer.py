"""Module testing the kale.consumer module."""
from __future__ import absolute_import

import unittest

from moto import mock_aws

from kale import consumer
from kale import settings
from kale import sqs


class ConsumerTestCase(unittest.TestCase):
    """Test consumer logic."""

    _previous_region = None

    def setUp(self):
        self.mock_aws = mock_aws()
        self.mock_aws.start()
        sqs.SQSTalk._queues = {}

    def tearDown(self):
        self.mock_aws.stop()

    def test_fetch_batch(self):
        c = consumer.Consumer()

        # Use actual queue name from test_queue_config.yaml
        queue_name = 'default'
        self.assertIsNotNone(c.fetch_batch(
            queue_name, 10, 60))
        self.assertIsNotNone(c.fetch_batch(
            queue_name, 10, 60, 2))
