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
import glob
import os
import re
import shutil
import sys
from importlib import metadata
from pathlib import Path

from grpc_tools import protoc
from packaging import version

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

grpc_tools_version = metadata.version('grpcio-tools')
dest_dir = 'skywalking/protocol'
src_dir = 'protocol'
pyproject = Path(__file__).resolve().parents[1] / 'pyproject.toml'

protobuf_gencode_version = re.compile(r'^# Protobuf Python Version: (\S+)$', re.MULTILINE)
grpc_gencode_version = re.compile(r"^GRPC_GENERATED_VERSION = '([^']+)'$", re.MULTILINE)


def touch(filename):
    open(filename, 'a').close()


def dependency_floor(name):
    spec = re.search(rf'^{re.escape(name)}\s*=\s*"[^"]*>=\s*([0-9][0-9.]*)',
                     pyproject.read_text(encoding='utf-8'), re.MULTILINE)
    if spec is None:
        sys.exit(f'Cannot find the {name} lower bound in pyproject.toml')
    return version.parse(spec.group(1))


def check_generated_versions(pattern, recorded_version, dependency):
    """Generated code refuses to load on a runtime older than the one it was generated for
    (protobuf checks the `Protobuf Python Version` header, the *_pb2_grpc stubs check
    GRPC_GENERATED_VERSION), so code generated for a newer runtime than the floor in
    pyproject.toml breaks `import skywalking` for anyone sitting on that floor."""
    floor = dependency_floor(dependency)

    found = set()
    for generated in glob.iglob(os.path.join(dest_dir, '**', pattern), recursive=True):
        recorded = recorded_version.search(Path(generated).read_text(encoding='utf-8'))
        if recorded is None:
            sys.exit(f'{generated} does not record the {dependency} version it targets, cannot verify it')
        found.add(recorded.group(1))

    too_new = sorted(v for v in found if version.parse(v) > floor)
    if too_new:
        sys.exit(f'grpcio-tools {grpc_tools_version} generated code for {dependency} {", ".join(too_new)}, '
                 f'newer than the {dependency}>={floor} floor in pyproject.toml. '
                 f'Pin an older grpcio-tools (GRPC_TOOLS_VERSION in the Makefile).')


def codegen():
    protos = list(glob.iglob(f'{src_dir}/**/*.proto', recursive=True))
    if not protos:
        sys.exit(f'No .proto sources under ./{src_dir}: run "git submodule update --init" first.')

    # The whole directory is generated (and git-ignored); start clean so stale files from an
    # earlier run with another grpcio-tools version never end up in the package.
    shutil.rmtree(dest_dir, ignore_errors=True)
    os.mkdir(dest_dir)

    touch(os.path.join(dest_dir, '__init__.py'))
    protoc_args = [
        'grpc_tools.protoc',
        f'--proto_path={src_dir}',
        f'--python_out={dest_dir}',
        f'--grpc_python_out={dest_dir}'
    ]
    if version.parse(grpc_tools_version) >= version.parse('1.49.0'):
        # https://github.com/grpc/grpc/issues/31247
        protoc_args += [f'--pyi_out={dest_dir}']
    protoc_args += protos
    if protoc.main(protoc_args) != 0:
        sys.exit('grpc_tools.protoc failed')

    for py_file in glob.iglob(os.path.join(dest_dir, '**/*.py'), recursive=True):
        touch(os.path.join(os.path.dirname(py_file), '__init__.py'))
        with open(py_file, 'r+') as file:
            code = file.read()
            file.seek(0)
            file.write(re.sub(r'from ((?!\.).+) (import .+_pb2.*)', 'from ..\\1 \\2', code))
            file.truncate()

    check_generated_versions('*_pb2.py', protobuf_gencode_version, 'protobuf')
    check_generated_versions('*_pb2_grpc.py', grpc_gencode_version, 'grpcio')


if __name__ == '__main__':
    codegen()
