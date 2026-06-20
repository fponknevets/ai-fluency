"""HTTP client wrapper for API requests with Bearer token support."""
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    """Wrapper around requests.Session with Bearer token support."""
    
    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Optional base URL for requests
            token: Optional JWT token for Bearer authentication
        """
        self.session = requests.Session()
        self.base_url = base_url.rstrip("/") if base_url else ""
        self.token = token
        # Extract root URL (scheme + netloc) for root-level endpoints
        if self.base_url:
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            self.root_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            self.root_url = ""
        self._update_headers()
    
    def set_token(self, token: str):
        """Set or update JWT token for subsequent requests."""
        self.token = token
        self._update_headers()
    
    def _update_headers(self):
        """Update default headers with Bearer token if available."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"
        self.session.headers.update(headers)
    
    def _build_url(self, endpoint: str, use_root: bool = False) -> str:
        """
        Build full URL from base and endpoint.
        
        Args:
            endpoint: API endpoint path
            use_root: If True, use root URL (for root-level endpoints like /health)
        
        Returns:
            Full URL string
        """
        endpoint = endpoint.lstrip("/")
        if use_root and self.root_url:
            return f"{self.root_url}/{endpoint}"
        elif self.base_url:
            return f"{self.base_url}/{endpoint}"
        return endpoint
    
    def get(self, endpoint: str, use_root: bool = False, **kwargs) -> requests.Response:
        """Send GET request."""
        url = self._build_url(endpoint, use_root=use_root)
        logger.debug(f"GET {url}")
        try:
            response = self.session.get(url, **kwargs)
            logger.debug(f"Response: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"GET request failed: {e}")
            raise
    
    def post(self, endpoint: str, json: Dict = None, use_root: bool = False, **kwargs) -> requests.Response:
        """Send POST request."""
        url = self._build_url(endpoint, use_root=use_root)
        logger.debug(f"POST {url}")
        try:
            response = self.session.post(url, json=json, **kwargs)
            logger.debug(f"Response: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"POST request failed: {e}")
            raise
    
    def put(self, endpoint: str, json: Dict = None, use_root: bool = False, **kwargs) -> requests.Response:
        """Send PUT request."""
        url = self._build_url(endpoint, use_root=use_root)
        logger.debug(f"PUT {url}")
        try:
            response = self.session.put(url, json=json, **kwargs)
            logger.debug(f"Response: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"PUT request failed: {e}")
            raise
    
    def delete(self, endpoint: str, use_root: bool = False, **kwargs) -> requests.Response:
        """Send DELETE request."""
        url = self._build_url(endpoint, use_root=use_root)
        logger.debug(f"DELETE {url}")
        try:
            response = self.session.delete(url, **kwargs)
            logger.debug(f"Response: {response.status_code}")
            return response
        except requests.RequestException as e:
            logger.error(f"DELETE request failed: {e}")
            raise
    
    def close(self):
        """Close the session."""
        self.session.close()
