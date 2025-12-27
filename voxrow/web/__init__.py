#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

ROOT_DIR: Path = Path("voxrow") / "web"
app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None,
)
templates: Jinja2Templates = Jinja2Templates(
    directory=ROOT_DIR / "templates",
)

app.mount(
    "/files",
    StaticFiles(
        directory=ROOT_DIR / "static",
    ),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> dict:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )
