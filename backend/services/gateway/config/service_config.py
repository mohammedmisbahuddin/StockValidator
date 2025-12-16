"""
Service configuration for API Gateway
Defines routing to backend services
"""
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.config import settings


class ServiceConfig:
    """Configuration for backend services"""
    
    # Service base URLs
    AUTH_SERVICE_URL: str = getattr(settings, 'AUTH_SERVICE_URL', 'http://localhost:8001')
    STOCK_SERVICE_URL: str = getattr(settings, 'STOCK_SERVICE_URL', 'http://localhost:8002')
    NOTIFICATION_SERVICE_URL: str = getattr(settings, 'NOTIFICATION_SERVICE_URL', 'http://localhost:8003')
    
    # Route mapping: Gateway path prefix → Service URL
    ROUTES: Dict[str, str] = {
        '/api/auth': AUTH_SERVICE_URL,
        '/api/stocks': STOCK_SERVICE_URL,
        '/api/notifications': NOTIFICATION_SERVICE_URL,
    }
    
    @classmethod
    def get_service_url(cls, path: str) -> Optional[tuple[str, str]]:
        """
        Get service URL for a given path
        
        Args:
            path: Request path (e.g., '/api/auth/login')
        
        Returns:
            Tuple of (service_url, service_path) or None if not found
            Example: ('http://localhost:8001', '/auth/login')
        """
        # Find matching route prefix
        for prefix, service_url in cls.ROUTES.items():
            if path.startswith(prefix):
                # Remove '/api' prefix, keep service name
                # /api/auth/login → /auth/login
                service_path = path[4:]  # Remove '/api'
                if not service_path.startswith('/'):
                    service_path = '/' + service_path
                return service_url, service_path
        
        return None
    
    @classmethod
    def get_all_routes(cls) -> Dict[str, str]:
        """Get all route mappings"""
        return cls.ROUTES.copy()


def get_service_config() -> ServiceConfig:
    """Get service configuration instance"""
    return ServiceConfig()

