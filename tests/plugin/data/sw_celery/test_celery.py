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

import pytest
import requests

from skywalking.plugins.sw_celery import support_matrix
from tests.orchestrator import get_test_vector
from tests.plugin.base import TestPluginBase


def get_celery_test_vector():
    return [
        version.replace('celery==', 'celery[redis]==', 1)
        for version in get_test_vector(lib_name='celery', support_matrix=support_matrix)
    ]


@pytest.fixture
def prepare():
    # type: () -> Callable
    return lambda *_: requests.get('http://0.0.0.0:9090/users', timeout=20)


class TestPlugin(TestPluginBase):
    @pytest.mark.parametrize('version', get_celery_test_vector())
    def test_plugin(self, docker_compose, version):
        self.validate()
