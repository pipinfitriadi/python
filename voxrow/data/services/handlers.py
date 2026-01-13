#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 13 January 2026


from ...core.adapters import ports
from ...core.domain.value_objects import Data


def data_mart(
    source: ports.AbstractSourcePort,
    transform: ports.AbstractTransformPort,
    destination: ports.AbstractDestinationPort,
) -> None:
    data: Data = source.fetch()
    data = transform.enrich(data)

    destination.load(data)
