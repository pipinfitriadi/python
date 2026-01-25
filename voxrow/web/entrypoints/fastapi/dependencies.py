#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import validate_call

from ...domain.value_objects import Settings

# Variables
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
