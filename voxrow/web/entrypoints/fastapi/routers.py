#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from typing import get_args

from fastapi import APIRouter, Response, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja

from ....data.domain import value_objects
from ....data.services import handlers
from ...domain.value_objects import (
    ROOT_DIR,
    STATIC_DIR,
)
from .dependencies import AppSettings, Token

# Variables
router: APIRouter = APIRouter()
templates: Jinja2Templates = Jinja2Templates(directory=ROOT_DIR / "templates")
jinja: Jinja = Jinja(templates)


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    return FileResponse(STATIC_DIR / "favicon.svg")


@router.get("/bps/inflation")
async def extract_bps_inflation(
    token: Token,
    settings: AppSettings,
) -> Response:
    await handlers.extract_bps_inflation(settings)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/idx/stock-summary")
async def extract_idx_stock_summary(
    token: Token,
    settings: AppSettings,
    date: value_objects.Date = None,
) -> Response:
    await handlers.extract_idx_stock_summary(
        settings,
        date=date or get_args(value_objects.Date)[1].default_factory()(),
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", include_in_schema=False)
@jinja.page("inflation.html.j2")
async def root() -> dict:
    return dict(title="Inflasi")
