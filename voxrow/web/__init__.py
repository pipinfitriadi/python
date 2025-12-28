#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from minify_html import minify

ENCODING: str = "utf-8"
ROOT_DIR: Path = Path("voxrow") / "web"
TITLE: str = "VOXROW"
app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None,
)
templates: Jinja2Templates = Jinja2Templates(
    directory=ROOT_DIR / "templates",
)


@app.middleware("http")
async def minify_html_middleware(request: Request, call_next: Callable) -> Response:
    response: Response = await call_next(request)

    if "text/html" in response.headers.get("content-type", ""):
        response_body: bytes = b""

        async for chunk in response.body_iterator:
            response_body += chunk

        minified_content: bytes = minify(
            response_body.decode(ENCODING),
            minify_css=True,
            minify_js=True,
        ).encode(ENCODING)

        # Update the response body and content length
        response.headers["content-length"] = str(len(minified_content))

        return HTMLResponse(
            content=minified_content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    return response


app.add_middleware(GZipMiddleware)
app.mount(
    "/files",
    StaticFiles(
        directory=ROOT_DIR / "static",
    ),
    name="static",
)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(ROOT_DIR / "static" / "favicon.svg")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request) -> dict:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=dict(title=TITLE),
    )
