# coding=utf-8
# Copyright 2018-2020 EVA
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

from src.parser.statement import AbstractStatement

from src.parser.types import StatementType
from src.parser.table_ref import TableRef


class TrainFilterStatement(AbstractStatement):
    """Train Filter Statement constructed after parsing the input query

    Attributes:
        name: str
            name of filter to be trained
        target_data: TableRef
            data containing the mapping from frames to the desired
            output that is to be learned
    """

    def __init__(self,
                 name: str,
                 target_data: TableRef):
        super().__init__(StatementType.TRAIN_FILTER)
        self._name = name
        self._target_data = target_data

    def __str__(self) -> str:
        print_str = 'TRAIN {} ON {}'. \
                    format(self._name, self._target_data)
        return print_str

    @property
    def name(self):
        return self._name

    @property
    def target_data(self):
        return self._target_data

    def __eq__(self, other):
        if not isinstance(other, TrainFilterStatement):
            return False
        return (self.name == other.name
                and self.target_data == other.target_data)
