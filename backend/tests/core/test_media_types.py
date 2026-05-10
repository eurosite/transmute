import pytest
from core.media_types import media_type_aliases, media_type_extensions


# ── media_type_aliases ───────────────────────────────────────────────

@pytest.mark.parametrize("alias,canonical", [
    ("jpg", "jpeg"),
    ("jfif", "jpeg"),
    ("jpe", "jpeg"),
    ("yml", "yaml"),
    ("tif", "tiff"),
    ("htm", "html"),
    ("mpg", "mpeg"),
    ("aif", "aiff"),
    ("ndjson", "jsonl"),
    ("tgz", "tar.gz"),
    ("tbz2", "tar.bz2"),
    ("txz", "tar.xz"),
    ("tzst", "tar.zst"),
    ("latex", "tex"),
    ("asciidoc", "adoc"),
])
def test_alias_resolves(alias, canonical):
    assert media_type_aliases[alias] == canonical


def test_aliases_are_all_lowercase():
    for alias, canonical in media_type_aliases.items():
        assert alias == alias.lower(), f"alias key '{alias}' is not lowercase"
        assert canonical == canonical.lower(), f"canonical '{canonical}' is not lowercase"


# ── media_type_extensions ────────────────────────────────────────────

@pytest.mark.parametrize("subtype,ext", [
    ("pdf/a", "pdf"),
    ("pdf/x", "pdf"),
    ("pdf/e", "pdf"),
    ("pdf/ua", "pdf"),
    ("pdf/vt", "pdf"),
])
def test_pdf_subtype_maps_to_pdf(subtype, ext):
    assert media_type_extensions[subtype] == ext


def test_all_pdf_subtypes_present():
    expected = {"pdf/a", "pdf/x", "pdf/e", "pdf/ua", "pdf/vt", "kepub"}
    assert expected == set(media_type_extensions.keys())


def test_kepub_maps_to_compound_extension():
    assert media_type_extensions["kepub"] == "kepub.epub"
