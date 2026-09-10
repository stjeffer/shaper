"""Single-process hosted ASGI composition for HTTP and MCP."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from shaper.interfaces.http import HttpServices, create_app


def create_hosted_app(
    services: HttpServices,
    mcp_server: FastMCP,
    *,
    on_startup: Callable[[], None] | None = None,
    on_shutdown: Callable[[], None] | None = None,
) -> FastAPI:
    """Mount authenticated MCP under HTTP with one coordinated lifespan."""

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if on_startup is not None:
            on_startup()
        try:
            async with mcp_server.session_manager.run():
                yield
        finally:
            if on_shutdown is not None:
                on_shutdown()

    app = create_app(services)
    app.router.lifespan_context = lifespan
    app.mount("/mcp", mcp_server.streamable_http_app())
    return app
