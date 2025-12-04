import os
import re
from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING

import ffmpeg

from ._strpath import StrPath


if TYPE_CHECKING:
    from ._track_base import TrackBase

__all__ = ["Streams"]

time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")


@dataclass(frozen=True)
class Streams:
    streams: tuple[TrackBase, ...]

    def __add__(self, other: Streams) -> Streams:
        return Streams(streams=self.streams + other.streams)

    def _build(self, output: str, **kwargs):
        return ffmpeg.output(
            *[s.streams[0].ffmpeg_input for s in self.streams],
            output,
            **{"loglevel": "error", **kwargs},
        ).global_args("-progress", "pipe:1", "-nostats")

    def save(
        self,
        output: StrPath,
        *,
        report_progress: Callable[[float], None] | None = None,
        **kwargs
    ) -> None:
        proc = (
            self._build(os.fspath(output), **kwargs)
            .global_args("-progress", "pipe:1", "-nostats")
            .run_async(pipe_stdout=True, overwrite_output=True)
        )

        for line in proc.stdout:
            line = line.decode("utf-8", errors="ignore").strip()
            match = time_pattern.search(line)
            if match:
                h, m, s = map(float, match.groups())
                total_seconds = h * 3600 + m * 60 + s
                if report_progress:
                    report_progress(total_seconds)

        proc.wait()
