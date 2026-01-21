#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

from pathlib import Path

from pydantic import validate_call
from pydantic.dataclasses import dataclass

from ...domain import domain_services
from ...domain.value_objects import Data, ResourceLocation
from . import AbstractDestinationPort


@dataclass(frozen=True)
class PathDestinationPort(AbstractDestinationPort):
    file: Path

    @validate_call
    def load(self, data: Data) -> ResourceLocation:
        self.file.write_text(domain_services.dumps_to_json(data))

        return self.file
