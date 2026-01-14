#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

import html
from calendar import monthrange
from io import StringIO
from typing import Tuple

import lxml.html
import numpy as np
import pandas as pd
from pydantic import validate_call

from ...core.domain.value_objects import Data


@validate_call
def inflation_bps_to_datamart(*args: Data) -> Tuple[Data, ...]:
    data: Data = args[0]["data"]
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

    return (
        dict(
            title=title,
            data=df_flat_table.replace({np.nan: None}).reset_index().to_dict("records"),
        ),
    )
