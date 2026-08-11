"""Auth and subscription API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.api.deps as api_deps
import app.api.main as api_main
import app.storage.db as db_module
from app.api.main import create_app
from app.config.settings import settings as config_settings
from app.models import Base


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db_module.engine = engine
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_module.SessionLocal = session_local
    api_deps.SessionLocal = session_local
    api_main.SessionLocal = session_local
    Base.metadata.create_all(bind=engine)

    d = config_settings.model_dump()
    d["scheduler"] = {**d["scheduler"], "enabled": False}
    d["sync_default_sources_on_startup"] = False
    monkeypatch.setattr(
        api_main,
        "settings",
        type(config_settings).model_validate(d),
    )

    app = create_app()
    with TestClient(app) as tc:
        yield tc


def test_register_login_me_and_subscription(client: TestClient):
    r = client.post(
        "/api/v1/register",
        json={"email": "dash@example.com", "password": "secretpass1", "name": "Dash"},
    )
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    r2 = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r2.status_code == 200
    assert r2.json()["email"] == "dash@example.com"
    assert r2.json()["digest_subscribed"] is True

    r3 = client.patch(
        "/api/v1/me/subscription",
        headers={"Authorization": f"Bearer {token}"},
        json={"digest_subscribed": False},
    )
    assert r3.status_code == 200
    assert r3.json()["digest_subscribed"] is False

    r4 = client.post(
        "/api/v1/login",
        json={"email": "dash@example.com", "password": "secretpass1"},
    )
    assert r4.status_code == 200
    token2 = r4.json()["access_token"]
    r5 = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r5.json()["digest_subscribed"] is False


def test_register_duplicate_email(client: TestClient):
    body = {"email": "dup@example.com", "password": "secretpass1", "name": "Dup User"}
    assert client.post("/api/v1/register", json=body).status_code == 200
    assert client.post("/api/v1/register", json=body).status_code == 409
