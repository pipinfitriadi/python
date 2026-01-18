#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 31 December 2025

from calendar import monthrange
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Callable
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja
from lxml import etree
from minify_html import minify
from pydantic import validate_call

from ..core.adapters.ports import httpx
from ..core.domain.value_objects import ContentType
from ..core.services import handlers, unit_of_work
from ..data.adapters.ports import boto3
from ..data.domain import domain_services, value_objects
from .domain.value_objects import (
    ROOT_DIR,
    STATIC_DIR,
    Settings,
)

# Variables
app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None,
)
jinja: Jinja = Jinja(Jinja2Templates(directory=ROOT_DIR / "templates"))
bearer_scheme: HTTPBearer = HTTPBearer()


@lru_cache()
def get_settings() -> Settings:  # pragma: no cover
    return Settings()


@validate_call
async def validate_token(
    settings: Settings = Depends(get_settings),  # noqa: B008
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),  # noqa: B008
) -> str:
    if credentials.credentials != settings.cron_secret.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ivalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


@app.middleware("http")
async def minify_middleware(request: Request, call_next: Callable) -> Response:
    SVG_OR_XML: tuple = (ContentType.svg, ContentType.xml)
    response: Response = await call_next(request)
    content_type: ContentType = response.headers.get("content-type", "")

    if any(ct in content_type for ct in (ContentType.html, *SVG_OR_XML)):
        response_body: bytes = b""
        minified_content: bytes = b""

        async for chunk in response.body_iterator:
            response_body += chunk

        response_body_decoded: str = response_body.decode(value_objects.ENCODING)

        if ContentType.html in content_type:
            minified_content = minify(
                response_body_decoded,
                minify_css=True,
                minify_js=True,
            ).encode(value_objects.ENCODING)
        elif any(ct in content_type for ct in SVG_OR_XML):
            minified_content = etree.tostring(
                element_or_tree=etree.XML(
                    text=response_body_decoded,
                    parser=etree.XMLParser(remove_blank_text=True),
                ),
                encoding=value_objects.ENCODING,
            )

        # Update the response body and content length
        response.headers["content-length"] = str(len(minified_content))
        response = HTMLResponse(
            content=minified_content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    return response


app.add_middleware(GZipMiddleware)
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# Routes
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(STATIC_DIR / "favicon.svg")


@app.get("/bps/inflation", include_in_schema=False)
async def extract_inflation_bps(
    settings: Settings = Depends(get_settings),  # noqa: B008
    token: Annotated = Depends(validate_token),  # noqa: B008
) -> Response:
    bucket: str = "datalake"
    now: datetime = datetime.now(tz=ZoneInfo(value_objects.TIME_ZONE))
    filename: date = date(
        year=now.year,
        month=now.month,
        day=monthrange(now.year, now.month)[1],
    )

    with unit_of_work.EtlUnitOfWork(
        sources=(
            httpx.HttpxSourcePort(
                url="https://webapi.bps.go.id/v1/api/view/domain/{DOMAIN}/model/{MODEL}/lang/{LANG}/id/{ID}/key/{KEY}/".format(
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
            bucket=bucket,
            key=f"webapi.bps.go.id/inflation/{filename}.json",
            content_type=ContentType.json,
        ),
    ) as uow:
        datalake_key: Path = handlers.etl(uow)

    with unit_of_work.EtlUnitOfWork(
        sources=(
            boto3.Boto3SourcePort(
                credential=settings.cloudflare_r2,
                bucket=bucket,
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


@app.get("/", include_in_schema=False)
@jinja.page("inflation.html.j2")
async def root() -> dict:
    return dict(title="Inflasi")
