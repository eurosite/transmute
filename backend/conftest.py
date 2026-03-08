import pytest
from pathlib import Path
from db import FileDB

@pytest.fixture
def safe_path_test_settings(tmp_path):
    class SafePathTestSettings:
        db_path: Path = tmp_path / "database.db"
        upload_dir: Path = tmp_path / "uploads"
        tmp_dir: Path = tmp_path / "tmp"
        output_dir: Path = tmp_path / "outputs"

    SafePathTestSettings.upload_dir.mkdir()
    SafePathTestSettings.tmp_dir.mkdir()
    SafePathTestSettings.output_dir.mkdir()

    return SafePathTestSettings

@pytest.fixture
def tmp_db(safe_path_test_settings, monkeypatch):
    monkeypatch.setattr('core.helper_functions.get_settings', lambda: safe_path_test_settings)
    db = FileDB()
    yield db
    db.close()