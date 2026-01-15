#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

import json
from pathlib import Path

from fastapi.testclient import TestClient
from httpx import Response
from pytest_mock import MockerFixture

from voxrow.core.domain.value_objects import ContentType
from voxrow.data.domain.value_objects import Boto3Credential
from voxrow.web.domain.value_objects import Settings
from voxrow.web.entrypoint import app, get_settings

# Constants
TEST_FILES_DIR: Path = Path("tests") / "files"
TEST_FILE_INFLATION: Path = TEST_FILES_DIR / "datalake" / "bps" / "inflation.json"


def get_test_settings() -> Settings:
    return Settings(
        bps_key="123",
        cloudflare_r2=Boto3Credential(  # noqa: S106
            endpoint_url="https://123.r2.cloudflarestorage.com",
            aws_access_key_id="123",
            aws_secret_access_key="123",
        ),
    )


# Variables
app.dependency_overrides[get_settings] = get_test_settings
client: TestClient = TestClient(app)


# Tests
def test_favicon() -> None:
    response: Response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"] == ContentType.svg
    assert response.text != ""


def test_root(mocker: MockerFixture) -> None:
    mocker.patch.object(
        Path,
        "is_file",
        return_value=False,
    )

    mocker_response: mocker.Mock = mocker.Mock()
    mocker_response.json.return_value = json.loads(TEST_FILE_INFLATION.read_text())
    mocker.patch("voxrow.core.adapters.ports.httpx.get", return_value=mocker_response)

    mocker.patch.object(Path, "write_text", side_effect=None)

    response: Response = client.get("/")

    assert response.status_code == 200
    assert ContentType.html in response.headers["content-type"]
    assert response.text != ""
