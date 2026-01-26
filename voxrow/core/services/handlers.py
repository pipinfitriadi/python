#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 14 January 2026

from pydantic import validate_call

from ..domain.domain_services import Transform
from ..domain.value_objects import CONFIG_DICT, Data, ResourceLocation
from .unit_of_work import AbstractDataUnitOfWork


@validate_call(config=CONFIG_DICT)
def etl(
    sources: tuple[Data | AbstractDataUnitOfWork, ...],
    destination: AbstractDataUnitOfWork,
    transform: Transform | None = None,
) -> ResourceLocation:
    "Extract, Transform, Load"

    data_sources: list[Data] = []

    for source in sources:
        if isinstance(source, AbstractDataUnitOfWork):
            with source as uow:
                data_sources.append(uow.source_port.extract(source=uow.source_domain))
        else:
            data_sources.append(source)

    with destination as uow:
        resource_location: ResourceLocation = uow.destination_port.load(
            data_sources[0] if transform is None else transform(*data_sources),
            destination=uow.destination_domain,
        )

    return resource_location
