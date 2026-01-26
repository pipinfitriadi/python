#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from pydantic import validate_call

from ..domain.domain_services import Transform
from ..domain.value_objects import (
    CONFIG_DICT,
    Data,
    Destination,
    ResourceLocation,
    Source,
)
from .unit_of_work import AbstractDataUnitOfWork


@validate_call(config=CONFIG_DICT)
def etl(
    sources: tuple[Data | tuple[AbstractDataUnitOfWork, Source], ...],
    destination: tuple[AbstractDataUnitOfWork, Destination],
    transform: Transform | None = None,
) -> ResourceLocation:
    "Extract, Transform, Load"

    data_sources: list[Data] = []

    for element in sources:
        if (
            isinstance(element, tuple)
            and len(element) == 2
            and isinstance(element[0], AbstractDataUnitOfWork)
            and isinstance(element[1], Source)
        ):
            with element[0] as uow:
                data_sources.append(uow.source_port.extract(source=element[1]))
        else:
            data_sources.append(element)

    with destination[0] as uow:
        resource_location: ResourceLocation = uow.destination_port.load(
            data_sources[0] if transform is None else transform(*data_sources),
            destination=destination[1],
        )

    return resource_location
