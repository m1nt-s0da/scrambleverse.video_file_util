from fractions import Fraction
from threading import Lock
from typing import Any, TYPE_CHECKING
from ._size import FrameSizeLike, FrameSize

if TYPE_CHECKING:
    from ._video_track import VideoTrack

__all__ = ["VideoFrames"]


class VideoFrames:
    __proc: Any = None
    __proc_lock = Lock()

    def __init__(
        self,
        track: VideoTrack,
        size: FrameSizeLike,
        fps: int | Fraction,
        *,
        pix_fmt="rgb24",
    ) -> None:
        self.__track = track
        self.__size = FrameSize(size)
        self.__fps = fps
        self.__pix_fmt = pix_fmt
        self.__len = int(self.__track.file.duration * float(self.__fps))

    def __len__(self) -> int:
        return self.__len

    def start(self) -> bool:
        new_width, new_height = self.__size

        track = self.__track.scale((new_width, new_height)).fps(self.__fps)

        with self.__proc_lock:
            if self.__proc is not None:
                return False

            self.__proc = track.ffmpeg_input.output(
                f"pipe:",
                format="rawvideo",
                pix_fmt=self.__pix_fmt,
                loglevel="error",
            ).run_async(pipe_stdout=True)
            return True

    def close(self) -> None:
        with self.__proc_lock:
            if self.__proc is not None:
                self.__proc.kill()
            else:
                raise RuntimeError("Process is not running")

    def __enter__(self) -> "VideoFrames":
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def __iter__(self):
        frame_size = self.__size.width * self.__size.height * 3
        i = 0
        try:
            while i < self.__len:
                in_bytes = self.__proc.stdout.read(frame_size)
                if not in_bytes:
                    break
                frame = memoryview(in_bytes).cast("B").toreadonly()
                yield frame
                i += 1
        except Exception:
            raise
        else:
            self.__proc.wait()
        finally:
            self.__proc.kill()
