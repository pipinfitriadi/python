#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

from fastapi import FastAPI

app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None,
)


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}
