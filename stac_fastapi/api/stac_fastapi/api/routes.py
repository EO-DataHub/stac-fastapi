"""Route factories."""

import functools
import inspect
import warnings
from typing import Any, Callable, Dict, List, Optional, Type, TypedDict, Union

from fastapi import Depends, params
from fastapi.dependencies.utils import get_parameterless_sub_dependant
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import BaseRoute, Match
from starlette.status import HTTP_204_NO_CONTENT

from stac_fastapi.api.models import APIRequest

import jwt


def _wrap_response(resp: Any) -> Any:
    if resp is not None:
        return resp
    else:  # None is returned as 204 No Content
        return Response(status_code=HTTP_204_NO_CONTENT)


def sync_to_async(func):
    """Run synchronous function asynchronously in a background thread."""

    @functools.wraps(func)
    async def run(*args, **kwargs):
        return await run_in_threadpool(func, *args, **kwargs)

    return run

# Define the OAuth2 scheme for Bearer token
bearer_scheme = HTTPBearer(auto_error=False)

# TODO: Also extract group information from the headers
def extract_headers(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, str]:
        """Extract headers from request.

        Args:
            token: The OAuth2 token extracted from the Authorization header.

        Returns:
            Dict of headers.
        """
        if credentials:
            decoded_jwt = jwt.decode(credentials.credentials, options={"verify_signature": False}, algorithms=["HS256"])
            username = decoded_jwt.get("preferred_username")
        else:
            username = ""

        return {"X-Username": username} # Allows support for more headers in future, e.g. group information


def create_async_endpoint(
    func: Callable,
    request_model: Union[Type[APIRequest], Type[BaseModel], Dict],
    response_class: Optional[Type[Response]] = None,
):
    """Wrap a function in a coroutine which may be used to create a FastAPI endpoint.

    Synchronous functions are executed asynchronously using a background thread.
    """

    if response_class:
        warnings.warn(
            "`response_class` option is deprecated, please set the Response class directly in the endpoint.",  # noqa: E501
            DeprecationWarning,
        )

    if not inspect.iscoroutinefunction(func):
        func = sync_to_async(func)

    if issubclass(request_model, APIRequest):

        async def _endpoint(
            request: Request,
            request_data: request_model = Depends(),  # type:ignore
            username_header = Depends(extract_headers),
        ):
            """Endpoint."""
            return _wrap_response(await func(request=request, username_header=username_header, **request_data.kwargs()))

    elif issubclass(request_model, BaseModel):

        async def _endpoint(
            request: Request,
            request_data: request_model,  # type:ignore
            username_header = Depends(extract_headers),
        ):
            """Endpoint."""
            return _wrap_response(await func(request_data, username_header=username_header, request=request))

    else:

        async def _endpoint(
            request: Request,
            request_data: Dict[str, Any],  # type:ignore
            username_header = Depends(extract_headers),
        ):
            """Endpoint."""
            return _wrap_response(await func(request_data, username_header=username_header, request=request))

    return _endpoint


class Scope(TypedDict, total=False):
    """More strict version of Starlette's Scope."""

    # https://github.com/encode/starlette/blob/6af5c515e0a896cbf3f86ee043b88f6c24200bcf/starlette/types.py#L3
    path: str
    method: str
    type: Optional[str]


def add_route_dependencies(
    routes: List[BaseRoute], scopes: List[Scope], dependencies=List[params.Depends]
) -> None:
    """Add dependencies to routes.

    Allows a developer to add dependencies to a route after the route has been
    defined.

    Returns:
        None
    """
    for scope in scopes:
        for route in routes:
            match, _ = route.matches({"type": "http", **scope})
            if match != Match.FULL:
                continue

            # Mimicking how APIRoute handles dependencies:
            # https://github.com/tiangolo/fastapi/blob/1760da0efa55585c19835d81afa8ca386036c325/fastapi/routing.py#L408-L412
            for depends in dependencies[::-1]:
                route.dependant.dependencies.insert(
                    0,
                    get_parameterless_sub_dependant(
                        depends=depends, path=route.path_format
                    ),
                )

            # Register dependencies directly on route so that they aren't ignored if
            # the routes are later associated with an app (e.g.
            # app.include_router(router))
            # https://github.com/tiangolo/fastapi/blob/58ab733f19846b4875c5b79bfb1f4d1cb7f4823f/fastapi/applications.py#L337-L360
            # https://github.com/tiangolo/fastapi/blob/58ab733f19846b4875c5b79bfb1f4d1cb7f4823f/fastapi/routing.py#L677-L678
            route.dependencies.extend(dependencies)
