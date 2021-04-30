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

from src.planner.abstract_plan import AbstractPlan
from src.planner.types import PlanOprType
from src.udfs.filters.abstract_filter import AbstractFilter


class TrainFilterPlan(AbstractPlan):
    """
    This plan is used for storing information required to create udf operators

    Attributes:
        filter_obj: AbstractFilter
            object of filter to be trained
        target_data: TableRef
            data containing the mapping from frames to the desired
            output that is to be learned
    """

    def __init__(self,
                 filter_obj: AbstractFilter):
        super().__init__(PlanOprType.TRAIN)
        self._filter_obj = filter_obj

    @property
    def filter_obj(self):
        return self._filter_obj
