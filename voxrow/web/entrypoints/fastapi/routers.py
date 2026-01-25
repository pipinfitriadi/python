#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from calendar import monthrange
from datetime import date, datetime
from http import HTTPMethod
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from ....core.adapters.ports import httpx
from ....core.domain.value_objects import ContentEncoding, ContentType, Data
from ....core.services import handlers, unit_of_work
from ....data.adapters.ports import boto3
from ....data.domain import domain_services, value_objects
from ...domain.value_objects import (
    ROOT_DIR,
    STATIC_DIR,
    Settings,
)
from .dependencies import get_settings, validate_token

# Variables
router: APIRouter = APIRouter()
templates: Jinja2Templates = Jinja2Templates(directory=ROOT_DIR / "templates")
jinja: Jinja = Jinja(templates)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse(STATIC_DIR / "favicon.svg")


@router.get("/bps/inflation")
async def extract_inflation_bps(
    settings: Settings = Depends(get_settings),  # noqa: B008
    token: Annotated = Depends(validate_token),  # noqa: B008
) -> Response:
    BUCKET: str = "datalake"
    WEB_DOMAIN: str = "webapi.bps.go.id"
    now: datetime = datetime.now(tz=value_objects.TIME_ZONE)
    filename: date = date(
        year=now.year,
        month=now.month,
        day=monthrange(now.year, now.month)[1],
    )

    with unit_of_work.EtlUnitOfWork(
        sources=(
            httpx.HttpxSourcePort(
                url="https://{WEB_DOMAIN}/v1/api/view/domain/{DOMAIN}/model/{MODEL}/lang/{LANG}/id/{ID}/key/{KEY}/".format(
                    WEB_DOMAIN=WEB_DOMAIN,
                    KEY=settings.bps_key.get_secret_value(),
                    LANG="ind",
                    DOMAIN="0000",  # Pusat
                    MODEL="statictable",  # Static Table
                    # Tingkat Inflasi Harga Konsumen Nasional Tahunan (Y-on-Y)
                    ID=915,
                )
            ),
        ),
        destination=boto3.Boto3DestinationPort(
            credential=settings.cloudflare_r2,
            bucket=BUCKET,
            key=f"{WEB_DOMAIN}/inflation/{filename}.json.gz",
            content_type=ContentType.json,
            content_encoding=ContentEncoding.gzip,
        ),
    ) as uow:
        datalake_key: Path = handlers.etl(uow)

    with unit_of_work.EtlUnitOfWork(
        sources=(
            boto3.Boto3SourcePort(
                credential=settings.cloudflare_r2,
                bucket=BUCKET,
                key=datalake_key,
            ),
        ),
        destination=boto3.Boto3DestinationPort(
            credential=settings.cloudflare_r2,
            bucket="web",
            key="inflation.json",
            content_type=ContentType.json,
        ),
        transform=domain_services.inflation_bps_to_datamart,
    ) as uow:
        handlers.etl(uow)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/idx/stock-summary")
async def extract_stock_summary_idx(
    settings: Settings = Depends(get_settings),  # noqa: B008
    token: Annotated = Depends(validate_token),  # noqa: B008
    date: date = None,
) -> Response:
    date = date or datetime.now(tz=value_objects.TIME_ZONE).date()

    if date.strftime("%a") not in ("Sat", "Sun"):
        WEB_DOMAIN: str = "idx.co.id"
        data: Data = domain_services.decodo_web_scraping_parsed(
            httpx.HttpxSourcePort(
                url="https://scraper-api.decodo.com/v2/scrape",
                method=HTTPMethod.POST,
                headers={
                    "Authorization": (
                        f"Basic {settings.decodo_web_scraping_token.get_secret_value()}"
                    ),
                    "Accept": ContentType.json,
                    "Content-Type": ContentType.json,
                },
                json=dict(
                    url="https://{WEB_DOMAIN}/primary/TradingSummary/GetStockSummary?date={DATE}".format(
                        WEB_DOMAIN=WEB_DOMAIN,
                        DATE=date.strftime("%Y%m%d"),
                    ),
                    successful_status_codes=[200],
                ),
                timeout=60,
            ).extract()
        )

        if data["data"]:
            with unit_of_work.EtlUnitOfWork(
                sources=(data,),
                destination=boto3.Boto3DestinationPort(
                    credential=settings.cloudflare_r2,
                    bucket="datalake",
                    key=f"{WEB_DOMAIN}/GetStockSummary/{date}.json.gz",
                    content_type=ContentType.json,
                    content_encoding=ContentEncoding.gzip,
                ),
            ) as uow:
                handlers.etl(uow)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", include_in_schema=False)
@jinja.page("inflation.html.j2")
async def root() -> dict:
    return dict(title="Inflasi")
