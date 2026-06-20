"""Tests for JWT security and authentication."""
import pytest
import logging

logger = logging.getLogger(__name__)


class TestJWTSecurity:
    """Test suite for JWT token validation and security."""
    
    def test_health_without_token(self):
        """
        Test that health endpoint is accessible without JWT token.
        
        Note: Health endpoints are typically public for monitoring.
        This test verifies the endpoint works without auth.
        """
        logger.info("Testing health endpoint without JWT token")
        
        from config.http_client import HTTPClient
        from config.config import TASK_SERVICE_URL
        
        # Create client WITHOUT token
        client = HTTPClient(base_url=TASK_SERVICE_URL, token=None)
        response = client.get("/health", use_root=True)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text}")
        
        # Health endpoints are typically public
        assert response.status_code == 200, (
            f"Expected 200 for public health endpoint, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        data = response.json()
        assert isinstance(data, dict), "Health response should be a JSON object"
        
        client.close()
        logger.info("Health endpoint accessibility test PASSED")
    
    def test_task_creation_without_token(self):
        """
        Test that task creation fails without JWT token.
        
        Expected behavior:
        - Status code 401 (Unauthorized) or 403 (Forbidden)
        """
        logger.info("Testing task creation without JWT token")
        
        from config.http_client import HTTPClient
        from config.config import TASK_SERVICE_URL
        
        # Create client WITHOUT token
        client = HTTPClient(base_url=TASK_SERVICE_URL, token=None)
        
        task_data = {
            "title": "Test Task",
            "description": "Should fail without token"
        }
        
        response = client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code in (401, 403), (
            f"Expected 401 or 403, got {response.status_code}. "
            f"Task creation should require JWT authentication."
        )
        
        client.close()
        logger.info("No-token task creation test PASSED")
    
    def test_invalid_token_format(self, task_service_client):
        """
        Test that invalid token format is rejected.
        
        Expected behavior:
        - Status code 401 (Unauthorized)
        """
        logger.info("Testing invalid token format")
        
        from config.http_client import HTTPClient
        from config.config import TASK_SERVICE_URL
        
        # Create client with malformed token
        client = HTTPClient(base_url=TASK_SERVICE_URL, token="invalid.token.format")
        
        response = client.get("/tasks")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 401, (
            f"Expected 401, got {response.status_code}. "
            f"Invalid token should be rejected."
        )
        
        client.close()
        logger.info("Invalid token format test PASSED")
    
    def test_empty_token(self):
        """
        Test that empty token is rejected.
        
        Expected behavior:
        - Status code 401 (Unauthorized)
        """
        logger.info("Testing empty token")
        
        from config.http_client import HTTPClient
        from config.config import TASK_SERVICE_URL
        
        # Create client with empty token
        client = HTTPClient(base_url=TASK_SERVICE_URL, token="")
        
        response = client.get("/tasks")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 401, (
            f"Expected 401, got {response.status_code}. "
            f"Empty token should be rejected."
        )
        
        client.close()
        logger.info("Empty token test PASSED")
    
    def test_bearer_prefix_required(self):
        """
        Test that Bearer token is properly formatted with prefix.
        
        Expected behavior:
        - Valid JWT should work with Bearer prefix
        - Response status should be 200 for valid token
        """
        logger.info("Testing Bearer token prefix")
        
        from config.http_client import HTTPClient
        from config.config import TASK_SERVICE_URL, IDENTITY_SERVICE_URL
        from config.auth import get_or_create_test_user_token
        
        # Get valid token (Identity Service URL is already correct)
        token = get_or_create_test_user_token(IDENTITY_SERVICE_URL)
        
        # The HTTPClient should automatically add Bearer prefix
        client = HTTPClient(base_url=TASK_SERVICE_URL, token=token)
        
        response = client.get("/tasks")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, (
            f"Expected 200 with valid Bearer token, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Bearer prefix test PASSED")
