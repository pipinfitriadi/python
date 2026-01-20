#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from typing import Protocol, Tuple, runtime_checkable

from pydantic import validate_call

from .value_objects import Data


@runtime_checkable
class Transform(Protocol):
    @validate_call
    def __call__(self, *args: Data) -> Tuple[Data, ...]: ...
