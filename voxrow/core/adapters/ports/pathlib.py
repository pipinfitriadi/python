#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from pydantic import validate_call
from pydantic.dataclasses import dataclass

from ...domain.value_objects import Data, PathDestination, ResourceLocation
from . import AbstractDestinationPort


@dataclass(frozen=True)
class PathDestinationPort(AbstractDestinationPort):
    @validate_call
    def load(self, data: Data, *, destination: PathDestination) -> ResourceLocation:
        destination.file.write_text(data)

        return destination.file
