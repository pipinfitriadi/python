#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from ..adapters import ports
from ..domain.value_objects import Data, ResourceLocation
from . import unit_of_work


def etl(uow: unit_of_work.EtlUnitOfWork) -> ResourceLocation:
    "Extract, Transform, Load"

    sources: tuple[Data, ...] = tuple(
        source.extract() if isinstance(source, ports.AbstractSourcePort) else source
        for source in uow.sources
    )

    return uow.destination.load(
        sources[0] if uow.transform is None else uow.transform(*sources)
    )
