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

import logging

from skywalking import config

logger_debug_enabled = False


def getLogger(name=None):  # noqa
    logger = logging.getLogger(name)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s [pid:%(process)d] [%(threadName)s] [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False

    return logger


logger = getLogger('skywalking')


def init():
    global logger_debug_enabled
    logging.addLevelName(logging.CRITICAL + 10, 'OFF')
    logger.setLevel(logging.getLevelName(config.agent_logging_level))
    logger_debug_enabled = logger.isEnabledFor(logging.DEBUG)
