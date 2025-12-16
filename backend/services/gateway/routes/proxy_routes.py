"""
Proxy routes for API Gateway
Forwards requests to appropriate backend services
"""
import httpx
from fastapi import APIRouter, Request, Response, HTTPException, status
from fastapi.responses import StreamingResponse
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from config.service_config import ServiceConfig

logger = logging.getLogger(__name__)

router = APIRouter()


@router.api_route("/api/{service_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(service_path: str, request: Request):
    """
    Proxy request to appropriate backend service
    
    Routes:
    - /api/auth/* → Auth Service (8001)
    - /api/stocks/* → Stock Service (8002)
    - /api/notifications/* → Notification Service (8003)
    """
    # Construct full path
    full_path = f"/api/{service_path}"
    
    # Get service URL and path
    service_info = ServiceConfig.get_service_url(full_path)
    
    if not service_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No service found for path: {full_path}"
        )
    
    service_url, target_path = service_info
    
    # Ensure target_path starts with /
    if not target_path.startswith('/'):
        target_path = '/' + target_path
    
    # Build target URL
    target_url = f"{service_url}{target_path}"
    
    # Get query parameters
    query_params = dict(request.query_params)
    if query_params:
        query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
        target_url = f"{target_url}?{query_string}"
    
    logger.info(f"Proxying {request.method} {full_path} → {target_url}")
    
    # Get request body
    body = await request.body()
    
    # Get headers (exclude host and connection headers)
    headers = {}
    for key, value in request.headers.items():
        # Skip headers that shouldn't be forwarded
        if key.lower() in ["host", "connection", "content-length", "content-encoding", "transfer-encoding"]:
            continue
        # Ensure header values are strings
        headers[key] = str(value) if not isinstance(value, str) else value
    
    try:
        # Forward request to backend service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                content=body if body else None,
                headers=headers,
                follow_redirects=False
            )
            
            # Get response content
            content = response.content
            
            # Build response headers (exclude some that shouldn't be forwarded)
            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)
            response_headers.pop("transfer-encoding", None)
            response_headers.pop("connection", None)
            
            # Return response
            return Response(
                content=content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout forwarding request to {target_url}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Backend service timeout"
        )
    except httpx.ConnectError:
        logger.error(f"Connection error forwarding to {target_url}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Backend service unavailable: {service_url}"
        )
    except Exception as e:
        logger.error(f"Error forwarding request: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gateway error: {str(e)}"
        )


@router.get("/api")
async def api_info():
    """API Gateway information"""
    routes = ServiceConfig.get_all_routes()
    return {
        "gateway": "StockValidator API Gateway",
        "version": "1.0.0",
        "routes": {
            prefix: url for prefix, url in routes.items()
        },
        "documentation": "/docs"
    }

