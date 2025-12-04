from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

from ._size import FrameSize, FrameSizeLike
from ._track_base import TrackBase
from ._frames import VideoFrames

if TYPE_CHECKING:
    from ._info import VideoFile

__all__ = ["VideoTrack"]


@dataclass(frozen=True)
class VideoTrack(TrackBase):
    codec_name: str
    frame_size: FrameSize
    avg_frame_rate: Fraction
    r_frame_rate: Fraction

    def __init__(
        self,
        file: VideoFile,
        track_index: str,
        *,
        codec_name: str,
        frame_size: FrameSizeLike,
        avg_frame_rate: Fraction,
        r_frame_rate: Fraction,
        filters: tuple[tuple[str, tuple, dict], ...] = (),
    ):
        super().__init__(file, track_index, filters=filters)

        object.__setattr__(self, "codec_name", codec_name)
        object.__setattr__(self, "frame_size", FrameSize(frame_size))
        object.__setattr__(self, "avg_frame_rate", avg_frame_rate)
        object.__setattr__(self, "r_frame_rate", r_frame_rate)

    def scale(self, size: FrameSizeLike) -> VideoTrack:
        size = FrameSize(size)
        new_filters = self.filters + (("scale", (size.width, size.height), {}),)
        return VideoTrack(
            file=self.file,
            track_index=self.track_index,
            codec_name=self.codec_name,
            frame_size=self.frame_size,
            avg_frame_rate=self.avg_frame_rate,
            r_frame_rate=self.r_frame_rate,
            filters=new_filters,
        )

    def fps(self, fps: Fraction | int | float) -> VideoTrack:
        new_filters = self.filters + (("fps", (str(fps),), {}),)
        return VideoTrack(
            file=self.file,
            track_index=self.track_index,
            codec_name=self.codec_name,
            frame_size=self.frame_size,
            avg_frame_rate=self.avg_frame_rate,
            r_frame_rate=self.r_frame_rate,
            filters=new_filters,
        )

    def frames(
        self,
        size: FrameSizeLike,
        fps: int | Fraction,
        *,
        pix_fmt="rgb24",
    ) -> VideoFrames:
        return VideoFrames(self, size, fps, pix_fmt=pix_fmt)
