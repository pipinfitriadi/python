#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 9 December 2025

import html
import json
from calendar import monthrange
from io import StringIO
from os import getenv
from pathlib import Path
from typing import Callable

import httpx
import lxml.html
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fasthx.jinja import Jinja
from minify_html import minify

# Constants
ENCODING: str = "utf-8"
ROOT_DIR: Path = Path("voxrow") / "web"
STATIC_DIR: Path = ROOT_DIR / "static"

# Variables
app: FastAPI = FastAPI(
    docs_url=None,
    redoc_url=None,
)
jinja: Jinja = Jinja(Jinja2Templates(directory=ROOT_DIR / "templates"))


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


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(STATIC_DIR / "favicon.svg")


@app.get("/", include_in_schema=False)
@jinja.page("inflation.html.j2")
async def root() -> dict:
    json_file: Path = STATIC_DIR / "inflation.json"

    if not json_file.is_file():
        resp: httpx.Response = httpx.get(
            "https://webapi.bps.go.id/v1/api/view/domain/{DOMAIN}/model/{MODEL}/lang/{LANG}/id/{ID}/key/{KEY}/".format(
                KEY=getenv("BPS_KEY"),
                LANG="ind",
                DOMAIN="0000",  # Pusat
                MODEL="statictable",  # Static Table
                ID=915,  # Tingkat Inflasi Harga Konsumen Nasional Tahunan (Y-on-Y)
            )
        )
        data: dict = resp.json()["data"]
        title: str = lxml.html.fromstring(data["title"]).text.strip()
        df: pd.DataFrame = pd.read_html(
            io=StringIO(html.unescape(data["table"])),
            header=2,
            index_col=0,
            decimal=",",
            thousands=".",
            flavor="lxml",
        )[0][:12]
        df_flat_table: pd.DataFrame = (
            df.reset_index()
            .rename(columns={"index": "Bulan"})
            .melt(
                id_vars="Bulan",
                var_name="Tahun",
                value_name="inflation",
            )
        )
        df_flat_table["date"] = (
            pd.concat(
                [
                    df_flat_table["Tahun"].astype(int),
                    df_flat_table["Bulan"].map(
                        {
                            "Januari": 1,
                            "Februari": 2,
                            "Maret": 3,
                            "April": 4,
                            "Mei": 5,
                            "Juni": 6,
                            "Juli": 7,
                            "Agustus": 8,
                            "September": 9,
                            "Oktober": 10,
                            "November": 11,
                            "Desember": 12,
                        }
                    ),
                ],
                axis=1,
            )
            .apply(
                lambda row: pd.to_datetime(
                    "{year}-{month}-{day}".format(
                        year=row["Tahun"],
                        month=row["Bulan"],
                        day=monthrange(row["Tahun"], row["Bulan"])[1],
                    )
                ),
                axis=1,
            )
            .dt.date
        )
        df_flat_table["inflation"] = df_flat_table["inflation"].astype(float)

        del df_flat_table["Bulan"]
        del df_flat_table["Tahun"]

        df_flat_table.set_index("date", inplace=True)

        json_file.write_text(
            json.dumps(
                dict(
                    title=title,
                    data=(
                        df_flat_table.replace({np.nan: None})
                        .reset_index()
                        .to_dict("records")
                    ),
                ),
                default=str,
            )
        )

    return dict(title="Inflasi")
