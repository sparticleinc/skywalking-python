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
"""``plugins.install()`` must load every plugin module on all supported Python versions.

1.0.8 loaded plugins with ``importer.find_module(modname).load_module(modname)``. Python 3.12
removed ``find_module`` from import finders, so ``agent.start()`` -> ``plugins.install()``
raised ``AttributeError: 'FileFinder' object has no attribute 'find_module'`` and an
application that enables the agent failed at startup.

Runs in a subprocess: installing plugins patches libraries process-wide.
"""
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

_SCRIPT = """
import logging
import skywalking.plugins as plugins
from skywalking import config
from skywalking.loggings import logger

config.init(agent_collector_backend_services='127.0.0.1:1', agent_name='plugins-install-test')
seen = []

class Collect(logging.Handler):
    def emit(self, record):
        seen.append(record.getMessage())

logger.addHandler(Collect())
logger.setLevel(logging.DEBUG)
plugins.install()
installing = [m for m in seen if m.startswith('installing plugin ')]
print(len(installing))
"""


class TestPluginsInstall(unittest.TestCase):
    def test_install_loads_every_plugin_module(self):
        proc = subprocess.run([sys.executable, '-c', _SCRIPT], cwd=ROOT, capture_output=True,
                              text=True, timeout=300)
        self.assertEqual(proc.returncode, 0, proc.stderr[-3000:])
        expected = sum(1 for p in (ROOT / 'skywalking' / 'plugins').glob('sw_*.py'))
        self.assertGreater(expected, 0)
        self.assertEqual(int(proc.stdout.strip().splitlines()[-1]), expected)


if __name__ == '__main__':
    unittest.main()
