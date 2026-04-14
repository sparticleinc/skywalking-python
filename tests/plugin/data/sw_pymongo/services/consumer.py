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

import socket
import time

import requests


def _wait_for_provider(timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(('provider', 9091), timeout=1):
                return
        except OSError:
            time.sleep(0.2)

    raise TimeoutError('provider:9091 did not become reachable in time')


if __name__ == '__main__':
    from flask import Flask, jsonify

    app = Flask(__name__)

    @app.route('/users', methods=['POST', 'GET'])
    def application():
        _wait_for_provider()
        requests.get('http://provider:9091/insert_many', timeout=5).raise_for_status()
        requests.get('http://provider:9091/find_one', timeout=5).raise_for_status()
        res = requests.get('http://provider:9091/delete_one', timeout=5)
        res.raise_for_status()
        return jsonify(res.json())

    PORT = 9090
    app.run(host='0.0.0.0', port=PORT, debug=False)
