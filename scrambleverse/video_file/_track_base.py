from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

import ffmpeg

from ._streams import Streams

if TYPE_CHECKING:
    from ._info import VideoFile

__all__ = ["TrackBase"]


@dataclass(frozen=True)
class TrackBase(Streams, ABC):
    file: VideoFile
    track_index: str
    filters: tuple[tuple[str, tuple, dict], ...]

    def __init__(
        self,
        file: VideoFile,
        track_index: str,
        *,
        filters: tuple[tuple[str, tuple, dict], ...] = ()
    ):
        super().__init__(streams=(self,))

        object.__setattr__(self, "file", file)
        object.__setattr__(self, "track_index", track_index)
        object.__setattr__(self, "filters", filters)

    @property
    def ffmpeg_input(self):
        input_ = ffmpeg.input(self.file.path)[self.track_index]
        for filter_name, args, kwargs in self.filters:
            input_ = input_.filter(filter_name, *args, **kwargs)
        return input_
