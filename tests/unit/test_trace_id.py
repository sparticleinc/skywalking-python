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

import uuid

from skywalking.trace import ID


def test_generated_trace_id_is_random_uuid4_hex():
    trace_id = ID()

    assert len(trace_id.value) == 32
    assert uuid.UUID(hex=trace_id.value).version == 4


def test_supplied_trace_id_is_preserved():
    assert ID('upstream-trace-id').value == 'upstream-trace-id'
