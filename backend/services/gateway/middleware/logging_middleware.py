"""
Logging middleware for API Gateway
Logs all requests and responses
"""
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response"""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"→ {request.method} {request.url.path} "
            f"[Client: {request.client.host if request.client else 'unknown'}]"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[Status: {response.status_code}] "
            f"[Duration: {duration:.3f}s]"
        )
        
        return response

