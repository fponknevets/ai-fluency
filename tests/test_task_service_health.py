"""Tests for Task Service health endpoint."""
import pytest
import logging

logger = logging.getLogger(__name__)


class TestTaskServiceHealth:
    """Test suite for Task Service health checks."""
    
    def test_health_endpoint_with_jwt(self, task_service_client):
        """
        Test that health endpoint is accessible with valid JWT token.
        
        Expected behavior:
        - Status code 200 (OK)
        - Response body contains health status information
        """
        logger.info("Testing Task Service health endpoint")
        
        # Send GET request to health endpoint (root-level, not under /api/v1)
        response = task_service_client.get("/health", use_root=True)
        
        # Assert successful response
        assert response.status_code == 200, (
            f"Expected status 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        # Assert response is valid JSON
        data = response.json()
        logger.info(f"Health response: {data}")
        
        # Verify response is a dict (schema is empty but should return object)
        assert isinstance(data, dict), "Health response should be a JSON object"
        
        logger.info("Health endpoint test PASSED")
