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
from voxrow.web.entrypoint import app, get_settings

# Constants
TEST_FILES_DIR: Path = Path("tests") / "files"
TEST_FILE_INFLATION: str = (
    TEST_FILES_DIR / "datalake" / "bps" / "inflation.json"
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
    )


# Variables
app.dependency_overrides[get_settings] = fake_get_settings
client: TestClient = TestClient(app)


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
                                decode=MagicMock(
                                    return_value=TEST_FILE_INFLATION,
                                )
                            )
                        )
                    ),
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


# Tests
def test_favicon() -> None:
    response: Response = client.get("/favicon.ico")

    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == ContentType.svg
    assert response.text != ""


def test_extract_inflation_bps(mock_extract_inflation_bps: Callable) -> None:
    assert (
        client.get(
            "/bps/inflation",
            headers=dict(Authorization="Bearer abc"),
        ).status_code
    ) == HTTPStatus.UNAUTHORIZED

    response: Response = client.get(
        "/bps/inflation",
        headers=dict(Authorization=f"Bearer {TEST_KEY}"),
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert response.text == ""


def test_root() -> None:
    response: Response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert ContentType.html in response.headers["content-type"]
    assert "Inflasi" in response.text
