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
import numpy as np
import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF


class Stat_Covariance(AbstractUDF):
    @property
    def name(self) -> str:
        return "Stat_Covariance"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        It will return a series composed of the aggregated values of each column.
        """

        x = inp.iloc[:, 0].values
        y = inp.iloc[:, 1].values

        # Aggregate the dataset
        cov_matrix = np.cov(x, y)
        cov = cov_matrix[0, 1]

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result_covariance": [cov]})
