import os
from dataclasses import dataclass
from fractions import Fraction

import ffmpeg

from ._strpath import StrPath
from ._size import FrameSize, FrameSizeLike
from ._video_track import VideoTrack
from ._audio_track import AudioTrack

__all__ = ["VideoFile"]


@dataclass(frozen=True)
class VideoFile(os.PathLike[str]):
    path: str
    duration: float
    streams: tuple[VideoTrack | AudioTrack, ...]

    def __init__(self, path: StrPath) -> None:
        path = os.fspath(path)
        probe = ffmpeg.probe(path)
        tracks = []
        audio_track_count = 0
        video_track_count = 0
        duration = float(probe["format"]["duration"])
        for stream in probe["streams"]:
            if stream["codec_type"] == "video":
                avg_frame_rate = Fraction(stream["avg_frame_rate"])
                vt = VideoTrack(
                    file=self,
                    track_index=f"v:{video_track_count}",
                    codec_name=stream["codec_name"],
                    frame_size=FrameSize(
                        int(stream["width"]),
                        int(stream["height"]),
                    ),
                    avg_frame_rate=avg_frame_rate,
                    r_frame_rate=Fraction(stream["r_frame_rate"]),
                    frame_count=int(
                        stream.get(
                            "nb_read_frames",
                            stream.get("nb_frames", duration * float(avg_frame_rate)),
                        )
                    ),
                )
                tracks.append(vt)
                video_track_count += 1
            elif stream["codec_type"] == "audio":
                at = AudioTrack(
                    file=self,
                    track_index=f"a:{audio_track_count}",
                    codec_name=stream["codec_name"],
                    channels=int(stream["channels"]),
                    sample_rate=int(stream["sample_rate"]),
                )
                tracks.append(at)
                audio_track_count += 1
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "duration", duration)
        object.__setattr__(self, "streams", tuple(tracks))

    def __fspath__(self) -> str:
        return self.path

    @property
    def video_tracks(self) -> tuple[VideoTrack, ...]:
        return tuple(s for s in self.streams if isinstance(s, VideoTrack))

    @property
    def audio_tracks(self) -> tuple[AudioTrack, ...]:
        return tuple(s for s in self.streams if isinstance(s, AudioTrack))

    def thumbnail(
        self,
        size: FrameSizeLike,
        *,
        candidates: int = 10,
        pix_fmt="rgb24",
    ) -> bytes:
        size = FrameSize(size)
        stdout, _ = (
            ffmpeg.input(self.path)
            .filter("thumbnail", candidates)
            .filter("scale", size.width, size.height)
            .output(
                f"pipe:",
                vframes=1,
                format="rawvideo",
                pix_fmt=pix_fmt,
                loglevel="error",
            )
            .run(capture_stdout=True)
        )
        return stdout
