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
"""Fail unless a release tag (``v1.2.3``) matches ``tool.poetry.version`` in pyproject.toml.

Shared by the CircleCI release job and the manual GitHub Actions fallback, so a tag pushed on
the wrong commit can never publish a distribution under a different version.

Usage: python tools/check_tag_version.py <git-tag>
"""
import pathlib
import sys
import tomllib


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not argv[1]:
        print('usage: check_tag_version.py <git-tag>', file=sys.stderr)
        return 2
    git_tag = argv[1]
    project = tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))
    package_version = project['tool']['poetry']['version']
    expected_version = git_tag[1:] if git_tag.startswith('v') else git_tag
    if package_version != expected_version:
        print(f'Tag version {expected_version} does not match package version {package_version}.', file=sys.stderr)
        return 1
    print(f'Verified package version {package_version} for tag {git_tag}.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
