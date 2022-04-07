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
from typing import List
from eva.expression.abstract_expression import AbstractExpression, \
    ExpressionType
from eva.utils.logging_manager import LoggingLevel, LoggingManager


class WindowFunctionExpression(AbstractExpression):

    def __init__(self,
                 aggregate_func: AbstractExpression,
                 order_by: List[AbstractExpression],
                 frame_start: int,
                 frame_end: int):
        self.aggregate_func = aggregate_func
        self.order_by = order_by
        self.frame_start = frame_start
        self.frame_end = frame_end
        super().__init__(exp_type=ExpressionType.WINDOW_FUNCTION_EXPRESSION)

    def evaluate(self, *args, **kwargs):
        err_msg = 'WindowFunctionExpression doesnot support evaluate. \
                    It is used only for parsing and optimization'
        LoggingManager().log(err_msg, LoggingLevel.ERROR)
        raise RuntimeError(err_msg)

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, WindowFunctionExpression):
            return False
        return (is_subtree_equal
                and self.etype == other.etype
                and self.aggregate_func == other.aggregate_func
                and self.order_by == other.order_by
                and self.frame_start == other.frame_start
                and self.frame_end == other.frame_end)
