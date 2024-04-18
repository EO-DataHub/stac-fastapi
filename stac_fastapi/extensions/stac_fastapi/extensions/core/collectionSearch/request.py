"""Filter extension request models."""

from enum import Enum
from typing import Any, Dict, Optional, List

import attr
from pydantic import BaseModel, Field
from stac_pydantic.shared import BBox

from stac_fastapi.types.search import APIRequest, Limit, str2list



class FilterLang(str, Enum):
    """Choices for filter-lang value in a POST request.

    Based on
    https://github.com/stac-api-extensions/filter#queryables

    Note the addition of cql2-json, which is used by the pgstac backend,
    but is not included in the spec above.
    """

    cql_json = "cql-json"
    cql2_json = "cql2-json"
    cql2_text = "cql2-text"


@attr.s
class CollectionSearchExtensionGetRequest(APIRequest):
    """Filter extension GET request model."""

    filter: Optional[str] = attr.ib(default=None)
    filter_crs: Optional[str] = Field(alias="filter-crs", default=None)
    filter_lang: Optional[FilterLang] = Field(alias="filter-lang", default="cql2-text")
    bbox: Optional[str] = attr.ib(default=None, converter=str2list)
    #intersects: Optional[str] = attr.ib(default=None)
    datetime: Optional[str] = attr.ib(default=None)
    limit: Optional[int] = attr.ib(default=10)


class CollectionSearchExtensionPostRequest(BaseModel):
    """Filter extension POST request model."""

    bbox: Optional[BBox]
    # intersects: Optional[
    #     Union[Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon]
    # ]
    datetime: Optional[str]
    limit: Optional[Limit] = 10
