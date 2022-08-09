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
from typing import Iterator

from eva.executor.abstract_executor import AbstractExecutor
from eva.executor.executor_utils import apply_project
from eva.models.storage.batch import Batch
from eva.planner.project_plan import ProjectPlan


class ProjectExecutor(AbstractExecutor):
    """ """

    def __init__(self, node: ProjectPlan):
        super().__init__(node)
        self.target_list = node.target_list

    def validate(self):
        pass

    def exec(self, *args, **kwargs) -> Iterator[Batch]:
        child_executor = self.children[0]
        for batch in child_executor.exec():
            batch = apply_project(batch, self.target_list)

            if not batch.empty():
                yield batch
        yield from []
