#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from fastapi import Request, status
from fastapi.responses import HTMLResponse
from starlette.exceptions import HTTPException

from .routers import templates


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
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


async def internal_server_error_handler(
    request: Request,
    exc: Exception,  # noqa: ARG001
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
