#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from typing import Annotated, TypeAlias

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import validate_call

from ...domain.value_objects import Settings
from .. import get_settings

# Variables
bearer_scheme: HTTPBearer = HTTPBearer()


AppSettings: TypeAlias = Annotated[Settings, Depends(get_settings)]
Credentials: TypeAlias = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


@validate_call
async def validate_token(
    settings: AppSettings,
    credentials: Credentials,
) -> str:
    if credentials.credentials != settings.cron_secret.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials


Token: TypeAlias = Annotated[str, Depends(validate_token)]
