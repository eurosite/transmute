from pathlib import Path

from api.routes.conversions import copy_webvideo_to_mp4
from api.routes.files import resolve_downloaded_media_type
from downloaders import HttpDownloader, YtDlpDownloader


def test_ytdlp_downloads_are_stored_as_webvideo():
    assert resolve_downloaded_media_type(YtDlpDownloader(), "mp4") == "webvideo"


def test_http_downloads_keep_detected_media_type():
    assert resolve_downloaded_media_type(HttpDownloader(), "mp4") == "mp4"


def test_copy_webvideo_to_mp4_preserves_file_contents(tmp_path):
    source = tmp_path / "source.mp4"
    source.write_bytes(b"webvideo bytes")

    output_files = copy_webvideo_to_mp4(str(source), Path(tmp_path), "converted")

    assert output_files == [str(tmp_path / "converted.mp4")]
    assert (tmp_path / "converted.mp4").read_bytes() == b"webvideo bytes"