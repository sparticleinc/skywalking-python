#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest
from types import SimpleNamespace
from unittest import mock

from skywalking.plugins import sw_pymongo


class FakeSpan:
    def __init__(self, op, peer, component):
        self.op = op
        self.peer = peer
        self.component = component
        self.layer = None
        self.started = False
        self.stopped = False
        self.tags = []
        self.logged = []

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def tag(self, tag):
        self.tags.append(tag)
        return self

    def log(self, ex):
        self.logged.append(str(ex))
        return self


class FakeContext:
    def __init__(self):
        self.spans = []

    def new_exit_span(self, op, peer, component):
        span = FakeSpan(op, peer, component)
        self.spans.append(span)
        return span


class TestPyMongoCommandListener(unittest.TestCase):
    def test_started_and_succeeded_wrap_supported_commands(self):
        listener = sw_pymongo._PyMongoCommandListener()
        context = FakeContext()

        started = SimpleNamespace(
            command_name='find',
            database_name='test-database',
            request_id=1,
            operation_id=2,
            connection_id=('mongo', 27017),
            command={'find': 'users', 'filter': {'name': 'alice'}, '$db': 'test-database'},
        )
        finished = SimpleNamespace(
            request_id=1,
            operation_id=2,
            connection_id=('mongo', 27017),
        )

        with mock.patch('skywalking.plugins.sw_pymongo.get_context', return_value=context), \
                mock.patch.object(sw_pymongo.config, 'plugin_pymongo_trace_parameters', True), \
                mock.patch.object(sw_pymongo.config, 'plugin_pymongo_parameters_max_length', 512):
            listener.started(started)

            self.assertEqual(len(context.spans), 1)
            span = context.spans[0]
            self.assertTrue(span.started)
            self.assertEqual(span.op, 'MongoDB/FindOperation')
            self.assertEqual(span.peer, 'mongo:27017')

            tags = {tag.key: tag.val for tag in span.tags}
            self.assertEqual(tags['db.type'], 'MongoDB')
            self.assertEqual(tags['db.instance'], 'test-database')
            self.assertIn('find', tags['db.statement'])

            listener.succeeded(finished)

            self.assertTrue(span.stopped)
            self.assertEqual(listener._active_spans, {})

    def test_started_ignores_topology_commands(self):
        listener = sw_pymongo._PyMongoCommandListener()
        context = FakeContext()

        with mock.patch('skywalking.plugins.sw_pymongo.get_context', return_value=context):
            listener.started(SimpleNamespace(
                command_name='hello',
                database_name='admin',
                request_id=1,
                operation_id=2,
                connection_id=('mongo', 27017),
                command={'hello': 1},
            ))

        self.assertEqual(context.spans, [])
        self.assertEqual(listener._active_spans, {})

    def test_failed_command_logs_error_and_clears_active_span(self):
        listener = sw_pymongo._PyMongoCommandListener()
        context = FakeContext()

        started = SimpleNamespace(
            command_name='delete',
            database_name='test-database',
            request_id=3,
            operation_id=4,
            connection_id=('mongo', 27017),
            command={'delete': 'users', 'deletes': [{'q': {'name': 'alice'}, 'limit': 1}]},
        )
        failed = SimpleNamespace(
            request_id=3,
            operation_id=4,
            connection_id=('mongo', 27017),
            failure={'errmsg': 'boom'},
        )

        with mock.patch('skywalking.plugins.sw_pymongo.get_context', return_value=context):
            listener.started(started)
            span = context.spans[0]

            listener.failed(failed)

            self.assertTrue(span.stopped)
            self.assertEqual(len(span.logged), 1)
            self.assertIn('boom', span.logged[0])
            self.assertEqual(listener._active_spans, {})


if __name__ == '__main__':
    unittest.main()
