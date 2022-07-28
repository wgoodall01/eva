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
from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType
from pathlib import Path


class UploadPlan(AbstractPlan):
    """
    This plan is used for storing information required for upload
    operations.

    Arguments:
        path(Path): file path (with prefix prepended) where
                    the data is uploaded
        video_blob(str): base64 encoded video string
        """

    def __init__(self, file_path: Path, video_blob: str):
        super().__init__(PlanOprType.UPLOAD)
        self._file_path = file_path
        self._video_blob = video_blob

    @property
    def file_path(self):
        return self._file_path

    @property
    def video_blob(self):
        return self._video_blob

    def __str__(self):
        return 'UploadPlan(file_path={} video_blob={})'.format(
            self.file_path, "string of video blob")

    def __hash__(self) -> int:
        return hash((super().__hash__(), self.file_path, self.video_blob))
