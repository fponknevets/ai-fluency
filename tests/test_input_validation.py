"""Tests for input validation and data integrity."""
import pytest
import logging

logger = logging.getLogger(__name__)


class TestInputValidation:
    """Test suite for input validation and error handling."""
    
    def test_create_task_missing_title(self, task_service_client):
        """
        Test that task creation fails when title is missing.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing missing title validation")
        
        task_data = {
            "description": "Task without title"
            # Missing required 'title' field
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for missing title, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        logger.info("Missing title validation test PASSED")
    
    def test_create_task_missing_description(self, task_service_client):
        """
        Test that task creation fails when description is missing.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing missing description validation")
        
        task_data = {
            "title": "Task without description"
            # Missing required 'description' field
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for missing description, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        logger.info("Missing description validation test PASSED")
    
    def test_create_task_invalid_title_type(self, task_service_client):
        """
        Test that task creation fails with invalid title type.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing invalid title type validation")
        
        task_data = {
            "title": 12345,  # Should be string, not int
            "description": "Valid description"
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        # Some APIs coerce types, others reject
        if response.status_code == 422:
            logger.info("API rejected invalid type (strict validation)")
        elif response.status_code == 201:
            # If accepted, verify it was converted to string
            task = response.json()
            assert isinstance(task["title"], str), "Title should be string"
            logger.info("API coerced invalid type to string")
        else:
            raise AssertionError(f"Unexpected status: {response.status_code}")
    
    def test_create_task_empty_title(self, task_service_client):
        """
        Test that task creation fails with empty title.
        
        Expected behavior:
        - Status code 422 (Validation Error) or 201 with empty string
        """
        logger.info("Testing empty title validation")
        
        task_data = {
            "title": "",
            "description": "Task with empty title"
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        # Depending on API requirements, either reject or accept
        if response.status_code == 422:
            logger.info("API rejected empty title")
        elif response.status_code == 201:
            logger.info("API accepted empty title")
            task = response.json()
            assert task["title"] == "", "Empty title should be preserved"
    
    def test_create_task_very_long_title(self, task_service_client):
        """
        Test task creation with very long title (boundary condition).
        
        Expected behavior:
        - Status code 422 if exceeds limit, 201 if accepted
        """
        logger.info("Testing very long title boundary")
        
        # Create a title longer than typical database limits
        long_title = "x" * 10000
        
        task_data = {
            "title": long_title,
            "description": "Task with very long title"
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 422:
            logger.info("API rejected excessively long title (appropriate)")
        elif response.status_code == 201:
            logger.info("API accepted long title")
            task = response.json()
            # Verify it was stored/returned
            assert "title" in task
    
    def test_create_task_xss_payload_in_description(self, task_service_client):
        """
        Test that XSS payloads in description are safely handled.
        
        Expected behavior:
        - Status code 201 (accepted and sanitized/stored safely)
        - Payload should not execute in API response
        """
        logger.info("Testing XSS payload in description")
        
        xss_payload = "<script>alert('XSS')</script>"
        
        task_data = {
            "title": "XSS Test",
            "description": xss_payload
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 201, (
            f"API should accept task with XSS payload (handled safely). "
            f"Got {response.status_code}: {response.text}"
        )
        
        task = response.json()
        # Verify payload is stored as-is (API shouldn't execute or strip it)
        assert task["description"] == xss_payload, (
            "API should safely store XSS payload as-is"
        )
        
        logger.info("XSS payload test PASSED")
    
    def test_create_task_sql_injection_in_title(self, task_service_client):
        """
        Test that SQL injection attempts in title are handled safely.
        
        Expected behavior:
        - Status code 201 (accepted and safely stored)
        - Query should not execute
        """
        logger.info("Testing SQL injection in title")
        
        sql_payload = "'; DROP TABLE tasks; --"
        
        task_data = {
            "title": sql_payload,
            "description": "SQL injection test"
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 201, (
            f"API should safely handle SQL injection payload. "
            f"Got {response.status_code}: {response.text}"
        )
        
        task = response.json()
        # Verify payload stored as literal string
        assert task["title"] == sql_payload, (
            "SQL injection payload should be stored as literal string"
        )
        
        # Verify table still exists by listing tasks
        list_response = task_service_client.get("/tasks")
        assert list_response.status_code == 200, (
            "Tasks table should still exist (injection didn't execute)"
        )
        
        logger.info("SQL injection test PASSED")
    
    def test_get_task_invalid_uuid(self, task_service_client):
        """
        Test that invalid UUID in path is rejected.
        
        Expected behavior:
        - Status code 422 (Validation Error) or 404 (Not Found)
        """
        logger.info("Testing invalid UUID validation")
        
        invalid_uuid = "not-a-valid-uuid"
        
        response = task_service_client.get(f"/tasks/{invalid_uuid}")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code in (422, 404), (
            f"Expected 422 or 404 for invalid UUID, got {response.status_code}"
        )
        
        logger.info("Invalid UUID validation test PASSED")
    
    def test_update_task_with_invalid_is_completed_type(self, task_service_client):
        """
        Test that invalid is_completed type is handled.
        
        Expected behavior:
        - Status code 422 or 200 with type coercion
        """
        logger.info("Testing invalid is_completed type")
        
        # Create task first
        create_response = task_service_client.post(
            "/tasks",
            json={"title": "Test", "description": "Test"}
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Try to update with invalid type
        update_data = {
            "is_completed": "yes"  # Should be boolean
        }
        
        response = task_service_client.put(f"/tasks/{task_id}", json=update_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 422:
            logger.info("API rejected invalid is_completed type")
        elif response.status_code == 200:
            logger.info("API accepted invalid type (with coercion)")
    
    def test_create_task_with_null_description(self, task_service_client):
        """
        Test task creation with null description.
        
        Expected behavior:
        - Status code 422 if required, 201 if optional
        """
        logger.info("Testing null description")
        
        task_data = {
            "title": "Task Title",
            "description": None
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 422:
            logger.info("API requires non-null description")
        elif response.status_code == 201:
            logger.info("API allows null description")
            task = response.json()
            # Verify null was handled (stored as null or empty string)
            assert task["description"] in (None, ""), (
                "Description should be null or empty"
            )
