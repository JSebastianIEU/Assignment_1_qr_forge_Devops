"""Simple HTTPS reverse proxy to ACI backend"""
import os
import requests
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Backend ACI URL
BACKEND_URL = "http://qrforge-app-prod.northeurope.azurecontainer.io:8000"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy(request: Request, path: str):
    """Proxy all requests to ACI backend"""
    try:
        # Construct backend URL
        url = f"{BACKEND_URL}/{path}"
        
        # Copy query params
        if request.url.query:
            url = f"{url}?{request.url.query}"
        
        # Read body if present
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Make request to backend
        response = requests.request(
            method=request.method,
            url=url,
            headers={
                key: value 
                for key, value in request.headers.items()
                if key.lower() not in ["host", "connection"]
            },
            data=body,
            stream=True,
            timeout=60
        )
        
        # Return response
        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return Response(f"Gateway error: {str(e)}", status_code=502)

@app.get("/")
async def root():
    return {"status": "HTTPS Proxy to ACI active", "backend": BACKEND_URL}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("WEBSITES_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
