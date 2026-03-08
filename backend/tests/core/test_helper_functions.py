import pytest
from pathlib import Path
from fastapi import HTTPException

from core.helper_functions import ( 
    validate_sql_identifier, 
    detect_media_type, 
    sanitize_extension,
    validate_hexadecimal_filename,
    validate_safe_path,
    sanitize_filename,
    delete_file_and_metadata,
)

def test_validate_sql_identifier():
    assert validate_sql_identifier("abc123") == "abc123"
    assert validate_sql_identifier("_valid_id") == "_valid_id"
    assert validate_sql_identifier("id220041242__") == "id220041242__"

def test_empty_identifier():
    with pytest.raises(ValueError):
        validate_sql_identifier("")

@pytest.mark.parametrize("bad_identifier", [
    "9mm",
    "4mm",
    "2gmailcom",
    "123abc",
])
def test_identifier_starts_with_number(bad_identifier):
    with pytest.raises(ValueError):
        validate_sql_identifier(bad_identifier)

@pytest.mark.parametrize("bad_identifier", [
    "hel$$o",
    "task-1",
    "music-player-4",
    "id@123",
])
def test_identifier_contains_invalid_character(bad_identifier):
    with pytest.raises(ValueError):
        validate_sql_identifier(bad_identifier)

@pytest.mark.parametrize("long_id", [
    "AAAABBBBAAAABBBBAAAABBBBAAAABBBBAAAABBBBAAAABBBBAAAABBBBAAAABBBBC",
    "kolarmocha1233333333333333333333332333333333333333333333333333333333",
    "abc123111111111111111111111111111111111111111111111111111122222222222",
])
def test_identifier_too_long(long_id):
    with pytest.raises(ValueError):
        validate_sql_identifier(long_id)

@pytest.mark.parametrize("file_data", [
    { "filename": "api-sequence.drawio", "media_type": "drawio" },
    { "filename": "beaker-white.svg", "media_type": "svg" },
    { "filename": "config.yaml", "media_type": "yaml" },
    { "filename": "earth_mov", "media_type": "mov" },
    { "filename": "earth.mov", "media_type": "mov" },
    { "filename": "earth.mp4", "media_type": "mp4" },
    { "filename": "employees.json", "media_type": "json" },
    { "filename": "forest_example.jpg", "media_type": "jpg" },
])
def test_detect_media_type(pytestconfig, file_data):
    sample_path = pytestconfig.rootpath / "tests" / "fixtures"
    file = sample_path / file_data["filename"]
    assert detect_media_type(file) == file_data["media_type"]

@pytest.mark.parametrize("extension", [
    { "raw": ".mp4", "cleaned": "mp4" },
    { "raw": "mP4", "cleaned": "mp4" },
    { "raw": ".mp$4", "cleaned": "mp4" },
    { "raw": "png$@", "cleaned": "png" },
    { "raw": "jp-g", "cleaned": "jp-g" },
])
def test_sanitize_extension(extension):
    assert sanitize_extension(extension["raw"]) == extension["cleaned"]

@pytest.mark.parametrize("file", [
    { "filename": "abc-def-123.pdf", "verdict": True },
    { "filename": "abc-dex-123.pdf", "verdict": False },
    { "filename": "abc-def-123-01a.png", "verdict": True },
    { "filename": "gabc-def-123.pdf", "verdict": False },
])
def test_validate_hexadecimal_filename(file):
    assert validate_hexadecimal_filename(file["filename"]) == file["verdict"]

def test_validate_safe_path(safe_path_test_settings, monkeypatch):
    monkeypatch.setattr('core.helper_functions.get_settings', lambda: safe_path_test_settings)
    file_path = safe_path_test_settings.upload_dir / "abcdef123.jpg"
    assert validate_safe_path(file_path) == True

def test_safe_path_contains_non_hex_chars(safe_path_test_settings, monkeypatch):
    monkeypatch.setattr('core.helper_functions.get_settings', lambda: safe_path_test_settings)
    file_path = safe_path_test_settings.upload_dir / "abcdefx123.jpg"
    assert validate_safe_path(file_path, raise_exception=False) == False

def test_safe_path_contains_non_hex_chars_http_exception(safe_path_test_settings, monkeypatch):
    monkeypatch.setattr('core.helper_functions.get_settings', lambda: safe_path_test_settings)
    file_path = safe_path_test_settings.upload_dir / "abcdefx123.jpg"
    with pytest.raises(HTTPException):
        validate_safe_path(file_path)

def test_safe_path_directory_not_allowed_http_exception(safe_path_test_settings, monkeypatch, tmp_path):
    monkeypatch.setattr('core.helper_functions.get_settings', lambda: safe_path_test_settings)
    file_path = tmp_path / "invalid_directory" / "abcdef123.jpg"
    with pytest.raises(HTTPException):
        validate_safe_path(file_path)

def test_safe_path_directory_not_allowed(safe_path_test_settings, monkeypatch, tmp_path):
    monkeypatch.setattr('core.helper_functions.get_settings', lambda: safe_path_test_settings)
    file_path = tmp_path / "invalid_directory" / "abcdef123.jpg"
    assert validate_safe_path(file_path, raise_exception=False) == False

@pytest.mark.parametrize("file", [
    { "raw": "hello.txt", "sanitized": "hello.txt"},
    { "raw": "hello/hello.txt", "sanitized": "hellohello.txt"},
    { "raw": "hello2hello.txt", "sanitized": "hello2hello.txt"},
    { "raw": "hello-hello.txt", "sanitized": "hello-hello.txt"},
    { "raw": "hello$hello.txt", "sanitized": "hellohello.txt"},
    { "raw": ".hello$hello.txt.", "sanitized": "hellohello.txt"},
    { "raw": ".hello$hello.txt.pdf", "sanitized": "hellohello.txt.pdf"},
])
def test_sanitize_filename(file):
    assert sanitize_filename(file["raw"]) == file["sanitized"]

@pytest.mark.parametrize("file", [
    { "raw": "COM4.pdf", "sanitized": "_COM4.pdf"},
    { "raw": "COM3", "sanitized": "_COM3"},
    { "raw": "LPT9.png", "sanitized": "_LPT9.png"},
])
def test_sanitize_filename_windows_reserved_filename(file):
    assert sanitize_filename(file["raw"]) == file["sanitized"]

@pytest.mark.parametrize("file", [
    { 
        "raw": "heeeeeeeeeeeeeeeeeeeeeelllllllllllllllllllllllllllllllooooooooooooooooooooooooooooooooooooooooooowwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwooooooooooooooooooooooooooooooohooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooovvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv.txt", 
        "sanitized": "heeeeeeeeeeeeeeeeeeeeeelllllllllllllllllllllllllllllllooooooooooooooooooooooooooooooooooooooooooowwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwooooooooooooooooooooooooooooooohoooooo.txt",
    },
])
def test_sanitize_filename_long_name(file):
    assert sanitize_filename(file["raw"]) == file["sanitized"]

def test_sanitize_filename_unnamed():
    assert sanitize_filename("") == "unnamed"

def test_delete_file_and_metadata_not_found_http_exception(safe_path_test_settings, tmp_db):
    file: Path = safe_path_test_settings.upload_dir / "hello.txt"
    with pytest.raises(HTTPException):
        delete_file_and_metadata("hello", tmp_db)

def test_delete_file_and_metadata_not_found(safe_path_test_settings, tmp_db):
    file: Path = safe_path_test_settings.upload_dir / "hello.txt"
    assert delete_file_and_metadata("hello", tmp_db, raise_if_not_found=False) is None

def test_delete_file_and_meta_file_deleted(safe_path_test_settings, tmp_db):
    file: Path = safe_path_test_settings.upload_dir / "abc123.txt"
    file.touch()
    tmp_db.insert_file_metadata({
        "id": "abc123",
        "storage_path": str(file),
        "original_filename": "abc123.txt",
        "media_type": "txt",
        "extension": ".txt",
        "size_bytes": 1024,
        "sha256_checksum": "dummy_checksum",
    })
    delete_file_and_metadata("abc123", tmp_db)
    assert file.exists() == False

def test_delete_file_and_meta_file_must_follow_uuid(safe_path_test_settings, tmp_db):
    file: Path = safe_path_test_settings.upload_dir / "hello.txt"
    file.touch()
    tmp_db.insert_file_metadata({
        "id": "hello",
        "storage_path": str(file),
        "original_filename": "hello.txt",
        "media_type": "txt",
        "extension": ".txt",
        "size_bytes": 1024,
        "sha256_checksum": "dummy_checksum",
    })
    with pytest.raises(HTTPException):
        delete_file_and_metadata("hello", tmp_db)