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

from voxrow.web import app

# Constants
TEST_FILES_DIR: Path = Path("tests") / "files"
TEST_FILE_INFLATION: Path = TEST_FILES_DIR / "datalake" / "bps" / "inflation.json"

# Variables
client: TestClient = TestClient(app)


def test_favicon() -> None:
    response: Response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"


def test_root(mocker: MockerFixture) -> None:
    mocker.patch.object(
        Path,
        "is_file",
        return_value=False,
    )

    mocker_response: mocker.Mock = mocker.Mock()
    mocker_response.json.return_value = json.loads(TEST_FILE_INFLATION.read_text())
    mocker.patch("voxrow.web.httpx.get", return_value=mocker_response)

    mocker.patch("voxrow.web.open", mocker.mock_open())

    response: Response = client.get("/")

    assert response.status_code == 200
