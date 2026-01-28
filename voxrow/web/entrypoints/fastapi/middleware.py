#!/usr/bin/env python3

# Copyright (C) Pipin Fitriadi - All Rights Reserved

# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Pipin Fitriadi <pipinfitriadi@gmail.com>, 25 January 2026

from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import HTMLResponse
from lxml import etree
from minify_html import minify

from ....core.domain.value_objects import ENCODING, ContentType


async def minify_middleware(request: Request, call_next: Callable) -> Response:
    svg_or_xml: tuple = (ContentType.svg, ContentType.xml)
    response: Response = await call_next(request)
    content_type: ContentType = response.headers.get("content-type", "")

    if any(ct in content_type for ct in (ContentType.html, *svg_or_xml)):
        response_body: bytes = b""
        minified_content: bytes = b""

        async for chunk in response.body_iterator:
            response_body += chunk

        response_body_decoded: str = response_body.decode(ENCODING)

        if ContentType.html in content_type:
            minified_content = minify(
                response_body_decoded,
                minify_css=True,
                minify_js=True,
            ).encode(ENCODING)
        elif any(ct in content_type for ct in svg_or_xml):
            minified_content = etree.tostring(
                element_or_tree=etree.XML(
                    text=response_body_decoded,
                    parser=etree.XMLParser(remove_blank_text=True),
                ),
                encoding=ENCODING,
            )

        # Update the response body and content length
        response.headers["content-length"] = str(len(minified_content))
        response = HTMLResponse(
            content=minified_content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    return response
