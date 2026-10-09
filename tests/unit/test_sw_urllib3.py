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

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest
import urllib3
from urllib3._request_methods import RequestMethods

from skywalking.plugins import sw_urllib3
from skywalking.trace.context import agent


def test_install_instruments_urllib3_2_request_methods():
    original_request = RequestMethods.request

    try:
        sw_urllib3.install()

        assert RequestMethods.request is not original_request
    finally:
        RequestMethods.request = original_request


@pytest.fixture
def instrumented_http_endpoint(monkeypatch):
    received = []
    reported_segments = []
    monkeypatch.setattr(agent, 'is_segment_queue_full', lambda: False)
    monkeypatch.setattr(agent, 'archive_segment', reported_segments.append)

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 - stdlib HTTP handler callback
            received.append((self.rfile.read(int(self.headers['Content-Length'])), self.headers))
            self.send_response(202)
            self.end_headers()
            self.wfile.write(b'accepted')

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
    original_request = RequestMethods.request
    try:
        sw_urllib3.install()
        thread.start()
        base_url = 'http://127.0.0.1:'
        yield f'{base_url}{server.server_port}/echo', received
    finally:
        RequestMethods.request = original_request
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


@pytest.mark.parametrize('request_kind', ['positional_body', 'keyword_body', 'json', 'fields'])
def test_instrumented_requests_preserve_body_headers_and_response(
    instrumented_http_endpoint, request_kind
):
    url, received = instrumented_http_endpoint
    headers = {'X-Test': 'preserved'}
    with urllib3.PoolManager() as pool:
        if request_kind == 'positional_body':
            response = pool.request('POST', url, b'payload', headers=headers, timeout=2)
        elif request_kind == 'keyword_body':
            response = pool.request('POST', url, body=b'payload', headers=headers, timeout=2)
        elif request_kind == 'json':
            response = pool.request('POST', url, json={'value': 'payload'}, headers=headers, timeout=2)
        else:
            response = pool.request(
                'POST', url, fields={'value': 'payload'}, headers=headers,
                encode_multipart=False, timeout=2,
            )

    assert response.status == 202
    assert response.data == b'accepted'
    assert len(received) == 1
    body, sent_headers = received[0]
    if request_kind == 'json':
        assert json.loads(body) == {'value': 'payload'}
    elif request_kind == 'fields':
        assert body == b'value=payload'
    else:
        assert body == b'payload'
    assert sent_headers['X-Test'] == 'preserved'
    assert sent_headers['sw8']
