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

from eva.configuration.configuration_manager import ConfigurationManager
from eva.server.command_handler import execute_query_fetch_all

EVA_INSTALLATION_DIR = ConfigurationManager().get_value("core", "eva_installation_dir")
NDARRAY_DIR = "ndarray"

DummyObjectDetector_udf_query = """CREATE UDF IF NOT EXISTS DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (label NDARRAY STR(1))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EVA_INSTALLATION_DIR
)

DummyMultiObjectDetector_udf_query = """CREATE UDF
                  IF NOT EXISTS  DummyMultiObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(2))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EVA_INSTALLATION_DIR
)

ArrayCount_udf_query = """CREATE UDF
            IF NOT EXISTS  Array_Count
            INPUT (Input_Array NDARRAY ANYTYPE, Search_Key ANYTYPE)
            OUTPUT (key_count INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/array_count.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

StatStdev_udf_query = """CREATE UDF
            IF NOT EXISTS  Stat_Stdev
            INPUT (Input_Array NDARRAY ANYTYPE)
            OUTPUT (result_stdev INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/stat_stdev.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

StatMean_udf_query = """CREATE UDF
            IF NOT EXISTS  Stat_Mean
            INPUT (Input_Array NDARRAY ANYTYPE)
            OUTPUT (result_mean INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/stat_mean.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

StatStdevSample_udf_query = """CREATE UDF
            IF NOT EXISTS  Stat_Stdev_Sample
            INPUT (Input_Array NDARRAY ANYTYPE)
            OUTPUT (result_stdev INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/stat_stdev_sample.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

StatCorrelation_udf_query = """CREATE UDF
            IF NOT EXISTS  Stat_Correlation
            INPUT (Input_X NDARRAY ANYTYPE, Input_Y NDARRAY ANYTYPE)
            OUTPUT (result_correlation INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/stat_correlation.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

StatCovariance_udf_query = """CREATE UDF
            IF NOT EXISTS  Stat_Covariance
            INPUT (Input_X NDARRAY ANYTYPE, Input_Y NDARRAY ANYTYPE)
            OUTPUT (result_covariance INTEGER)
            TYPE NdarrayUDF
            IMPL "{}/udfs/{}/stat_covariance.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Crop_udf_query = """CREATE UDF IF NOT EXISTS Crop
                INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM),
                        bboxes NDARRAY FLOAT32(ANYDIM, 4))
                OUTPUT (Cropped_Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/crop.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Unnest_udf_query = """CREATE UDF IF NOT EXISTS Unnest
                INPUT  (inp NDARRAY ANYTYPE)
                OUTPUT (out ANYTYPE)
                TYPE  NdarrayUDF
                IMPL  "{}/udfs/{}/unnest.py";
        """.format(
    EVA_INSTALLATION_DIR, NDARRAY_DIR
)

Fastrcnn_udf_query = """CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
      INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
      OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                scores NDARRAY FLOAT32(ANYDIM))
      TYPE  Classification
      IMPL  '{}/udfs/fastrcnn_object_detector.py';
      """.format(
    EVA_INSTALLATION_DIR
)


def init_builtin_udfs(mode="debug"):
    """
    Loads the builtin udfs into the system.
    This should be called when the system bootstraps.
    In debug mode, it also loads udfs used in the test suite.
    Arguments:
        mode (str): 'debug' or 'release'
    """
    queries = [
        ArrayCount_udf_query,
        Crop_udf_query,
        DummyMultiObjectDetector_udf_query,
        DummyObjectDetector_udf_query,
        Fastrcnn_udf_query,
        StatCorrelation_udf_query,
        StatCovariance_udf_query,
        StatStdevSample_udf_query,
        StatStdev_udf_query,
        StatMean_udf_query,
    ]

    for query in queries:
        execute_query_fetch_all(query)
