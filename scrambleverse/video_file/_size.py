from dataclasses import dataclass
from typing import overload, TypeAlias

__all__ = ["FrameSize", "FrameSizeLike"]


@dataclass(frozen=True)
class FrameSize:
    width: int
    height: int

    @overload
    def __init__(self, width: int, height: int, /) -> None: ...
    @overload
    def __init__(self, size: FrameSizeLike, /) -> None: ...

    def __init__(self, *args) -> None:
        if len(args) == 1:
            t = tuple(args[0])
            assert len(t) == 2
            assert all(isinstance(v, int) for v in t)
            width, height = t
        else:
            assert len(args) == 2
            assert all(isinstance(v, int) for v in args)
            width = args[0]
            height = args[1]

        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)

    def fit_long_side(self, new_long_side: int) -> "FrameSize":
        long_side = max(self.width, self.height)
        scale = new_long_side / long_side
        return self * scale

    def fit_short_side(self, new_short_side: int) -> "FrameSize":
        short_side = min(self.width, self.height)
        scale = new_short_side / short_side
        return self * scale

    def __mul__(self, scale: float) -> "FrameSize":
        return FrameSize(int(self.width * scale), int(self.height * scale))

    def __iter__(self):
        yield self.width
        yield self.height

    def size_str(self) -> str:
        return f"{self.width}x{self.height}"


FrameSizeLike: TypeAlias = tuple[int, int] | FrameSize
