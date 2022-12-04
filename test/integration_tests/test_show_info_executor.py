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

import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.server.command_handler import execute_query_fetch_all
from eva.udfs.udf_bootstrap_queries import EVA_INSTALLATION_DIR

NUM_FRAMES = 10


bootstrap_queries = [
    f"""
    CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
    INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
    OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
    scores NDARRAY FLOAT32(ANYDIM))
    TYPE  Classification
    IMPL '{EVA_INSTALLATION_DIR}/udfs/fastrcnn_object_detector.py';
    """,
    f"""
    CREATE UDF IF NOT EXISTS Array_Count
    INPUT (Input_Array NDARRAY ANYTYPE, Search_Key ANYTYPE)
    OUTPUT (key_count INTEGER)
    TYPE NdarrayUDF
    IMPL "{EVA_INSTALLATION_DIR}/udfs/ndarray/array_count.py";
    """,
]


class ShowExecutorTest(unittest.TestCase):
    def setUp(self):
        CatalogManager().reset()
        for query in bootstrap_queries:
            execute_query_fetch_all(query)

    # integration test
    def test_show_udfs(self):
        result = execute_query_fetch_all("SHOW UDFS;")
        self.assertEqual(len(result.columns), 5)

        expected = {
            "name": ["FastRCNNObjectDetector", "Array_Count"],
            "inputs": [
                ["Frame_Array NDARRAY UINT8 [3, None, None]"],
                ["Input_Array NDARRAY ANYTYPE []", "Search_Key ANY"],
            ],
            "outputs": [
                [
                    "labels NDARRAY STR [None]",
                    "bboxes NDARRAY FLOAT32 [None, 4]",
                    "scores NDARRAY FLOAT32 [None]",
                ],
                ["key_count INTEGER"],
            ],
            "type": ["Classification", "NdarrayUDF"],
        }
        expected_df = pd.DataFrame(expected)
        self.assertTrue(all(expected_df.inputs == result.frames.inputs))
        self.assertTrue(all(expected_df.outputs == result.frames.outputs))
        self.assertTrue(all(expected_df.name == result.frames.name))
        self.assertTrue(all(expected_df.type == result.frames.type))
