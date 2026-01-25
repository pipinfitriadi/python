#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

import json
from http import HTTPStatus
from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from httpx import Response
from pytest import MonkeyPatch, fixture

from voxrow.core.domain.value_objects import ContentType
from voxrow.data.domain.value_objects import Boto3Credential
from voxrow.web.domain.value_objects import Settings
from voxrow.web.entrypoints.fastapi import app
from voxrow.web.entrypoints.fastapi.dependencies import get_settings

# Constants
TEST_FILES_DIR: Path = Path("tests") / "files"
TEST_DATALAKE_DIR: Path = TEST_FILES_DIR / "datalake"
TEST_FILE_INFLATION: str = (
    TEST_DATALAKE_DIR / "webapi.bps.go.id" / "inflation.json"
).read_text()
TEST_KEY: str = "123"


def fake_get_settings() -> Settings:
    return Settings(  # noqa: S106
        bps_key=TEST_KEY,
        cloudflare_r2=Boto3Credential(  # noqa: S106
            endpoint_url=f"https://{TEST_KEY}.r2.cloudflarestorage.com",
            aws_access_key_id=TEST_KEY,
            aws_secret_access_key=TEST_KEY,
        ),
        cron_secret=TEST_KEY,
        decodo_web_scraping_token=TEST_KEY,
    )


# Variables
app.dependency_overrides[get_settings] = fake_get_settings


@app.get("/test")
async def trigger_http_500() -> int:
    return 1 / 0


client: TestClient = TestClient(app, raise_server_exceptions=False)


# Mocks
@fixture
def mock_extract_inflation_bps(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "voxrow.data.adapters.ports.boto3.client",
        lambda *args, **kwargs: MagicMock(
            put_object=MagicMock(return_value=None),
            get_object=MagicMock(
                return_value=dict(
                    Body=MagicMock(
                        read=MagicMock(
                            return_value=MagicMock(
                                decode=MagicMock(return_value=TEST_FILE_INFLATION)
                            )
                        )
                    ),
                    ContentType=ContentType.json,
                )
            ),
        ),
    )
    monkeypatch.setattr(
        "voxrow.core.adapters.ports.httpx.get",
        lambda *args, **kwargs: MagicMock(
            json=MagicMock(return_value=json.loads(TEST_FILE_INFLATION)),
        ),
    )


@fixture
def mock_extract_stock_summary_idx(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "voxrow.data.adapters.ports.boto3.client",
        lambda *args, **kwargs: MagicMock(
            put_object=MagicMock(return_value=None),
        ),
    )
    monkeypatch.setattr(
        "voxrow.core.adapters.ports.httpx.post",
        lambda *args, **kwargs: MagicMock(
            json=MagicMock(
                return_value=dict(
                    results=[
                        dict(
                            content=(
                                TEST_DATALAKE_DIR / "idx.co.id" / "GetStockSummary.json"
                            ).read_text()
                        )
                    ],
                )
            ),
        ),
    )


# Tests
def test_trigger_http_500() -> None:
    response: Response = client.get("/test")
    text: str = response.text

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert ContentType.html in response.headers["content-type"]
    assert "Internal Server Error" in text
    assert str(HTTPStatus.INTERNAL_SERVER_ERROR) in text


def test_openapi_json() -> None:
    response: Response = client.get("/openapi.json")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert ContentType.html in response.headers["content-type"]


def test_docs() -> None:
    response: Response = client.get("/docs")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert ContentType.html in response.headers["content-type"]


def test_redoc() -> None:
    response: Response = client.get("/redoc")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert ContentType.html in response.headers["content-type"]


def test_favicon() -> None:
    response: Response = client.get("/favicon.ico")

    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == ContentType.svg
    assert response.text != ""


def test_extract_inflation_bps(mock_extract_inflation_bps: Callable) -> None:
    response: Response = client.get(
        "/bps/inflation",
        headers=dict(Authorization="Bearer abc"),
    )
    text: str = response.text

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert ContentType.html in response.headers["content-type"]
    assert "Ivalid or expired token" in text
    assert str(HTTPStatus.UNAUTHORIZED) in text

    response = client.get(
        "/bps/inflation",
        headers=dict(Authorization=f"Bearer {TEST_KEY}"),
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.text == ""


def test_extract_stock_summary_idx(mock_extract_stock_summary_idx: Callable) -> None:
    response: Response = client.get(
        "/idx/stock-summary",
        headers=dict(Authorization=f"Bearer {TEST_KEY}"),
        params=dict(date="2026-01-19"),
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.text == ""


def test_root() -> None:
    response: Response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert ContentType.html in response.headers["content-type"]
    assert "Inflasi" in response.text
