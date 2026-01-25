#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from ...domain.value_objects import STATIC_DIR
from . import exception_handlers, middleware, routers

# Variables
app: FastAPI = FastAPI(
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(BaseHTTPMiddleware, dispatch=middleware.minify_middleware)
app.add_middleware(GZipMiddleware)
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)
app.add_exception_handler(HTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(Exception, exception_handlers.internal_server_error_handler)
app.include_router(routers.router)
