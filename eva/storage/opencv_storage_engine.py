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
import shutil
import struct
from pathlib import Path
from typing import Iterator

from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.configuration.configuration_manager import ConfigurationManager
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.readers.opencv_reader import OpenCVReader
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.utils.logging_manager import logger


class OpenCVStorageEngine(AbstractStorageEngine):
    def __init__(self):
        self.metadata = "metadata"
        self.curr_version = ConfigurationManager().get_value(
            "storage", "video_engine_version"
        )

    def create(self, table: DataFrameMetadata, video_file: Path):
        # Create directory to store video and metadata related to the video
        dir_path = Path(table.file_url)
        try:
            dir_path.mkdir(parents=True)
            shutil.copy2(str(video_file), str(dir_path))
        except FileExistsError:
            error = "Failed to load the video as directory \
                        already exists: {}".format(
                dir_path
            )
            logger.error(error)
            raise FileExistsError(error)
        self._create_video_metadata(dir_path, video_file.name)
        return True

    def drop(self, table: DataFrameMetadata):
        dir_path = Path(table.file_url)
        try:
            shutil.rmtree(str(dir_path))
        except Exception as e:
            logger.exception(f"Failed to drop the video table {e}")

    def write(self, table: DataFrameMetadata, rows: Batch):
        pass

    def read(
        self,
        table: DataFrameMetadata,
        batch_mem_size: int,
        predicate: AbstractExpression = None,
    ) -> Iterator[Batch]:

        metadata_file = Path(table.file_url) / self.metadata
        video_file_name = self._get_video_file_path(metadata_file)
        video_file = Path(table.file_url) / video_file_name
        reader = OpenCVReader(
            str(video_file), batch_mem_size=batch_mem_size, predicate=predicate
        )
        for batch in reader.read():
            yield batch

    def _get_video_file_path(self, metadata_file):
        with open(metadata_file, "rb") as f:
            (version,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
            if version > self.curr_version:
                error = "Invalid metadata version {}".format(version)
                logger.error(error)
                raise RuntimeError(error)
            (length,) = struct.unpack("!H", f.read(struct.calcsize("!H")))
            path = f.read(length)
            return Path(path.decode())

    def _create_video_metadata(self, dir_path, video_file):
        # File structure
        # <version> <length> <file_name>
        with open(dir_path / self.metadata, "wb") as f:
            # write version number
            file_path_bytes = str(video_file).encode()
            length = len(file_path_bytes)
            data = struct.pack(
                "!HH%ds" % (length,),
                self.curr_version,
                length,
                file_path_bytes,
            )
            f.write(data)

    def _open(self, table):
        pass

    def _close(self, table):
        pass

    def _read_init(self, table):
        pass
