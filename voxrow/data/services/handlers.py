#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 26 January 2026

import random
from calendar import monthrange
from datetime import date, datetime, timedelta
from http import HTTPMethod
from pathlib import Path
from time import sleep

from pydantic import validate_call

from ...core.domain import value_objects
from ...core.services import handlers, unit_of_work
from ..domain import domain_services
from ..domain.value_objects import (
    TIME_ZONE,
    Boto3Destination,
    Boto3Source,
    Settings,
)
from .unit_of_work import Boto3DataUnitOfWork


@validate_call
async def extract_bps_inflation(settings: Settings) -> None:
    BUCKET: str = "datalake"
    WEB_DOMAIN: str = "webapi.bps.go.id"
    now: datetime = datetime.now(tz=TIME_ZONE)
    filename: date = date(
        year=now.year,
        month=now.month,
        day=monthrange(now.year, now.month)[1],
    )
    uow_boto3: Boto3DataUnitOfWork = Boto3DataUnitOfWork(settings.cloudflare_r2)
    datalake_key: Path = handlers.etl(
        sources=(
            unit_of_work.HttpxDataUnitOfWork()(
                source=value_objects.HttpxSource(
                    url="https://{WEB_DOMAIN}/v1/api/view/domain/{DOMAIN}/model/{MODEL}/lang/{LANG}/id/{ID}/key/{KEY}/".format(
                        WEB_DOMAIN=WEB_DOMAIN,
                        DOMAIN="0000",  # Pusat
                        MODEL="statictable",  # Static Table
                        LANG="ind",
                        # Tingkat Inflasi Harga Konsumen Nasional Tahunan (Y-on-Y)
                        ID=915,
                        KEY=settings.bps_key.get_secret_value(),
                    )
                )
            ),
        ),
        destination=uow_boto3(
            destination=Boto3Destination(
                bucket=BUCKET,
                key=f"{WEB_DOMAIN}/inflation/{filename}.json.gz",
                content_type=value_objects.ContentType.json,
                content_encoding=value_objects.ContentEncoding.gzip,
            )
        ),
    )

    handlers.etl(
        sources=(
            uow_boto3(
                source=Boto3Source(
                    bucket=BUCKET,
                    key=datalake_key,
                )
            ),
        ),
        destination=uow_boto3(
            destination=Boto3Destination(
                bucket="web",
                key="inflation.json",
                content_type=value_objects.ContentType.json,
            )
        ),
        transform=domain_services.inflation_bps_to_datamart,
    )


@validate_call
async def extract_idx_stock_summary(
    settings: Settings,
    start_date: date,
    end_date: date | None = None,
) -> None:
    if end_date is None:
        if start_date.strftime("%a") not in ("Sat", "Sun"):
            WEB_DOMAIN: str = "idx.co.id"

            with unit_of_work.HttpxDataUnitOfWork()(
                source=value_objects.HttpxSource(
                    url="https://scraper-api.decodo.com/v2/scrape",
                    method=HTTPMethod.POST,
                    headers={
                        "Authorization": "Basic {decodo_token}".format(
                            decodo_token=settings.decodo_web_scraping_token.get_secret_value()
                        ),
                        "Accept": value_objects.ContentType.json,
                        "Content-Type": value_objects.ContentType.json,
                    },
                    json=dict(
                        url="https://{WEB_DOMAIN}/primary/TradingSummary/GetStockSummary?date={DATE}".format(
                            WEB_DOMAIN=WEB_DOMAIN,
                            DATE=start_date.strftime("%Y%m%d"),
                        ),
                        successful_status_codes=[200],
                    ),
                    timeout=60,
                )
            ) as uow:
                data: value_objects.Data = domain_services.decodo_web_scraping_parsed(
                    uow.data.extract(source=uow.source)
                )

            if data["data"]:
                handlers.etl(
                    sources=(data,),
                    destination=Boto3DataUnitOfWork(settings.cloudflare_r2)(
                        destination=Boto3Destination(
                            bucket="datalake",
                            key=f"{WEB_DOMAIN}/GetStockSummary/{start_date}.json.gz",
                            content_type=value_objects.ContentType.json,
                            content_encoding=value_objects.ContentEncoding.gzip,
                        )
                    ),
                )
    elif start_date == end_date:
        await extract_idx_stock_summary(
            settings=settings,
            start_date=start_date,
            end_date=None,
        )
    elif start_date > end_date:
        await extract_idx_stock_summary(
            settings=settings,
            start_date=end_date,
            end_date=start_date,
        )
    else:
        for day in range((end_date - start_date).days + 1):
            await extract_idx_stock_summary(
                settings=settings,
                start_date=start_date + timedelta(days=day),
                end_date=None,
            )
            sleep(random.uniform(3.0, 5.0))  # noqa: S311
