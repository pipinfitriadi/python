#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 31 December 2025

from os import getenv
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja
from lxml import etree
from minify_html import minify

from ..core.adapters.ports import httpx, pathlib
from ..core.services import handlers, unit_of_work
from ..data.domain import domain_services
from .domain.value_objects import (
    ENCODING,
    ROOT_DIR,
    STATIC_DIR,
    ContentType,
)

# Variables
app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None,
)
jinja: Jinja = Jinja(Jinja2Templates(directory=ROOT_DIR / "templates"))


@app.middleware("http")
async def minify_middleware(request: Request, call_next: Callable) -> Response:
    SVG_OR_XML: tuple = (ContentType.svg, ContentType.xml)
    response: Response = await call_next(request)
    content_type: str = response.headers.get("content-type", "")

    if any(ct in content_type for ct in (ContentType.html, *SVG_OR_XML)):
        response_body: bytes = b""
        minified_content: bytes = b""

        async for chunk in response.body_iterator:
            response_body += chunk

        response_body_decoded: str = response_body.decode(ENCODING)

        if ContentType.html in content_type:
            minified_content = minify(
                response_body_decoded,
                minify_css=True,
                minify_js=True,
            ).encode(ENCODING)
        elif any(ct in content_type for ct in SVG_OR_XML):
            minified_content = etree.tostring(
                element_or_tree=etree.XML(
                    text=response_body_decoded,
                    parser=etree.XMLParser(remove_blank_text=True),
                ),
                encoding=ENCODING,
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


@app.get("/", include_in_schema=False)
@jinja.page("inflation.html.j2")
async def root() -> dict:
    json_file: Path = STATIC_DIR / "inflation.json"

    if not json_file.is_file():
        with unit_of_work.EtlUnitOfWork(
            sources=(
                httpx.HttpxSourcePort(
                    url="https://webapi.bps.go.id/v1/api/view/domain/{DOMAIN}/model/{MODEL}/lang/{LANG}/id/{ID}/key/{KEY}/".format(
                        KEY=getenv("BPS_KEY"),
                        LANG="ind",
                        DOMAIN="0000",  # Pusat
                        MODEL="statictable",  # Static Table
                        # Tingkat Inflasi Harga Konsumen Nasional Tahunan (Y-on-Y)
                        ID=915,
                    )
                ),
            ),
            destination=pathlib.PathDestinationPort(files=(json_file,)),
            transform=domain_services.inflation_bps_to_datamart,
        ) as uow:
            handlers.etl(uow)

    return dict(title="Inflasi")
