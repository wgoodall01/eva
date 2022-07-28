# coding=utf-8
# Copyright 2018-2021 EVA
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
from typing import List
from eva.planner.abstract_plan import AbstractPlan
from eva.expression.abstract_expression import AbstractExpression
from eva.planner.types import PlanOprType
from eva.catalog.models.df_metadata import DataFrameMetadata


class InsertPlan(AbstractPlan):
    """
    This plan is used for storing information required for insert
    operations.

    Arguments:
        table_metainfo{int} -- video metadata id to insert into
        column_list{List[AbstractExpression]} -- list of annotated column
        value_list{List[AbstractExpression]} -- list of abstract expression
                                                for the values to insert
    """

    def __init__(self, table_metainfo: DataFrameMetadata,
                 column_list: List[AbstractExpression],
                 value_list: List[AbstractExpression]):
        super().__init__(PlanOprType.INSERT)
        self.table_metainfo = table_metainfo
        self.columns_list = column_list
        self.value_list = value_list

    def __hash__(self) -> int:
        return hash((super().__hash__(),
                     self.table_metainfo,
                     tuple(self.column_list),
                     tuple(self.value_list)))
