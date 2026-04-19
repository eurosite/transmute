from downloaders import HttpDownloader, YtDlpDownloader
from registry.downloader_registry import DownloaderRegistry
import downloaders.ytdlp_downloader as ytdlp_downloader


class _MatchingExtractor:
    IE_NAME = "vimeo"

    def suitable(self, url: str) -> bool:
        return "vimeo.com" in url


class _GenericExtractor:
    IE_NAME = "generic"

    def suitable(self, url: str) -> bool:
        return True


def test_ytdlp_downloader_matches_site_specific_extractors(monkeypatch):
    monkeypatch.setattr(
        ytdlp_downloader,
        "_site_specific_extractors",
        lambda: (_MatchingExtractor(),),
    )

    assert YtDlpDownloader().can_handle("https://vimeo.com/148751763") is True


def test_ytdlp_downloader_does_not_match_generic_urls(monkeypatch):
    monkeypatch.setattr(
        ytdlp_downloader,
        "_site_specific_extractors",
        lambda: (),
    )

    assert YtDlpDownloader().can_handle("https://example.com/video.mp4") is False


def test_registry_prefers_http_downloader_when_only_generic_would_match(monkeypatch):
    monkeypatch.setattr(
        ytdlp_downloader,
        "_site_specific_extractors",
        lambda: (),
    )

    registry = DownloaderRegistry.__new__(DownloaderRegistry)
    registry.downloaders = [YtDlpDownloader, HttpDownloader]

    downloader = registry.get_downloader_for_url("https://example.com/video.mp4")

    assert isinstance(downloader, HttpDownloader)


def test_registry_prefers_ytdlp_for_site_specific_urls(monkeypatch):
    monkeypatch.setattr(
        ytdlp_downloader,
        "_site_specific_extractors",
        lambda: (_MatchingExtractor(),),
    )

    registry = DownloaderRegistry.__new__(DownloaderRegistry)
    registry.downloaders = [YtDlpDownloader, HttpDownloader]

    downloader = registry.get_downloader_for_url("https://vimeo.com/148751763")

    assert isinstance(downloader, YtDlpDownloader)