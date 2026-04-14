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
from typing import Callable
import socket
import time

import pytest
import requests

from skywalking.plugins.sw_pymongo import support_matrix
from tests.orchestrator import get_test_vector
from tests.plugin.base import TestPluginBase


@pytest.fixture
def prepare():
    # type: () -> Callable
    def _wait_for_port(port, timeout=10):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection(('0.0.0.0', port), timeout=1):
                    return
            except OSError:
                time.sleep(0.2)

        raise TimeoutError(f'Port {port} did not become ready in time')

    def _prepare(*_):
        _wait_for_port(9090)
        _wait_for_port(9091)
        response = requests.get('http://0.0.0.0:9090/users', timeout=5)
        response.raise_for_status()
        return response

    return _prepare


class TestPlugin(TestPluginBase):
    @pytest.mark.parametrize('version', get_test_vector(lib_name='pymongo', support_matrix=support_matrix))
    def test_plugin(self, docker_compose, version):
        self.validate()
