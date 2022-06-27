from youtooler.utils import *

class TestUtilsModule:
    def test_get_video_duration(self):
        assert get_video_duration('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 213
        assert get_video_duration('https://www.youtube.com/watch?v=9hhMUT2U2L4') == 244
