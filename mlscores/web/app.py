#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""FastAPI application for mlscores web interface."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="mlscores API",
        description="""
Multilinguality score calculator for Wikidata/Wikibase items.

This API allows you to calculate the percentage of labels and property values
available in multiple languages for Wikidata items, helping identify translation gaps.

## Features

- Calculate multilinguality scores for one or more items
- Filter by specific languages
- Get detailed missing translation information
- JSON and CSV output formats

## Usage Examples

### Calculate scores for a single item
```
GET /api/scores/Q42?languages=en&languages=fr
```

### Calculate scores for multiple items
```
POST /api/scores
{
    "identifiers": ["Q42", "Q5"],
    "languages": ["en", "fr", "es"],
    "include_missing": true
}
```
        """,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Include API routes
    app.include_router(router, prefix="/api")

    # Serve static files
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        @app.get("/")
        async def serve_frontend():
            """Serve the frontend HTML."""
            return FileResponse(static_dir / "index.html")

    return app


# Application instance
app = create_app()


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """
    Run the web server.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)
