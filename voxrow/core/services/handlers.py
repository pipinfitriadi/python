#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from ..domain.value_objects import Data
from . import unit_of_work


def etl(uow: unit_of_work.EtlUnitOfWork) -> None:
    "Extract, Transform, Load"

    sources: tuple[Data, ...] = tuple(source.extract() for source in uow.sources)

    uow.destination.loads(
        *(sources if uow.transform is None else uow.transform(*sources))
    )
