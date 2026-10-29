from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from infinite_engine.config import Settings
from infinite_engine.main import create_app
from pydantic import ValidationError


def test_health_without_credentials_or_storage(tmp_path: Path) -> None:
    data_dir = tmp_path / "not-created"
    settings = Settings(_env_file=None, data_dir=data_dir)
    with TestClient(create_app(settings)) as client:
        assert client.get("/api/health").json() == {"status": "ok", "service": "infinite-engine"}
        assert client.get("/api/health").status_code == 200
        assert client.get("/api/domains").status_code == 404
        assert client.post("/api/health").status_code == 405
    assert not data_dir.exists()


def test_environment_configuration(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("IE_DATA_DIR", str(tmp_path))
    assert Settings(_env_file=None).data_dir == tmp_path
    monkeypatch.setenv("IE_LOG_LEVEL", "not-a-level")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
