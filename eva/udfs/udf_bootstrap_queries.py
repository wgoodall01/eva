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

queries = []

queries.append(
    f"""
    CREATE UDF IF NOT EXISTS DummyObjectDetector
    INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
    OUTPUT (label NDARRAY STR(1))
    TYPE  Classification
    IMPL  '{EVA_INSTALLATION_DIR}/../test/util.py';
    """
)

queries.append(
    f"""
    CREATE UDF IF NOT EXISTS DummyMultiObjectDetector
    INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
    OUTPUT (labels NDARRAY STR(2))
    TYPE  Classification
    IMPL  '{EVA_INSTALLATION_DIR}/../test/util.py';
    """
)

queries.append(
    f"""
    CREATE UDF IF NOT EXISTS Array_Count
    INPUT (Input_Array NDARRAY ANYTYPE, Search_Key ANYTYPE)
    OUTPUT (key_count INTEGER)
    TYPE NdarrayUDF
    IMPL "{EVA_INSTALLATION_DIR}/udfs/ndarray/array_count.py";
    """
)


# Add the builtin SQL aggregations.
for aggregation_name in ["min", "max", "count", "sum", "avg"]:
    queries.append(
        f"""
        CREATE UDF IF NOT EXISTS {aggregation_name}
        INPUT (Input_Array NDARRAY ANYTYPE)
        OUTPUT (result INTEGER) -- Permits any result, floats included. FLOAT datatype is not implemented.
        TYPE NdarrayUDF
        IMPL "{EVA_INSTALLATION_DIR}/udfs/ndarray/sql_aggregations.py";
        """
    )

# Add the statistics aggregations.
for aggregation_name in [
    "correlation",
    "covariance",
    "geometric_mean",
    "harmonic_mean",
    "stdev",
    "stdev_sample",
    "z_score",
    "percentile",
]:
    queries.append(
        f"""
        CREATE UDF IF NOT EXISTS {aggregation_name}
        INPUT (Input_Array NDARRAY ANYTYPE) -- Permits any sequence of arguments to be passed
        OUTPUT (result NDARRAY ANYTYPE)             -- Permits any result. FLOAT datatype is not implemented.
        TYPE NdarrayUDF
        IMPL "{EVA_INSTALLATION_DIR}/udfs/ndarray/statistics_aggregations.py";
        """
    )

queries.append(
    f"""
    CREATE UDF IF NOT EXISTS linear_regression
    INPUT (Input_Array NDARRAY ANYTYPE) -- Permits any sequence of arguments to be passed
    OUTPUT (
        slope INTEGER,
        intercept INTEGER,
        rvalue INTEGER,
        pvalue INTEGER,
        stderr INTEGER,
        intercept_stderr INTEGER
    )
    TYPE NdarrayUDF
    IMPL "{EVA_INSTALLATION_DIR}/udfs/ndarray/statistics_aggregations.py";
    """
)


queries.append(
    f"""
    CREATE UDF IF NOT EXISTS Crop
    INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM),
            bboxes NDARRAY FLOAT32(ANYDIM, 4))
    OUTPUT (Cropped_Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
    TYPE  NdarrayUDF
    IMPL  "{EVA_INSTALLATION_DIR}/udfs/ndarray/crop.py";
    """
)


queries.append(
    f"""
    CREATE UDF IF NOT EXISTS FastRCNNObjectDetector
    INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
    OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
    scores NDARRAY FLOAT32(ANYDIM))
    TYPE  Classification
    IMPL '{EVA_INSTALLATION_DIR}/udfs/fastrcnn_object_detector.py';
    """
)


def init_builtin_udfs(mode="debug"):
    """
    Loads the builtin udfs into the system.
    This should be called when the system bootstraps.
    In debug mode, it also loads udfs used in the test suite.
    Arguments:
        mode (str): 'debug' or 'release'
    """

    for query in queries:
        execute_query_fetch_all(query)
