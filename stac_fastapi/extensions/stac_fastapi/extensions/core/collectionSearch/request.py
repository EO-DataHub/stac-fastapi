"""Collection Search extension request models."""

from enum import Enum
from typing import Any, Dict, Optional, List

import attr
from pydantic import BaseModel, Field
from stac_pydantic.shared import BBox

from stac_fastapi.types.search import APIRequest, Limit, str2list

@attr.s
class CollectionSearchExtensionGetRequest(APIRequest):
    """Collection Search extension GET request model."""

    bbox: Optional[str] = attr.ib(default=None, converter=str2list)
    datetime: Optional[str] = attr.ib(default=None)
    limit: Optional[int] = attr.ib(default=10)


class CollectionSearchExtensionPostRequest(BaseModel):
    """Collection Search extension POST request model."""

    bbox: Optional[BBox]
    datetime: Optional[str]
    limit: Optional[Limit] = 10
