from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._track_base import TrackBase

if TYPE_CHECKING:
    from ._info import VideoFile

__all__ = ["AudioTrack"]


@dataclass(frozen=True)
class AudioTrack(TrackBase):
    codec_name: str
    channels: int
    sample_rate: int

    def __init__(
        self,
        file: VideoFile,
        track_index: str,
        *,
        codec_name: str,
        channels: int,
        sample_rate: int,
        filters: tuple[tuple[str, tuple, dict], ...] = ()
    ):
        super().__init__(file, track_index, filters=filters)

        object.__setattr__(self, "codec_name", codec_name)
        object.__setattr__(self, "channels", channels)
        object.__setattr__(self, "sample_rate", sample_rate)

    def resample(self, sample_rate: int) -> AudioTrack:
        new_filters = self.filters + (("aresample", (sample_rate,), {}),)
        return AudioTrack(
            file=self.file,
            track_index=self.track_index,
            codec_name=self.codec_name,
            channels=self.channels,
            sample_rate=self.sample_rate,
            filters=new_filters,
        )
