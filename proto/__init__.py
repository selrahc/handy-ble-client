# Copyright 2018 Espressif Systems (Shanghai) PTE LTD
# Modified 2021 Sweet Tech AS
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os


def _load_source(name, path):
    try:
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(name, path).load_module()
    except ImportError:
        # importlib.machinery doesn't exists in Python 2 so we will use imp (deprecated in Python 3)
        import imp
        return imp.load_source(name, path)


this_path = os.path.dirname(__file__)

# protocomm component related python files generated from .proto files
constants_pb2 = _load_source("constants_pb2", this_path + "/constants_pb2.py")
sec0_pb2 = _load_source("sec0_pb2",      this_path + "/sec0_pb2.py")
sec1_pb2 = _load_source("sec1_pb2",      this_path + "/sec1_pb2.py")
session_pb2 = _load_source("session_pb2",   this_path + "/session_pb2.py")
