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
import copy
from typing import List, Tuple

from eva.catalog.catalog_manager import CatalogManager
from eva.expression.abstract_expression import (
    AbstractExpression,
    ExpressionType,
)
from eva.expression.expression_utils import (
    conjuction_list_to_expression_tree,
    contains_single_column,
    expression_tree_to_conjunction_list,
    function_expression_to_tuple_value_expression,
    is_simple_predicate,
)
from eva.expression.function_expression import FunctionExpression
from eva.expression.tuple_value_expression import TupleValueExpression
from eva.optimizer.operators import LogicalFilter, LogicalFunctionScan
from eva.parser.create_statement import ColumnDefinition
from eva.utils.logging_manager import logger


def column_definition_to_udf_io(
    col_list: List[ColumnDefinition], is_input: bool
):
    """Create the UdfIO object fro each column definition provided

    Arguments:
        col_list(List[ColumnDefinition]): parsed input/output definitions
        is_input(bool): true if input else false
    """
    if isinstance(col_list, ColumnDefinition):
        col_list = [col_list]

    result_list = []
    for col in col_list:
        if col is None:
            logger.error("Empty column definition while creating udf io")
            result_list.append(col)
        result_list.append(
            CatalogManager().udf_io(
                col.name,
                col.type,
                array_type=col.array_type,
                dimensions=col.dimension,
                is_input=is_input,
            )
        )
    return result_list


def extract_equi_join_keys(
    join_predicate: AbstractExpression,
    left_table_aliases: List[str],
    right_table_aliases: List[str],
) -> Tuple[List[AbstractExpression], List[AbstractExpression]]:

    pred_list = expression_tree_to_conjunction_list(join_predicate)
    left_join_keys = []
    right_join_keys = []
    for pred in pred_list:
        if pred.etype == ExpressionType.COMPARE_EQUAL:
            left_child = pred.children[0]
            right_child = pred.children[1]
            # only extract if both are TupleValueExpression
            if (
                left_child.etype == ExpressionType.TUPLE_VALUE
                and right_child.etype == ExpressionType.TUPLE_VALUE
            ):
                if (
                    left_child.table_alias in left_table_aliases
                    and right_child.table_alias in right_table_aliases
                ):
                    left_join_keys.append(left_child)
                    right_join_keys.append(right_child)
                elif (
                    left_child.table_alias in right_table_aliases
                    and right_child.table_alias in left_table_aliases
                ):
                    left_join_keys.append(right_child)
                    right_join_keys.append(left_child)

    return (left_join_keys, right_join_keys)


def extract_pushdown_predicate(
    predicate: AbstractExpression, column_alias: str
) -> Tuple[AbstractExpression, AbstractExpression]:
    """Decompose the predicate into pushdown predicate and remaining predicate

    Args:
        predicate (AbstractExpression): predicate that needs to be decomposed
        column (str): column_alias to extract predicate
    Returns:
        Tuple[AbstractExpression, AbstractExpression]: (pushdown predicate,
        remaining predicate)
    """
    if predicate is None:
        return None, None

    if contains_single_column(predicate, column_alias):
        if is_simple_predicate(predicate):
            return predicate, None

    pushdown_preds = []
    rem_pred = []
    pred_list = expression_tree_to_conjunction_list(predicate)
    for pred in pred_list:
        if contains_single_column(pred, column_alias) and is_simple_predicate(
            pred
        ):
            pushdown_preds.append(pred)
        else:
            rem_pred.append(pred)

    return (
        conjuction_list_to_expression_tree(pushdown_preds),
        conjuction_list_to_expression_tree(rem_pred),
    )


def extract_function_expressions(
    predicate: AbstractExpression,
) -> Tuple[List[FunctionExpression], AbstractExpression]:
    """Decompose the predicate into a list of function expressions and remaining predicate

    Args:
        predicate (AbstractExpression): input predicate

    Returns:
        Tuple[List[FunctionExpression], AbstractExpression]: list of
            function expressions and remaining predicate
    """
    pred_list = expression_tree_to_conjunction_list(predicate)
    function_exprs = []
    remaining_exprs = []
    for pred in pred_list:
        # either child of the predicate has a FunctionExpression
        if isinstance(pred.children[0], FunctionExpression) or isinstance(
            pred.children[1], FunctionExpression
        ):
            function_exprs.append(pred)
        else:
            remaining_exprs.append(pred)

    return (
        function_exprs,
        conjuction_list_to_expression_tree(remaining_exprs),
    )


def convert_predicate_containing_function_expr_to_function_scan(
    predicate: AbstractExpression,
):
    func_expr = None
    child_idx = -1
    if isinstance(predicate.children[0], FunctionExpression):
        func_expr = predicate.children[0]
        child_idx = 0
    elif isinstance(predicate.children[1], FunctionExpression):
        func_expr = predicate.children[1]
        child_idx = 1

    if child_idx == -1 or func_expr is None:
        logger.warning("Predicate does not contain Function Expression")
        return None, None

    func_scan = LogicalFunctionScan(func_expr)
    tuple_value_expr = function_expression_to_tuple_value_expression(func_expr)
    if tuple_value_expr:
        predicate.children[child_idx] = tuple_value_expr
        return func_scan, predicate
    else:
        return None, None


def extract_function_exprs_from_projection(
    project_list: List[AbstractExpression],
) -> Tuple[List[FunctionExpression], List[AbstractExpression]]:
    """Split the project_list into a list of function expressions and other projections

    Args:
        project_list (List[AbstractExpression]): input projection list

    Returns:
        Tuple[List[FunctionExpression], List[AbstractExpression]]: list of
            function expressions and other projections
    """
    function_exprs = []
    other_exprs = []
    for expr in project_list:
        if isinstance(expr, FunctionExpression):
            function_exprs.append(expr)
        else:
            other_exprs.append(expr)

    return (function_exprs, other_exprs)


def convert_function_expr_to_function_scan(func_expr: FunctionExpression):
    if not isinstance(func_expr, FunctionExpression):
        logger.warn(f"Expected FunctionExpression, got {type(func_expr)}")
        return None, None

    # Do not copy any output column from the original Function Expression before
    # converting to FunctionScan. FunctionScan is expected to generate all the columns.
    new_func_expr = FunctionExpression(
        func=func_expr.function,
        name=func_expr.name,
        alias=func_expr.alias,
        children=func_expr.children,
    )
    new_func_expr.udf_obj = func_expr.udf_obj
    func_scan = LogicalFunctionScan(new_func_expr)

    tuple_value_expr = function_expression_to_tuple_value_expression(func_expr)
    if tuple_value_expr:
        return func_scan, tuple_value_expr
    else:
        logger.warn(f"Failed to convert {func_expr} to TupleValueExpression")
        return None, None
