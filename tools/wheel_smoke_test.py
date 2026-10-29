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
"""Smoke test for a built distribution, run against the *installed* wheel (`make wheel-smoke`).

Tests on the source tree cannot see packaging defects: 1.0.6 and 1.0.7 were published without
`skywalking/protocol`, so `import skywalking.decorators` raised ModuleNotFoundError for every
user while the repository itself looked fine.
"""
import asyncio
import sys

import google.protobuf
import skywalking

if 'site-packages' not in skywalking.__file__:
    sys.exit(f'Imported skywalking from {skywalking.__file__}, not from an installed wheel - '
             'run this from outside the source tree.')

# The imports applications do at module level, plus the generated modules the agent loads.
from skywalking import agent, config  # noqa: E402,F401
# agent.start() imports this for the default `grpc` reporter; it loads skywalking.client.grpc
# and the *_pb2_grpc stubs, whose GRPC_GENERATED_VERSION check runs against the grpcio floor.
import skywalking.agent.protocol.grpc  # noqa: E402,F401
from skywalking.agent import agent as sw_agent  # noqa: E402
from skywalking.decorators import trace  # noqa: E402
from skywalking.protocol.common.Command_pb2 import Commands  # noqa: E402,F401
from skywalking.protocol.language_agent.Meter_pb2 import MeterData  # noqa: E402,F401
from skywalking.protocol.logging.Logging_pb2 import LogData  # noqa: E402,F401


@trace()
def sync_traced(x):
    return x * 2


@trace()
async def async_traced(x):
    return x + 1


assert not sw_agent.is_started()
assert sync_traced(21) == 42
assert asyncio.run(async_traced(41)) == 42

print(f'wheel smoke test OK: python {sys.version.split()[0]}, protobuf {google.protobuf.__version__}')
