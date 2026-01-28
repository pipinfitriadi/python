#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

import json
from collections.abc import Callable
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from botocore.client import BaseClient
from fastapi.testclient import TestClient
from typer.testing import CliRunner, Result

from voxrow.core.domain.value_objects import ContentType
from voxrow.data.domain.value_objects import Boto3Credential
from voxrow.web.domain.domain_services import get_fastapi_settings
from voxrow.web.domain.value_objects import Settings
from voxrow.web.entrypoints import fastapi, typer

if TYPE_CHECKING:
    from httpx import Response

# Constants
TEST_FILES_DIR: Path = Path("tests") / "files"
TEST_DATALAKE_DIR: Path = TEST_FILES_DIR / "datalake"
TEST_FILE_INFLATION: str = (
    TEST_DATALAKE_DIR / "webapi.bps.go.id" / "inflation.json"
).read_text()
TEST_KEY: str = "123"
TEST_DATE: str = "2026-01-19"


def fake_get_settings() -> Settings:
    return Settings(
        bps_key=TEST_KEY,
        cloudflare_r2=Boto3Credential(
            endpoint_url=f"https://{TEST_KEY}.r2.cloudflarestorage.com",
            aws_access_key_id=TEST_KEY,
            aws_secret_access_key=TEST_KEY,
        ),
        cron_secret=TEST_KEY,
        decodo_web_scraping_token=TEST_KEY,
    )


# Mocks
@pytest.fixture
def mock_extract_bps_inflation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "voxrow.data.services.unit_of_work.client",
        lambda *args, **kwargs: MagicMock(  # noqa: ARG005
            spec=BaseClient,
            put_object=MagicMock(return_value=None),
            get_object=MagicMock(
                return_value=dict(
                    Body=MagicMock(
                        read=MagicMock(
                            return_value=MagicMock(
                                decode=MagicMock(return_value=TEST_FILE_INFLATION),
                            ),
                        ),
                    ),
                    ContentType=ContentType.json,
                ),
            ),
        ),
    )
    monkeypatch.setattr(
        "voxrow.core.adapters.ports.httpx.get",
        lambda *args, **kwargs: MagicMock(  # noqa: ARG005
            json=MagicMock(return_value=json.loads(TEST_FILE_INFLATION)),
        ),
    )


@pytest.fixture
def mock_extract_idx_stock_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "voxrow.data.services.handlers.sleep",
        MagicMock(),
    )
    monkeypatch.setattr(
        "voxrow.data.services.unit_of_work.client",
        lambda *args, **kwargs: MagicMock(  # noqa: ARG005
            spec=BaseClient,
            put_object=MagicMock(return_value=None),
        ),
    )
    monkeypatch.setattr(
        "voxrow.core.adapters.ports.httpx.post",
        lambda *args, **kwargs: MagicMock(  # noqa: ARG005
            json=MagicMock(
                return_value=dict(
                    results=[
                        dict(
                            content=(
                                TEST_DATALAKE_DIR / "idx.co.id" / "GetStockSummary.json"
                            ).read_text(),
                        ),
                    ],
                ),
            ),
        ),
    )


# Tests
class TestFastAPI:
    client: TestClient

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        fastapi.app.dependency_overrides[get_fastapi_settings] = fake_get_settings

        @fastapi.app.get("/test")
        async def trigger_http_500() -> int:
            return 1 / 0

        self.client = TestClient(fastapi.app, raise_server_exceptions=False)

    def test_trigger_http_500(self) -> None:
        response: Response = self.client.get("/test")
        text: str = response.text

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert ContentType.html in response.headers["content-type"]
        assert "Internal Server Error" in text
        assert str(HTTPStatus.INTERNAL_SERVER_ERROR) in text

    def test_openapi_json(self) -> None:
        response: Response = self.client.get("/openapi.json")

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert ContentType.html in response.headers["content-type"]

    def test_docs(self) -> None:
        response: Response = self.client.get("/docs")

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert ContentType.html in response.headers["content-type"]

    def test_redoc(self) -> None:
        response: Response = self.client.get("/redoc")

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert ContentType.html in response.headers["content-type"]

    def test_favicon(self) -> None:
        response: Response = self.client.get("/favicon.ico")

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == ContentType.svg
        assert response.text != ""

    def test_extract_bps_inflation(
        self,
        mock_extract_bps_inflation: Callable,  # noqa: ARG002
    ) -> None:
        response: Response = self.client.get(
            "/bps/inflation",
            headers=dict(Authorization="Bearer abc"),
        )
        text: str = response.text

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert ContentType.html in response.headers["content-type"]
        assert "Invalid or expired token" in text
        assert str(HTTPStatus.UNAUTHORIZED) in text

        response = self.client.get(
            "/bps/inflation",
            headers=dict(Authorization=f"Bearer {TEST_KEY}"),
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.text == ""

    def test_extract_idx_stock_summary(
        self,
        mock_extract_idx_stock_summary: Callable,  # noqa: ARG002
    ) -> None:
        response: Response = self.client.get(
            "/idx/stock-summary",
            headers=dict(Authorization=f"Bearer {TEST_KEY}"),
            params=dict(date=TEST_DATE),
        )

        assert response.status_code == HTTPStatus.NO_CONTENT
        assert response.text == ""

    def test_root(self) -> None:
        response: Response = self.client.get("/")

        assert response.status_code == HTTPStatus.OK
        assert ContentType.html in response.headers["content-type"]
        assert "Inflasi" in response.text


class TestTyper:
    runner: CliRunner

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.runner = CliRunner()

    @pytest.fixture
    def mock_get_typer_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "voxrow.web.domain.domain_services.get_typer_settings",
            fake_get_settings,
        )

    def test_extract_bps_inflation(
        self,
        mock_get_typer_settings: Callable,  # noqa: ARG002
        mock_extract_bps_inflation: Callable,  # noqa: ARG002
    ) -> None:
        result: Result = self.runner.invoke(
            typer.app,
            ["extract-bps-inflation"],
        )

        assert result.exit_code == 0

    def test_extract_idx_stock_summary(
        self,
        mock_get_typer_settings: Callable,  # noqa: ARG002
        mock_extract_idx_stock_summary: Callable,  # noqa: ARG002
    ) -> None:
        result: Result = self.runner.invoke(
            typer.app,
            [
                "extract-idx-stock-summary",
                "--start-date",
                TEST_DATE,
                "--end-date",
                TEST_DATE,
            ],
        )

        assert result.exit_code == 0

        result = self.runner.invoke(
            typer.app,
            [
                "extract-idx-stock-summary",
                "--start-date",
                "2026-01-20",
                "--end-date",
                TEST_DATE,
            ],
        )

        assert result.exit_code == 0
