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
from collections import deque
import copy
import itertools
from typing import Dict, List

from eva.constants import UNDEFINED_GROUP_ID
from eva.optimizer.group import Group
from eva.optimizer.group_expression import GroupExpression
from eva.optimizer.operators import OperatorType
from eva.utils.logging_manager import logger


class Memo:
    """
    For now, we assume every group has only one logic expression.
    """

    def __init__(self):
        # map from hash to group_expr to speed up finding duplicates
        self._group_exprs: Dict[int, GroupExpression] = dict()
        self._groups = dict()

    @property
    def groups(self):
        return self._groups

    @property
    def group_exprs(self):
        return self._group_exprs

    def find_duplicate_expr(self, expr: GroupExpression) -> GroupExpression:
        if hash(expr) in self.group_exprs:
            return self.group_exprs[hash(expr)]
        else:
            return None

    def get_group_by_id(self, group_id: int) -> GroupExpression:
        if group_id in self._groups.keys():
            return self._groups[group_id]
        else:
            logger.error("Missing group id")

    """
    For the consistency of the memo, all modification should use the
    following functions.
    """

    def _get_table_aliases(self, expr: GroupExpression) -> List[str]:
        """
        Collects table aliases of all the children
        """
        aliases = []
        for child_grp_id in expr.children:
            child_grp = self._groups[child_grp_id]
            aliases.extend(child_grp.aliases)
        if (
            expr.opr.opr_type == OperatorType.LOGICALGET
            or expr.opr.opr_type == OperatorType.LOGICALQUERYDERIVEDGET
        ):
            aliases.append(expr.opr.alias)

        return aliases

    def _create_new_group(self, expr: GroupExpression):
        """
        Create new group for the expr
        """
        new_group_id = len(self._groups)
        aliases = self._get_table_aliases(expr)
        self._groups[new_group_id] = Group(new_group_id, aliases)
        self._insert_expr(expr, new_group_id)

    def _insert_expr(self, expr: GroupExpression, group_id: int):
        """
        Insert a group expressoin into a particular group
        """
        assert group_id < len(self.groups), "Group Id out of the bound"

        group = self.groups[group_id]
        group.add_expr(expr)
        self._group_exprs[hash(expr)] = expr

    def erase_group(self, group_id: int):
        """
        Remove all the expr from the group_id
        """
        group = self.groups[group_id]
        for expr in group.logical_exprs:
            del self._group_exprs[hash(expr)]
        for expr in group.physical_exprs:
            del self._group_exprs[hash(expr)]

        group.clear_grp_exprs()

    def add_group_expr(
        self,
        expr: GroupExpression,
        group_id: int = UNDEFINED_GROUP_ID,
        check_duplicate: bool = True,
    ) -> GroupExpression:
        """Add group expression to a group.

        If the `group_id` is specified, it adds the expression to the corresponding
        group. However, if group_id is not specified, it creates a new group.
        If `check_duplicate` is set to True, the function checks for a duplicate
        expresison in the memo before creating a new group.
        The function raises error if the caller provides a valid `group_id` and  sets
        `check_duplicate = True`.
        Args:
            expr (GroupExpression): group expresison to be added
            group_id (int, optional): group id of the group, the caller wants to add
            the expression. Defaults to UNDEFINED_GROUP_ID.
            check_duplicate (bool, optional): decides if caller wants to check for
            duplicate. Defaults to True.

        Returns:
            GroupExpression: The group expression with the correct group_id
        Raises:
            RuntimeError: if caller passes valid group_id and sets check_duplicate to
            True
        """
        if group_id != UNDEFINED_GROUP_ID and check_duplicate:
            err_msg = "Both group_id and check_duplicate are set"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        # check duplicate expression
        if check_duplicate:
            duplicate_expr = self.find_duplicate_expr(expr)
            if duplicate_expr is not None:
                return duplicate_expr

        expr.group_id = group_id

        if expr.group_id == UNDEFINED_GROUP_ID:
            self._create_new_group(expr)
        else:
            self._insert_expr(expr, group_id)

        assert (
            expr.group_id is not UNDEFINED_GROUP_ID
        ), "Expr should have a valid group id"

        return expr

    def get_all_logical_plans(self, group_id):
        plans = []
        root_group = self.get_group_by_id(group_id)
        for expr in root_group.logical_exprs:
            child_plans = []
            for child in expr.children:
                child_plans.append(self.get_all_logical_plans(child))

            for plan_comb in itertools.product(*child_plans):
                root_opr = copy.deepcopy(expr.opr)
                for child_opr in plan_comb:
                    root_opr.append_child(child_opr)
                plans.append(root_opr)

        return plans
