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

import asyncio
import unittest

from skywalking.agent import agent
from skywalking.decorators import trace


class TestTraceWhenAgentNotStarted(unittest.TestCase):
    """@trace must be a transparent pass-through while the agent is not started.

    1.0.7 read the name-mangled private attribute `agent.__started` from outside the class on
    the sync path, so every call to a sync @trace function raised AttributeError.
    """

    def test_agent_is_not_started(self):
        self.assertFalse(agent.is_started())

    def test_sync_function_returns_its_value(self):
        @trace()
        def double(x):
            return x * 2

        self.assertEqual(42, double(21))

    def test_sync_function_exception_propagates_unchanged(self):
        @trace()
        def boom():
            raise ValueError('boom')

        with self.assertRaises(ValueError):
            boom()

    def test_async_function_returns_its_value(self):
        @trace()
        async def increment(x):
            return x + 1

        self.assertEqual(42, asyncio.run(increment(41)))

    def test_wrapped_function_keeps_its_name(self):
        @trace()
        def named():
            pass

        self.assertEqual('named', named.__name__)


if __name__ == '__main__':
    unittest.main()
