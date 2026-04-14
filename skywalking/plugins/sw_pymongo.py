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

import threading

from skywalking import Layer, Component, config
from skywalking.trace.context import get_context
from skywalking.trace.tags import TagDbType, TagDbInstance, TagDbStatement

try:
    from pymongo import monitoring
except ImportError:  # pragma: no cover - exercised in runtime environments with pymongo installed
    monitoring = None

    class _CommandListenerBase:
        pass
else:
    _CommandListenerBase = monitoring.CommandListener


link_vector = ['https://pymongo.readthedocs.io']
support_matrix = {
    'pymongo': {
        '>=3.10': ['4.16.*']
    }
}
note = """"""

_IGNORED_COMMANDS = {
    'hello',
    'ismaster',
}
_INSTALLED = False


class _PyMongoCommandListener(_CommandListenerBase):
    def __init__(self):
        self._active_spans = {}
        self._lock = threading.Lock()

    def started(self, event):
        command_name = event.command_name.lower()
        if command_name in _IGNORED_COMMANDS:
            return

        span = get_context().new_exit_span(
            op=f'MongoDB/{_operation_name(command_name)}',
            peer=_format_peer(event.connection_id),
            component=Component.MongoDB,
        )
        span.layer = Layer.Database
        span.tag(TagDbType('MongoDB'))
        span.tag(TagDbInstance(event.database_name))

        if config.plugin_pymongo_trace_parameters:
            span.tag(TagDbStatement(_truncate(_format_statement(command_name, event.command))))

        span.start()

        with self._lock:
            self._active_spans[_event_key(event)] = span

    def succeeded(self, event):
        self._finish(event)

    def failed(self, event):
        self._finish(event, failure=getattr(event, 'failure', None))

    def _finish(self, event, failure=None):
        with self._lock:
            span = self._active_spans.pop(_event_key(event), None)

        if span is None:
            return

        if failure is not None:
            span.log(Exception(str(failure)))

        span.stop()


_LISTENER = _PyMongoCommandListener()


def install():
    global _INSTALLED

    if _INSTALLED:
        return

    if monitoring is None:
        raise ImportError('pymongo.monitoring is unavailable')

    monitoring.register(_LISTENER)
    _INSTALLED = True


def _event_key(event):
    connection_id = getattr(event, 'connection_id', None)
    if isinstance(connection_id, list):
        connection_id = tuple(connection_id)

    return (
        threading.get_ident(),
        getattr(event, 'request_id', None),
        getattr(event, 'operation_id', None),
        connection_id,
    )


def _operation_name(command_name):
    return f'{command_name.capitalize()}Operation'


def _format_peer(connection_id):
    if isinstance(connection_id, (list, tuple)) and len(connection_id) >= 2:
        return f'{connection_id[0]}:{connection_id[1]}'

    return str(connection_id)


def _format_statement(command_name, command):
    if hasattr(command, 'to_dict'):
        command = command.to_dict()

    if isinstance(command, dict):
        command = dict(command)
        command.pop(command_name, None)

    return f'{command_name} {command}'


def _truncate(statement):
    max_len = config.plugin_pymongo_parameters_max_length
    return f'{statement[0:max_len]}...' if len(statement) > max_len else statement
