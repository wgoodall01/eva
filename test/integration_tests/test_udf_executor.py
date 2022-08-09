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
from test.util import (
    DummyObjectDetector,
    create_dummy_batches,
    create_sample_video,
    file_remove,
)

import numpy as np
import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.models.storage.batch import Batch
from eva.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


class UDFExecutorTest(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        create_sample_video(NUM_FRAMES)
        load_query = """LOAD DATA INFILE 'dummy.avi' INTO MyVideo;"""
        execute_query_fetch_all(load_query)

        create_udf_query = """CREATE UDF DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY UINT8(3, 256, 256))
                  OUTPUT (label NDARRAY STR(10))
                  TYPE  Classification
                  IMPL  'test/util.py';
        """
        execute_query_fetch_all(create_udf_query)

    def tearDown(self):
        file_remove("dummy.avi")

    # integration test

    def test_should_load_and_select_using_udf_video_in_table(self):
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        labels = DummyObjectDetector().labels
        expected = [
            {
                "myvideo.id": i,
                "dummyobjectdetector.label": np.array([labels[1 + i % 2]]),
            }
            for i in range(NUM_FRAMES)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_using_udf_video(self):
        # Equality test
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label = ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        expected = [
            {"myvideo.id": i * 2, "dummyobjectdetector.label": np.array(["person"])}
            for i in range(NUM_FRAMES // 2)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)

        # Contain test
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label @> ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        self.assertEqual(actual_batch, expected_batch)

        # Multi element contain test

        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label <@ ['person', 'bicycle'] \
            ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        expected = [
            {"myvideo.id": i * 2, "dummyobjectdetector.label": np.array(["person"])}
            for i in range(NUM_FRAMES // 2)
        ]
        expected += [
            {"myvideo.id": i, "dummyobjectdetector.label": np.array(["bicycle"])}
            for i in range(NUM_FRAMES)
            if i % 2 + 1 == 2
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        expected_batch.sort()
        self.assertEqual(actual_batch, expected_batch)

        nested_select_query = """SELECT id, data FROM
            (SELECT id, data, DummyObjectDetector(data) FROM MyVideo
                WHERE id >= 2
            ) AS T
            WHERE ['person'] <@ label;
            """
        actual_batch = execute_query_fetch_all(nested_select_query)
        actual_batch.sort()
        expected_batch = list(
            create_dummy_batches(
                filters=[i for i in range(2, NUM_FRAMES) if i % 2 == 0]
            )
        )[0]
        expected_batch.modify_column_alias("T")
        self.assertEqual(actual_batch, expected_batch)


    def test_aaudf_pull_up_rule(self):
        query = """SELECT id, DummyObjectDetector(data).label FROM MyVideo 
                    WHERE id < 5 
                    AND DummyObjectDetector(data).label = ['person']
                    AND DummyObjectDetector(data).label <@ ['person', 'bicycle'];"""
        actual_batch = execute_query_fetch_all(query)
        expected = [
            {"myvideo.id": i * 2, "dummyobjectdetector.label": np.array(["person"])}
            for i in range(3)
        ]
        print(actual_batch.frames)
        self.assertEqual(Batch(frames=pd.DataFrame(expected)), actual_batch)

    def test_single(self):
        select_query = "SELECT id,DummyObjectDetector(data) FROM MyVideo \
            WHERE DummyObjectDetector(data).label = ['person'] ORDER BY id;"
        actual_batch = execute_query_fetch_all(select_query)
        expected = [
            {"myvideo.id": i * 2, "dummyobjectdetector.label": np.array(["person"])}
            for i in range(NUM_FRAMES // 2)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected))
        self.assertEqual(actual_batch, expected_batch)


if __name__ == "__main__":
    unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(UDFExecutorTest("test_aaasingle"))
    runner = unittest.TextTestRunner()
    runner.run(suite)