"""HTTPS reverse proxy to ACI backend with full request/response handling"""

import os
import logging
import httpx
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="QR Forge HTTPS Proxy")

# Backend ACI URL
BACKEND_URL = "http://qrforge-app-prod.northeurope.azurecontainer.io:8000"

# Headers to strip when proxying
HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

PROXY_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]


def should_forward_header(name: str) -> bool:
    """Check if header should be forwarded to backend"""
    return name.lower() not in HOP_BY_HOP_HEADERS


async def forward_request(
    method: str,
    path: str,
    request: Request,
    body: Optional[bytes],
) -> Response:
    """Forward request to backend ACI and return response"""
    backend_url = f"{BACKEND_URL}/{path.lstrip('/')}"

    # Preserve query string
    if request.url.query:
        backend_url = f"{backend_url}?{request.url.query}"

    # Filter headers
    headers = {
        name: value
        for name, value in request.headers.items()
        if should_forward_header(name)
    }

    logger.info(f"{method} {path} -> {backend_url} (body={len(body) if body else 0}B)")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method=method,
                url=backend_url,
                headers=headers,
                content=body,
                follow_redirects=False,  # Don't follow redirects automatically
            )

            # Stream response body
            async def stream_body():
                async for chunk in response.aiter_bytes(chunk_size=16384):
                    yield chunk

            return StreamingResponse(
                stream_body(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to backend for {method} {path}")
        return Response(
            '{"error":"Backend timeout"}',
            status_code=504,
            media_type="application/json",
        )
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to backend: {e}")
        return Response(
            '{"error":"Backend unavailable"}',
            status_code=503,
            media_type="application/json",
        )
    except Exception as e:
        logger.exception(f"Proxy error for {method} {path}: {e}")
        return Response(
            f'{{"error":"Proxy error: {str(e)}"}}',
            status_code=502,
            media_type="application/json",
        )


@app.api_route("/{path:path}", methods=PROXY_METHODS)
async def proxy(request: Request, path: str):
    """Proxy all requests to ACI backend"""
    # Read body if method supports it
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()

    return await forward_request(
        method=request.method,
        path=path,
        request=request,
        body=body,
    )


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "QR Forge HTTPS Proxy",
        "status": "online",
        "backend": BACKEND_URL,
        "version": "1.0.0",
    }


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "healthy"}


@app.get("/ping", include_in_schema=False)
async def ping():
    return {"pong": True}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WEBSITES_PORT", 8000))
    logger.info(f"Starting proxy on 0.0.0.0:{port} -> {BACKEND_URL}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
