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


class min(AbstractUDF):
    @property
    def name(self) -> str:
        return "min"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        It will return a series composed of the aggregated values of each column.
        """

        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        value = np.min(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [value]})


class max(AbstractUDF):
    @property
    def name(self) -> str:
        return "max"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        """
        It will return a series composed of the aggregated values of each column.
        """

        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        value = np.max(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [value]})


class avg(AbstractUDF):
    @property
    def name(self) -> str:
        return "avg"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        stdev = np.mean(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [stdev]})


class sum(AbstractUDF):
    @property
    def name(self) -> str:
        return "sum"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        value = x.sum()

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [value]})


class count(AbstractUDF):
    @property
    def name(self) -> str:
        return "count"

    def setup(self):
        pass

    def forward(self, inp: pd.DataFrame) -> pd.DataFrame:
        # Aggregate the dataset into a single-row frame.
        x = inp.iloc[:, 0].values
        value = len(x)

        # The name of this key must match the `OUTPUT ($key_name TYPE)` clause in the `CREATE UDF` statement.
        return pd.DataFrame({"result": [value]})
