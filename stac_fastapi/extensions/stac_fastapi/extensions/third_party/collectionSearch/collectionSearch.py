# encoding: utf-8
"""Filter Extension."""
from enum import Enum
from typing import List, Type, Union

import attr
from fastapi import APIRouter, FastAPI
from starlette.responses import Response
from stac_pydantic import Collection

from stac_fastapi.api.models import JSONSchemaResponse, GeoJSONResponse
from stac_fastapi.api.routes import create_async_endpoint
from stac_fastapi.types.core import AsyncCollectionSearchClient, CollectionSearchClient
from stac_fastapi.types.extension import ApiExtension
from stac_fastapi.types.search import BaseCollectionSearchGetRequest, BaseCollectionSearchPostRequest
from stac_fastapi.types.config import ApiSettings

from ..collectionSearch.request import CollectionSearchExtensionGetRequest, CollectionSearchExtensionPostRequest

class FilterConformanceClasses(str, Enum):
    """Conformance classes for the Filter extension.

    See
    https://github.com/stac-api-extensions/filter
    """

    CORE = "https://api.stacspec.org/v1.0.0-rc.1/core"
    COLLECTION_SEARCH = "https://api.stacspec.org/v1.0.0-rc.1/collection-search"
    SIMPLE_QUERY = "http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/simple-query"

@attr.s
class CollectionSearchExtension(ApiExtension):
    """CollectionSearch Extension.

    The filter extension adds several endpoints which allow the retrieval of
    queryables and provides an expressive mechanism for searching based on Item
    Attributes:
        GET /queryables
        GET /collections/{collection_id}/queryables

    https://github.com/stac-api-extensions/filter/blob/main/README.md

    Attributes:
        client: Queryables endpoint logic
        conformance_classes: Conformance classes provided by the extension
    """
    
    GET = CollectionSearchExtensionGetRequest
    POST = CollectionSearchExtensionPostRequest

    search_get_request_model: Type[BaseCollectionSearchGetRequest] = attr.ib(
        default=BaseCollectionSearchGetRequest
    )
    search_post_request_model: Type[BaseCollectionSearchPostRequest] = attr.ib(
        default=BaseCollectionSearchPostRequest
    )
    
    client: Union[AsyncCollectionSearchClient, CollectionSearchClient] = attr.ib(
        factory=CollectionSearchClient
    )
    
    conformance_classes: List[str] = attr.ib(
        default=[
            FilterConformanceClasses.CORE,
            FilterConformanceClasses.COLLECTION_SEARCH,
            FilterConformanceClasses.SIMPLE_QUERY,
        ]
    )
    router: APIRouter = attr.ib(factory=APIRouter)
    response_class: Type[Response] = attr.ib(default=JSONSchemaResponse)
    

    def register(self, app: FastAPI) -> None:
        """Register the extension with a FastAPI application.

        Args:
            app: target FastAPI application.

        Returns:
            None
        """
        self.router.prefix = app.state.router_prefix
        self.router.add_api_route(
            name="Collection Search",
            path="/collection-search",
            methods=["GET"],
            endpoint=create_async_endpoint(
                self.client.get_collection_search, self.search_get_request_model, self.response_class
            ),
        )

        self.router.add_api_route(
            name="Collection Search",
            path="/collection-search",
            response_model=(Collection),
            response_class=GeoJSONResponse,
            response_model_exclude_unset=True,
            response_model_exclude_none=True,
            methods=["POST"],
            endpoint=create_async_endpoint(
                self.client.post_collection_search, self.search_post_request_model, GeoJSONResponse
            ),
        )

        app.include_router(self.router, tags=["Collection Search Extension"])
