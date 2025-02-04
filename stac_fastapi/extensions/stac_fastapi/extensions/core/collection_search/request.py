"""Collection Search extension request models."""

from typing import List, Optional

import attr
from fastapi import Path
from pydantic import BaseModel, Field
from stac_pydantic.shared import BBox

from stac_fastapi.types.rfc3339 import DateTimeType, str_to_interval
from stac_fastapi.types.search import APIRequest, Limit, str2bbox, str2list
from stac_fastapi.extensions.core.filter.request import FilterLang


@attr.s
class CollectionSearchExtensionGetRequest(APIRequest):
    """Collection Search extension GET request model."""

    bbox: Optional[BBox] = attr.ib(default=None, converter=str2bbox)
    datetime: Optional[DateTimeType] = attr.ib(default=None, converter=str_to_interval)
    limit: Optional[int] = attr.ib(default=10)
    q: Optional[List[str]] = attr.ib(default=None, converter=str2list)
    filter: Optional[str] = attr.ib(default=None)
    filter_crs: Optional[str] = Field(alias="filter-crs", default=None)
    filter_lang: Optional[FilterLang] = Field(alias="filter-lang", default="cql2-text")


@attr.s
class CollectionSearchExtensionGetRequestExt(CollectionSearchExtensionGetRequest):
    """Collection Search extension GET request model."""

    catalog_path: str = attr.ib(
        default=Path(
            ..., description="Path to selected Catalog", example="cat1/cat2/cat3"
        )
    )


class CollectionSearchExtensionPostRequest(BaseModel):
    """Collection Search extension POST request model."""

    bbox: Optional[BBox]
    datetime: Optional[DateTimeType]
    limit: Optional[Limit] = Field(default=10)
    q: Optional[List[str]]
    filter: Optional[str] = attr.ib(default=None)
    filter_crs: Optional[str] = Field(alias="filter-crs", default=None)
    filter_lang: Optional[FilterLang] = Field(alias="filter-lang", default="cql2-text")


class CollectionSearchExtensionPostRequestExt(CollectionSearchExtensionPostRequest):
    """Collection Search extension POST request model."""

    catalog_path: str = attr.ib(
        default=Path(
            ..., description="Path to selected Catalog", example="cat1/cat2/cat3"
        )
    )
