# coding=utf-8
# Copyright 2018-2022 EVA
#
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
import unittest
from test.util import NUM_FRAMES, create_sample_video, file_remove, load_inbuilt_udfs

import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all


class StatFunctionsTests(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD FILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)
        load_inbuilt_udfs()

    def tearDown(self):
        file_remove("dummy.avi")

    def test_should_compute_avg(self):
        query = "SELECT avg(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        self.assertAlmostEqual(batch.frames.values[0][0], 4.5)

    def test_should_compute_min(self):
        query = "SELECT min(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 0)

    def test_should_compute_max(self):
        query = "SELECT max(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 9)

    def test_should_compute_count(self):
        query = "SELECT count(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 10)

    def test_should_compute_sum(self):
        query = "SELECT sum(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 45)
