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
import scipy

from eva.udfs.abstract.abstract_udf import AbstractUDF


class correlation(AbstractUDF):
    @property
    def name(self) -> str:
        return "correlation"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        x = inp.iloc[:, 0].values
        y = inp.iloc[:, 1].values

        # Aggregate the dataset
        corr_matrix = np.corrcoef(x, y)

        corr = corr_matrix[0, 1]

        # Get the single result value from that frame.

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [corr]})


class covariance(AbstractUDF):
    @property
    def name(self) -> str:
        return "covariance"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Get a separate series for each variable
        x = inp.iloc[:, 0].values
        y = inp.iloc[:, 1].values

        # Compute the covariance matrix, and get the covariance between the two inputs
        cov_matrix = np.cov(x, y)
        cov = cov_matrix[0, 1]

        # The name of this key must match the `OUTPUT ($key_name TYPE)`
        # clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [cov]})


class geometric_mean(AbstractUDF):
    @property
    def name(self) -> str:
        return "geometric_mean"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        stdev = scipy.stats.mstats.gmean(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [stdev]})


class harmonic_mean(AbstractUDF):
    @property
    def name(self) -> str:
        return "harmonic_mean"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        stdev = scipy.stats.hmean(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [stdev]})


class stdev(AbstractUDF):
    @property
    def name(self) -> str:
        return "Stat_Stdev"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        stdev = np.std(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [stdev]})


class stdev_sample(AbstractUDF):
    @property
    def name(self) -> str:
        return "stdev_sample"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        stdev = np.std(x, ddof=1)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [stdev]})
