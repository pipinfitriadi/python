#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026

import json
from pathlib import Path

from pydantic import validate_call
from pydantic.dataclasses import dataclass

from ...domain.value_objects import Data
from . import AbstractDestinationPort


@dataclass(frozen=True)
class PathDestinationPort(AbstractDestinationPort):
    file: Path

    @validate_call
    def load(self, data: Data) -> None:
        self.file.write_text(json.dumps(data, default=str))
