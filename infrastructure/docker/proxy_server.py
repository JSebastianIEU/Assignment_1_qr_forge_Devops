"""
Minimal HTTPS-friendly reverse proxy for QR Forge.

Environment variables:
- TARGET_URL: upstream FastAPI service (default http://backend:8000)
- REQUEST_TIMEOUT: seconds for upstream requests (default 15)
"""

from __future__ import annotations

import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

TARGET_URL = os.getenv("TARGET_URL", "http://backend:8000")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "15"))

app = FastAPI(title="QR Forge HTTPS Proxy", docs_url=None, redoc_url=None)


@app.get("/health", include_in_schema=False)
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(full_path: str, request: Request) -> Response:
    # Build target URL
    url = httpx.URL(f"{TARGET_URL}/{full_path}").copy_with(query=request.url.query.encode("utf-8"))

    # Read body (if any)
    body = await request.body()

    # Forward headers (strip host so upstream sets its own)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            upstream_response = await client.request(
                request.method,
                url,
                content=body,
                headers=headers,
            )
    except httpx.RequestError as exc:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Upstream request failed: {exc}"},
        )

    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=upstream_response.headers,
        media_type=upstream_response.headers.get("content-type"),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
