"""Base clients."""

import abc
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import attr
from fastapi import Request
from stac_pydantic.links import Relations
from stac_pydantic.shared import BBox, MimeTypes
from stac_pydantic.version import STAC_VERSION
from starlette.responses import Response

from stac_fastapi.types import stac as stac_types
from stac_fastapi.types.config import ApiSettings
from stac_fastapi.types.conformance import BASE_CONFORMANCE_CLASSES
from stac_fastapi.types.extension import ApiExtension
from stac_fastapi.types.requests import get_base_url
from stac_fastapi.types.rfc3339 import DateTimeType
from stac_fastapi.types.search import (
    BaseCatalogSearchPostRequest,
    BaseCollectionSearchPostRequest,
    BaseDiscoverySearchPostRequest,
    BaseSearchPostRequest,
)
from stac_fastapi.types.stac import Conformance

NumType = Union[float, int]
StacType = Dict[str, Any]

api_settings = ApiSettings()


@attr.s  # type:ignore
class BaseTransactionsClient(abc.ABC):
    """Defines a pattern for implementing the STAC API Transaction Extension."""

    @abc.abstractmethod
    def create_item(
        self,
        collection_id: str,
        item: Union[stac_types.Item, stac_types.ItemCollection],
        **kwargs,
    ) -> Optional[Union[stac_types.Item, Response, None]]:
        """Create a new item.

        Called with `POST /collections/{collection_id}/items`.

        Args:
            item: the item or item collection
            collection_id: the id of the collection from the resource path

        Returns:
            The item that was created or None if item collection.
        """
        ...

    @abc.abstractmethod
    def update_item(
        self,
        catalog_id: str,
        collection_id: str,
        item_id: str,
        item: stac_types.Item,
        **kwargs,
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Perform a complete update on an existing item.

        Called with `PUT /collections/{collection_id}/items`. It is expected
        that this item already exists.  The update should do a diff against the
        saved item and perform any necessary updates.  Partial updates are not
        supported by the transactions extension.

        Args:
            item: the item (must be complete)
            collection_id: the id of the collection from the resource path

        Returns:
            The updated item.
        """
        ...

    @abc.abstractmethod
    def delete_item(
        self, item_id: str, collection_id: str, catalog_id: str, **kwargs
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Delete an item from a collection.

        Called with `DELETE /collections/{collection_id}/items/{item_id}`

        Args:
            item_id: id of the item.
            collection_id: id of the collection.

        Returns:
            The deleted item.
        """
        ...

    @abc.abstractmethod
    def create_collection(
        self, catalog_id: str, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Create a new collection.

        Called with `POST /collections`.

        Args:
            collection: the collection

        Returns:
            The collection that was created.
        """
        ...

    @abc.abstractmethod
    def create_catalog(
        self, catalog: stac_types.Catalog, **kwargs
    ) -> Optional[Union[stac_types.Catalog, Response]]:
        """Create a new catalog.

        Called with `POST /catalogs`.

        Args:
            catalog: the catalog

        Returns:
            The catalog that was created.
        """
        ...

    @abc.abstractmethod
    def update_collection(
        self, collection_id: str, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Perform a complete update on an existing collection.

        Called with `PUT /collections/{collection_id}`. It is expected that this item
        already exists.  The update should do a diff against the saved collection and
        perform any necessary updates.  Partial updates are not supported by the
        transactions extension.

        Args:
            collection_id: id of the existing collection to be updated
            collection: the updated collection (must be complete)

        Returns:
            The updated collection.
        """
        ...

    @abc.abstractmethod
    def delete_collection(
        self, catalog_id: str, collection_id: str, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Delete a collection.

        Called with `DELETE /collections/{collection_id}`

        Args:
            collection_id: id of the collection.

        Returns:
            The deleted collection.
        """
        ...


@attr.s  # type:ignore
class AsyncBaseTransactionsClient(abc.ABC):
    """Defines a pattern for implementing the STAC transaction extension."""

    @abc.abstractmethod
    async def create_item(
        self,
        collection_id: str,
        item: Union[stac_types.Item, stac_types.ItemCollection],
        **kwargs,
    ) -> Optional[Union[stac_types.Item, Response, None]]:
        """Create a new item.

        Called with `POST /collections/{collection_id}/items`.

        Args:
            item: the item or item collection
            collection_id: the id of the collection from the resource path

        Returns:
            The item that was created or None if item collection.
        """
        ...

    @abc.abstractmethod
    async def update_item(
        self,
        catalog_id: str,
        collection_id: str,
        item_id: str,
        item: stac_types.Item,
        **kwargs,
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Perform a complete update on an existing item.

        Called with `PUT /collections/{collection_id}/items`. It is expected
        that this item already exists.  The update should do a diff against the
        saved item and perform any necessary updates.  Partial updates are not
        supported by the transactions extension.

        Args:
            item: the item (must be complete)

        Returns:
            The updated item.
        """
        ...

    @abc.abstractmethod
    async def delete_item(
        self, item_id: str, collection_id: str, catalog_id: str, **kwargs
    ) -> Optional[Union[stac_types.Item, Response]]:
        """Delete an item from a collection.

        Called with `DELETE /collections/{collection_id}/items/{item_id}`

        Args:
            item_id: id of the item.
            collection_id: id of the collection.

        Returns:
            The deleted item.
        """
        ...

    @abc.abstractmethod
    async def create_collection(
        self, collection: stac_types.Collection, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Create a new collection.

        Called with `POST /collections`.

        Args:
            collection: the collection

        Returns:
            The collection that was created.
        """
        ...

    @abc.abstractmethod
    async def update_collection(
        self,
        catalog_id: str,
        collection_id: str,
        collection: stac_types.Collection,
        **kwargs,
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Perform a complete update on an existing collection.

        Called with `PUT /catalogs/{catalog_id}/collections/{collection_id}`. It is expected that this item
        already exists.  The update should do a diff against the saved collection and
        perform any necessary updates.  Partial updates are not supported by the
        transactions extension.

        Args:
            collection_id: id of the existing collection to be updated
            collection: the updated collection (must be complete)

        Returns:
            The updated collection.
        """
        ...

    @abc.abstractmethod
    async def delete_collection(
        self, catalog_id: str, collection_id: str, **kwargs
    ) -> Optional[Union[stac_types.Collection, Response]]:
        """Delete a collection.

        Called with `DELETE /catalogs/{catalog_id}/collections/{collection_id}`

        Args:
            collection_id: id of the collection.

        Returns:
            The deleted collection.
        """
        ...


@attr.s
class LandingPageMixin(abc.ABC):
    """Create a STAC landing page (GET /)."""

    stac_version: str = attr.ib(default=STAC_VERSION)
    landing_page_id: str = attr.ib(default=api_settings.stac_fastapi_landing_id)
    title: str = attr.ib(default=api_settings.stac_fastapi_title)
    description: str = attr.ib(default=api_settings.stac_fastapi_description)

    def _landing_page(
        self,
        base_url: str,
        conformance_classes: List[str],
        extension_schemas: List[str],
    ) -> stac_types.LandingPage:
        landing_page = stac_types.LandingPage(
            type="Catalog",
            id=self.landing_page_id,
            title=self.title,
            description=self.description,
            stac_version=self.stac_version,
            conformsTo=conformance_classes,
            links=[
                {
                    "rel": Relations.self.value,
                    "type": MimeTypes.json,
                    "href": base_url,
                },
                {
                    "rel": Relations.root.value,
                    "type": MimeTypes.json,
                    "href": base_url,
                },
                {
                    "rel": "data",
                    "type": MimeTypes.json,
                    "href": urljoin(base_url, "collections"),
                },
                {
                    "rel": Relations.conformance.value,
                    "type": MimeTypes.json,
                    "title": "STAC/OGC conformance classes implemented by this server",
                    "href": urljoin(base_url, "conformance"),
                },
                {
                    "rel": Relations.search.value,
                    "type": MimeTypes.geojson,
                    "title": "STAC search",
                    "href": urljoin(base_url, "search"),
                    "method": "GET",
                },
                {
                    "rel": Relations.search.value,
                    "type": MimeTypes.geojson,
                    "title": "STAC search",
                    "href": urljoin(base_url, "search"),
                    "method": "POST",
                },
            ],
            stac_extensions=extension_schemas,
        )
        return landing_page


@attr.s  # type:ignore
class BaseCoreClient(LandingPageMixin, abc.ABC):
    """Defines a pattern for implementing STAC api core endpoints.

    Attributes:
        extensions: list of registered api extensions.
    """

    base_conformance_classes: List[str] = attr.ib(
        factory=lambda: BASE_CONFORMANCE_CLASSES
    )
    extensions: List[ApiExtension] = attr.ib(default=attr.Factory(list))
    post_request_model = attr.ib(default=BaseSearchPostRequest)

    def conformance_classes(self) -> List[str]:
        """Generate conformance classes by adding extension conformance to base
        conformance classes."""
        base_conformance_classes = self.base_conformance_classes.copy()

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance_classes.extend(extension_classes)

        return list(set(base_conformance_classes))

    def extension_is_enabled(self, extension: str) -> bool:
        """Check if an api extension is enabled."""
        return any([type(ext).__name__ == extension for ext in self.extensions])

    def list_conformance_classes(self):
        """Return a list of conformance classes, including implemented extensions."""
        base_conformance = BASE_CONFORMANCE_CLASSES

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            base_conformance.extend(extension_classes)

        return base_conformance

    def landing_page(self, **kwargs) -> stac_types.LandingPage:
        """Landing page.

        Called with `GET /`.

        Returns:
            API landing page, serving as an entry point to the API.
        """
        request: Request = kwargs["request"]
        base_url = get_base_url(request)
        landing_page = self._landing_page(
            base_url=base_url,
            conformance_classes=self.conformance_classes(),
            extension_schemas=[],
        )

        # Add Queryables link
        if self.extension_is_enabled("FilterExtension"):
            landing_page["links"].append(
                {
                    # TODO: replace this with Relations.queryables.value,
                    "rel": "http://www.opengis.net/def/rel/ogc/1.0/queryables",
                    # TODO: replace this with MimeTypes.jsonschema,
                    "type": "application/schema+json",
                    "title": "Queryables",
                    "href": urljoin(base_url, "queryables"),
                    "method": "GET",
                }
            )

        # Add Collections links
        collections = self.all_collections(request=kwargs["request"])
        for collection in collections["collections"]:
            landing_page["links"].append(
                {
                    "rel": Relations.child.value,
                    "type": MimeTypes.json.value,
                    "title": collection.get("title") or collection.get("id"),
                    "href": urljoin(base_url, f"collections/{collection['id']}"),
                }
            )

        # Add OpenAPI URL
        landing_page["links"].append(
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "title": "OpenAPI service description",
                "href": urljoin(
                    str(request.base_url), request.app.openapi_url.lstrip("/")
                ),
            }
        )

        # Add human readable service-doc
        landing_page["links"].append(
            {
                "rel": "service-doc",
                "type": "text/html",
                "title": "OpenAPI service documentation",
                "href": urljoin(
                    str(request.base_url), request.app.docs_url.lstrip("/")
                ),
            }
        )

        return landing_page

    def conformance(self, **kwargs) -> stac_types.Conformance:
        """Conformance classes.

        Called with `GET /conformance`.

        Returns:
            Conformance classes which the server conforms to.
        """
        return Conformance(conformsTo=self.conformance_classes())

    @abc.abstractmethod
    def post_global_search(
        self, search_request: BaseSearchPostRequest, **kwargs
    ) -> stac_types.ItemCollection:
        """Cross catalog search (POST).

        Called with `POST /search`.

        Args:
            search_request: search request parameters.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    def get_global_search(
        self,
        catalogs: Optional[List[str]] = None,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: Optional[int] = 10,
        query: Optional[str] = None,
        token: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sortby: Optional[str] = None,
        intersects: Optional[str] = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Cross catalog search (GET).

        Called with `GET /search`.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    def post_search(
        self, catalog_id: str, search_request: BaseCatalogSearchPostRequest, **kwargs
    ) -> stac_types.ItemCollection:
        """Single catalog item search (POST).

        Called with `POST /catalogs/{catalog_id}/search`.

        Args:
            search_request: search request parameters.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    def get_search(
        self,
        catalog_id: str,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: Optional[int] = 10,
        query: Optional[str] = None,
        token: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sortby: Optional[str] = None,
        intersects: Optional[str] = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Single catalog item search (GET).

        Called with `GET /catalogs/{catalog_id}/search`.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    def get_item(
        self, item_id: str, collection_id: str, catalog_id: str, **kwargs
    ) -> stac_types.Item:
        """Get item by id.

        Called with `GET /collections/{collection_id}/items/{item_id}`.

        Args:
            item_id: Id of the item.
            collection_id: Id of the collection.

        Returns:
            Item.
        """
        ...

    @abc.abstractmethod
    def all_collections(self, **kwargs) -> stac_types.Collections:
        """Get all available collections.

        Called with `GET /collections`.

        Returns:
            A list of collections.
        """
        ...

    @abc.abstractmethod
    def all_catalogs(self, **kwargs) -> stac_types.Catalogs:
        """Get all available catalogs.

        Called with `GET /catalogs`.

        Returns:
            A list of catalogs.
        """
        ...

    @abc.abstractmethod
    def get_collection(
        self, catalog_id: str, collection_id: str, **kwargs
    ) -> stac_types.Collection:
        """Get collection by id.

        Called with `GET /catalogs/{catalog_id}/collections/{collection_id}`.

        Args:
            collection_id: Id of the collection.

        Returns:
            Collection.
        """
        ...

    @abc.abstractmethod
    def get_catalog(self, catalog_id: str, **kwargs) -> stac_types.Catalog:
        """Get catalog by id.

        Called with `GET /catalogs/{catalog_id}`.

        Args:
            catalog_id: Id of the catalog.

        Returns:
            Catalog.
        """
        ...

    @abc.abstractmethod
    def get_catalog_collections(
        self, catalog_id: str, **kwargs
    ) -> stac_types.Collections:
        """Get collections by catalog id.

        Called with `GET /catalogs/{catalog_id}/collections`.

        Args:
            catalog_id: Id of the catalog.

        Returns:
            Collections.
        """
        ...

    @abc.abstractmethod
    def item_collection(
        self,
        collection_id: str,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: int = 10,
        token: str = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Get all items from a specific collection.

        Called with `GET /collections/{collection_id}/items`

        Args:
            collection_id: id of the collection.
            limit: number of items to return.
            token: pagination token.

        Returns:
            An ItemCollection.
        """
        ...


@attr.s  # type:ignore
class AsyncBaseCoreClient(LandingPageMixin, abc.ABC):
    """Defines a pattern for implementing STAC api core endpoints.

    Attributes:
        extensions: list of registered api extensions.
    """

    base_conformance_classes: List[str] = attr.ib(
        factory=lambda: BASE_CONFORMANCE_CLASSES
    )
    extensions: List[ApiExtension] = attr.ib(default=attr.Factory(list))
    post_request_model = attr.ib(default=BaseSearchPostRequest)

    def conformance_classes(self) -> List[str]:
        """Generate conformance classes by adding extension conformance to base
        conformance classes."""
        conformance_classes = self.base_conformance_classes.copy()

        for extension in self.extensions:
            extension_classes = getattr(extension, "conformance_classes", [])
            conformance_classes.extend(extension_classes)

        return list(set(conformance_classes))

    def extension_is_enabled(self, extension: str) -> bool:
        """Check if an api extension is enabled."""
        return any([type(ext).__name__ == extension for ext in self.extensions])

    async def landing_page(self, **kwargs) -> stac_types.LandingPage:
        """Landing page.

        Called with `GET /`.

        Returns:
            API landing page, serving as an entry point to the API.
        """
        request: Request = kwargs["request"]
        base_url = get_base_url(request)
        landing_page = self._landing_page(
            base_url=base_url,
            conformance_classes=self.conformance_classes(),
            extension_schemas=[],
        )

        # Add Queryables link
        if self.extension_is_enabled("FilterExtension"):
            landing_page["links"].append(
                {
                    # TODO: replace this with Relations.queryables.value,
                    "rel": "http://www.opengis.net/def/rel/ogc/1.0/queryables",
                    # TODO: replace this with MimeTypes.jsonschema,
                    "type": "application/schema+json",
                    "title": "Queryables",
                    "href": urljoin(base_url, "queryables"),
                    "method": "GET",
                }
            )

        # Add Collections links
        # collections = await self.all_collections(request=kwargs["request"])
        # for collection in collections["collections"]:
        #     landing_page["links"].append(
        #         {
        #             "rel": Relations.child.value,
        #             "type": MimeTypes.json.value,
        #             "title": collection.get("title") or collection.get("id"),
        #             "href": urljoin(base_url, f"collections/{collection['id']}"),
        #         }
        #     )

        # Add Collections links
        catalogs = await self.all_catalogs(request=kwargs["request"])
        for catalog in catalogs["collections"]:
            landing_page["links"].append(
                {
                    "rel": Relations.child.value,
                    "type": MimeTypes.json.value,
                    "title": catalog.get("title") or catalog.get("id"),
                    "href": urljoin(base_url, f"collections/{catalog['id']}"),
                }
            )

        # Add OpenAPI URL
        landing_page["links"].append(
            {
                "rel": "service-desc",
                "type": "application/vnd.oai.openapi+json;version=3.0",
                "title": "OpenAPI service description",
                "href": urljoin(base_url, request.app.openapi_url.lstrip("/")),
            }
        )

        # Add human readable service-doc
        landing_page["links"].append(
            {
                "rel": "service-doc",
                "type": "text/html",
                "title": "OpenAPI service documentation",
                "href": urljoin(base_url, request.app.docs_url.lstrip("/")),
            }
        )

        return landing_page

    async def conformance(self, **kwargs) -> stac_types.Conformance:
        """Conformance classes.

        Called with `GET /conformance`.

        Returns:
            Conformance classes which the server conforms to.
        """
        return Conformance(conformsTo=self.conformance_classes())

    @abc.abstractmethod
    async def post_global_search(
        self, search_request: BaseSearchPostRequest, **kwargs
    ) -> stac_types.ItemCollection:
        """Cross catalog search (POST).

        Called with `POST /search`.

        Args:
            search_request: search request parameters.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    async def get_global_search(
        self,
        catalogs: Optional[List[str]] = None,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: Optional[int] = 10,
        query: Optional[str] = None,
        token: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sortby: Optional[str] = None,
        intersects: Optional[str] = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Cross catalog search (GET).

        Called with `GET /search`.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    async def get_search(
        self,
        catalog_id: str,
        collections: Optional[List[str]] = None,
        ids: Optional[List[str]] = None,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: Optional[int] = 10,
        query: Optional[str] = None,
        token: Optional[str] = None,
        fields: Optional[List[str]] = None,
        sortby: Optional[str] = None,
        intersects: Optional[str] = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Single catalog item search (GET).

        Called with `GET /catalogs/{catalog_id}/search`.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    async def post_search(
        self, catalog_id: str, search_request: BaseCatalogSearchPostRequest, **kwargs
    ) -> stac_types.ItemCollection:
        """Single catalog item search (POST).

        Called with `POST /catalogs/{catalog_id}/search`.

        Args:
            search_request: search request parameters.

        Returns:
            ItemCollection containing items which match the search criteria.
        """
        ...

    @abc.abstractmethod
    async def get_item(
        self, item_id: str, collection_id: str, catalog_id: str, **kwargs
    ) -> stac_types.Item:
        """Get item by id.

        Called with `GET /catalogs/{catalog_id}/collections/{collection_id}/items/{item_id}`.

        Args:
            item_id: Id of the item.
            collection_id: Id of the collection.

        Returns:
            Item.
        """
        ...

    @abc.abstractmethod
    async def all_collections(self, **kwargs) -> stac_types.Collections:
        """Get all available collections.

        Called with `GET /collections`.

        Returns:
            A list of collections.
        """
        ...

    @abc.abstractmethod
    async def all_catalogs(self, **kwargs) -> stac_types.Catalogs:
        """Get all available catalogs.

        Called with `GET /catalogs`.

        Returns:
            A list of catalogs.
        """
        ...

    @abc.abstractmethod
    async def get_collection(
        self, collection_id: str, **kwargs
    ) -> stac_types.Collection:
        """Get collection by id.

        Called with `GET /catalogs/{catalog_id}/collections/{collection_id}`.

        Args:
            collection_id: Id of the collection.

        Returns:
            Collection.
        """
        ...

    @abc.abstractmethod
    async def get_catalog(self, catalog_id: str, **kwargs) -> stac_types.Catalog:
        """Get catalog by id.

        Called with `GET /catalogs/{catalog_id}`.

        Args:
            catalog_id: Id of the catalog.

        Returns:
            Catalog.
        """
        ...

    @abc.abstractmethod
    async def item_collection(
        self,
        collection_id: str,
        bbox: Optional[BBox] = None,
        datetime: Optional[DateTimeType] = None,
        limit: int = 10,
        token: str = None,
        **kwargs,
    ) -> stac_types.ItemCollection:
        """Get all items from a specific collection.

        Called with `GET /catalogs/{catalog_id}/collections/{collection_id}/items`

        Args:
            collection_id: id of the collection.
            limit: number of items to return.
            token: pagination token.

        Returns:
            An ItemCollection.
        """
        ...


@attr.s
class AsyncBaseFiltersClient(abc.ABC):
    """Defines a pattern for implementing the STAC filter extension."""

    async def get_queryables(
        self, collection_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get the queryables available for the given collection_id.

        If collection_id is None, returns the intersection of all queryables over all
        collections.

        This base implementation returns a blank queryable schema. This is not allowed
        under OGC CQL but it is allowed by the STAC API Filter Extension
        https://github.com/radiantearth/stac-api-spec/tree/master/fragments/filter#queryables
        """
        return {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "https://example.org/queryables",
            "type": "object",
            "title": "Queryables for Example STAC API",
            "description": "Queryable names for the example STAC API Item Search filter.",
            "properties": {},
        }


@attr.s
class BaseFiltersClient(abc.ABC):
    """Defines a pattern for implementing the STAC filter extension."""

    def get_queryables(
        self, collection_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Get the queryables available for the given collection_id.

        If collection_id is None, returns the intersection of all queryables over all
        collections.

        This base implementation returns a blank queryable schema. This is not allowed
        under OGC CQL but it is allowed by the STAC API Filter Extension
        https://github.com/stac-api-extensions/filter#queryables
        """
        return {
            "$schema": "https://json-schema.org/draft/2019-09/schema",
            "$id": "https://example.org/queryables",
            "type": "object",
            "title": "Queryables for Example STAC API",
            "description": "Queryable names for the example STAC API Item Search filter.",
            "properties": {},
        }


@attr.s
class AsyncBaseCollectionSearchClient(abc.ABC):
    """Defines a pattern for implementing the STAC Collection Search extension."""

    async def post_all_collections(
        self, search_request: BaseCollectionSearchPostRequest, **kwargs
    ) -> stac_types.Collections:
        """Get all available collections.
        Called with `GET /collections`.
        Returns:
            A list of collections.
        """
        return stac_types.Collections(collections=[])


@attr.s
class BaseCollectionSearchClient(abc.ABC):
    """Defines a pattern for implementing the STAC Collection Search extension."""

    async def post_all_collections(
        self, search_request: BaseCollectionSearchPostRequest, **kwargs
    ) -> stac_types.Collections:
        """Get all available collections.
        Called with `GET /collections`.
        Returns:
            A list of collections.
        """
        return stac_types.Collections(collections=[])


@attr.s
class AsyncDiscoverySearchClient(abc.ABC):
    """Defines a pattern for implementing the STAC Collection Search extension."""

    @abc.abstractmethod
    async def post_discovery_search(
        self, search_request: BaseDiscoverySearchPostRequest, **kwargs
    ) -> stac_types.Collections:
        """Cross catalog search (POST) of collections.

        Called with `POST /collection-search`.

        Args:
            search_request: search request parameters.

        Returns:
            A tuple of (collections, next pagination token if any).
        """
        ...

    @abc.abstractmethod
    async def get_discovery_search(
        self,
        q: Optional[str] = None,
        limit: Optional[int] = 10,
        **kwargs,
    ) -> stac_types.Collections:
        """Cross catalog search (GET) of collections.

        Called with `GET /collection-search`.

        Returns:
            A tuple of (collections, next pagination token if any).
        """
        ...


@attr.s
class DiscoverySearchClient(abc.ABC):
    """Defines a pattern for implementing the STAC Collection Search extension."""

    @abc.abstractmethod
    def post_discovery_search(
        self, search_request: BaseDiscoverySearchPostRequest, **kwargs
    ) -> stac_types.Collections:
        """Cross catalog search (POST) of collections.

        Called with `POST /collection-search`.

        Args:
            search_request: search request parameters.

        Returns:
            A tuple of (collections, next pagination token if any).
        """
        ...

    @abc.abstractmethod
    def get_discovery_search(
        self,
        q: Optional[str] = None,
        limit: Optional[int] = 10,
        **kwargs,
    ) -> stac_types.Collections:
        """Cross catalog search (GET) of collections.

        Called with `GET /collection-search`.

        Returns:
            A tuple of (collections, next pagination token if any).
        """
        ...
