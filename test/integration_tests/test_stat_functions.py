# coding=utf-8
# Copyright 2018-2022 EVA
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

    def test_should_compute_mean(self):
        query = "SELECT Stat_Mean(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        self.assertAlmostEqual(batch.frames.values[0][0], 4.5)

    def test_should_compute_geometric_mean(self):
        query = "SELECT Stat_Geometric_Mean(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        self.assertAlmostEqual(batch.frames.values[0][0], 0)

    def test_should_compute_harmonic_mean(self):
        query = "SELECT Stat_Harmonic_Mean(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        self.assertAlmostEqual(batch.frames.values[0][0], 0)

    def test_should_compute_stdev(self):
        query = "SELECT Stat_Stdev(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        self.assertAlmostEqual(batch.frames.values[0][0], 2.8722813232690143)

    def test_should_compute_stdev_samp(self):
        query = "SELECT Stat_Stdev_Sample(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        self.assertAlmostEqual(batch.frames.values[0][0], 3.0276503540974917)

    def test_should_compute_correlation(self):
        query = "SELECT Stat_Correlation(id, id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 1)

    def test_should_compute_covariance(self):
        query = "SELECT Stat_Covariance(id, id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 9.166666666666666)

    def test_should_compute_min(self):
        query = "SELECT Stat_Min(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 0)

    def test_should_compute_max(self):
        query = "SELECT Stat_Max(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 9)

    def test_should_compute_count(self):
        query = "SELECT Stat_Count(id) FROM MyVideo;"
        batch = execute_query_fetch_all(query)
        print(batch)
        self.assertAlmostEqual(batch.frames.values[0][0], 10)
