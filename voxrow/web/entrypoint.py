#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 31 December 2025

from calendar import monthrange
from datetime import date, datetime
from functools import lru_cache
from http import HTTPMethod
from pathlib import Path
from typing import Annotated, Callable

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
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..core.adapters.ports import httpx
from ..core.domain.value_objects import ContentType, Data
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
templates: Jinja2Templates = Jinja2Templates(directory=ROOT_DIR / "templates")
jinja: Jinja = Jinja(templates)
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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="error.html.j2",
        status_code=exc.status_code,
        context=dict(
            title=exc.detail,
            status_code=exc.status_code,
        ),
    )


@app.exception_handler(Exception)
async def exception_handler(
    request: Request,
    exc: Exception,
) -> HTMLResponse:
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    return templates.TemplateResponse(
        request=request,
        name="error.html.j2",
        status_code=status_code,
        context=dict(
            title="Internal Server Error",
            status_code=status_code,
        ),
    )


# Routes
@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse(STATIC_DIR / "favicon.svg")


@app.get("/bps/inflation", include_in_schema=False)
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
            key=f"{WEB_DOMAIN}/inflation/{filename}.json",
            content_type=ContentType.json,
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


@app.get("/idx/stock-summary", include_in_schema=False)
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
                    key=f"{WEB_DOMAIN}/GetStockSummary/{date}.json",
                    content_type=ContentType.json,
                ),
            ) as uow:
                handlers.etl(uow)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/", include_in_schema=False)
@jinja.page("inflation.html.j2")
async def root() -> dict:
    return dict(title="Inflasi")
