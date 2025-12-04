import pytest
from scrambleverse.video_file import FrameSize


class TestFrameSizeInitialization:
    """FrameSizeの初期化テスト"""

    def test_init_with_two_args(self):
        """2つの引数で初期化"""
        fs = FrameSize(1920, 1080)
        assert fs.width == 1920
        assert fs.height == 1080

    def test_init_with_tuple(self):
        """タプルで初期化"""
        fs = FrameSize((1920, 1080))
        assert fs.width == 1920
        assert fs.height == 1080

    def test_init_with_framesize(self):
        """FrameSizeオブジェクトで初期化"""
        fs1 = FrameSize(1920, 1080)
        fs2 = FrameSize(fs1)
        assert fs2.width == 1920
        assert fs2.height == 1080

    def test_frozen(self):
        """frozen=Trueで不変性を確認"""
        fs = FrameSize(1920, 1080)
        with pytest.raises(AttributeError):
            fs.width = 640  # type: ignore


class TestFrameSizeIterator:
    """イテレータテスト"""

    def test_iter(self):
        """タプル風に展開できる"""
        fs = FrameSize(1920, 1080)
        width, height = fs
        assert width == 1920
        assert height == 1080

    def test_tuple_conversion(self):
        """tupleに変換できる"""
        fs = FrameSize(1920, 1080)
        assert tuple(fs) == (1920, 1080)


class TestFrameSizeOperations:
    """スケーリング操作テスト"""

    def test_mul_by_float(self):
        """浮動小数点数でスケーリング"""
        fs = FrameSize(1920, 1080)
        fs_half = fs * 0.5
        assert fs_half.width == 960
        assert fs_half.height == 540

    def test_mul_by_int(self):
        """整数でスケーリング"""
        fs = FrameSize(1920, 1080)
        fs_double = fs * 2
        assert fs_double.width == 3840
        assert fs_double.height == 2160

    def test_mul_rounding(self):
        """スケーリング時の丸め"""
        fs = FrameSize(1920, 1080)
        fs_scaled = fs * 0.33
        assert fs_scaled.width == int(1920 * 0.33)
        assert fs_scaled.height == int(1080 * 0.33)


class TestFrameSizeFitLongSide:
    """fit_long_sideテスト"""

    def test_fit_long_side_landscape(self):
        """横長動画のlongside をスケール"""
        fs = FrameSize(1920, 1080)  # 長辺: 1920
        fs_scaled = fs.fit_long_side(960)
        assert fs_scaled.width == 960
        assert fs_scaled.height == 540

    def test_fit_long_side_portrait(self):
        """縦長動画のlongside をスケール"""
        fs = FrameSize(1080, 1920)  # 長辺: 1920
        fs_scaled = fs.fit_long_side(960)
        assert fs_scaled.width == 540
        assert fs_scaled.height == 960

    def test_fit_long_side_square(self):
        """正方形のlongside をスケール"""
        fs = FrameSize(1000, 1000)  # 長辺: 1000
        fs_scaled = fs.fit_long_side(500)
        assert fs_scaled.width == 500
        assert fs_scaled.height == 500


class TestFrameSizeFitShortSide:
    """fit_short_sideテスト"""

    def test_fit_short_side_landscape(self):
        """横長動画のshortside をスケール"""
        fs = FrameSize(1920, 1080)  # 短辺: 1080
        fs_scaled = fs.fit_short_side(540)
        assert fs_scaled.width == 960
        assert fs_scaled.height == 540

    def test_fit_short_side_portrait(self):
        """縦長動画のshortside をスケール"""
        fs = FrameSize(1080, 1920)  # 短辺: 1080
        fs_scaled = fs.fit_short_side(540)
        assert fs_scaled.width == 540
        assert fs_scaled.height == 960

    def test_fit_short_side_square(self):
        """正方形のshortside をスケール"""
        fs = FrameSize(1000, 1000)  # 短辺: 1000
        fs_scaled = fs.fit_short_side(500)
        assert fs_scaled.width == 500
        assert fs_scaled.height == 500


class TestFrameSizeStringRepresentation:
    """文字列表現テスト"""

    def test_size_str(self):
        """size_str()フォーマット"""
        fs = FrameSize(1920, 1080)
        assert fs.size_str() == "1920x1080"

    def test_size_str_with_small_values(self):
        """小さい値でのsize_str()"""
        fs = FrameSize(640, 480)
        assert fs.size_str() == "640x480"


class TestFrameSizeEdgeCases:
    """エッジケーステスト"""

    def test_very_small_size(self):
        """非常に小さいサイズ"""
        fs = FrameSize(1, 1)
        assert fs.width == 1
        assert fs.height == 1

    def test_very_large_size(self):
        """非常に大きいサイズ"""
        fs = FrameSize(7680, 4320)  # 8K
        assert fs.width == 7680
        assert fs.height == 4320

    def test_mul_result_rounding(self):
        """スケーリング結果が切り上げられる"""
        fs = FrameSize(100, 100)
        fs_scaled = fs * 0.333
        assert isinstance(fs_scaled.width, int)
        assert isinstance(fs_scaled.height, int)

    def test_zero_scale(self):
        """0倍スケーリング"""
        fs = FrameSize(1920, 1080)
        fs_zero = fs * 0
        assert fs_zero.width == 0
        assert fs_zero.height == 0
