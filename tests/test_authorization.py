"""Tests for authorization and access control (RBAC)."""
import pytest
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def second_user_client():
    """
    Create a second authenticated user for testing access control.
    
    Yields:
        HTTPClient authenticated with a different user's JWT
    """
    from config.http_client import HTTPClient
    from config.config import TASK_SERVICE_URL, IDENTITY_SERVICE_URL
    from config.auth import get_or_create_test_user_token
    
    logger.info("Creating second user for access control testing")
    token = get_or_create_test_user_token(IDENTITY_SERVICE_URL)
    client = HTTPClient(base_url=TASK_SERVICE_URL, token=token)
    
    yield client
    client.close()


class TestAuthorization:
    """Test suite for authorization and access control."""
    
    def test_user_can_create_own_tasks(self, task_service_client):
        """
        Test that authenticated user can create tasks.
        
        Expected behavior:
        - Task is created with correct user_id
        - Task appears in user's task list
        """
        logger.info("Testing user can create own tasks")
        
        task_data = {
            "title": "User's Own Task",
            "description": "This task belongs to the user"
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}. Response: {response.text}"
        )
        
        task = response.json()
        
        # Verify task has user_id (proves ownership)
        assert "user_id" in task, "Task should have user_id field"
        assert task["user_id"], "Task user_id should not be empty"
        
        logger.info(f"Task created with user_id: {task['user_id']}")
        logger.info("User can create own tasks test PASSED")
    
    def test_task_ownership_integrity(self, task_service_client):
        """
        Test that retrieved tasks have correct user_id.
        
        Expected behavior:
        - All tasks belong to the authenticated user
        - user_id is consistent across GET operations
        """
        logger.info("Testing task ownership integrity")
        
        # Create a task
        task_data = {
            "title": "Ownership Test Task",
            "description": "Testing ownership verification"
        }
        
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        created_task = create_response.json()
        task_id = created_task["id"]
        user_id = created_task["user_id"]
        
        # Get the task individually
        get_response = task_service_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        
        retrieved_task = get_response.json()
        
        # Verify user_id is consistent
        assert retrieved_task["user_id"] == user_id, (
            "Task user_id should remain consistent across operations"
        )
        
        logger.info("Task ownership integrity test PASSED")
    
    def test_list_tasks_shows_only_user_tasks(self, task_service_client):
        """
        Test that listing tasks returns only current user's tasks.
        
        Expected behavior:
        - All returned tasks have the same user_id
        - No other users' tasks appear in the list
        """
        logger.info("Testing task list shows only user's tasks")
        
        # Get user's ID from a task they create
        task_data = {
            "title": "List Test Task",
            "description": "For verifying task ownership in list"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        current_user_id = create_response.json()["user_id"]
        
        # List all tasks
        list_response = task_service_client.get("/tasks")
        assert list_response.status_code == 200
        
        tasks = list_response.json()
        
        # Verify all tasks belong to current user
        for task in tasks:
            assert task["user_id"] == current_user_id, (
                f"All tasks should belong to current user {current_user_id}, "
                f"but found task with user_id {task['user_id']}"
            )
        
        logger.info(f"Verified {len(tasks)} tasks all belong to current user")
        logger.info("List tasks ownership test PASSED")
    
    def test_cannot_modify_other_user_task(self, task_service_client, second_user_client):
        """
        Test that user cannot modify another user's task.
        
        Expected behavior:
        - Status code 403 (Forbidden) or 404 (Not Found)
        - Task is not modified
        """
        logger.info("Testing cannot modify other user's task")
        
        # User 1 creates a task
        task_data = {
            "title": "Original Title",
            "description": "User 1's task"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task_id = create_response.json()["id"]
        original_title = create_response.json()["title"]
        
        # User 2 tries to modify it
        update_data = {"title": "Modified Title"}
        update_response = second_user_client.put(f"/tasks/{task_id}", json=update_data)
        
        logger.info(f"Update attempt by other user: {update_response.status_code}")
        
        # Should fail with 403 or 404
        assert update_response.status_code in (403, 404), (
            f"Expected 403 or 404, got {update_response.status_code}. "
            f"Users should not be able to modify other users' tasks."
        )
        
        # Verify task was not modified
        get_response = task_service_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == original_title, (
            "Task should not be modified by unauthorized user"
        )
        
        logger.info("Cannot modify other user's task test PASSED")
    
    def test_cannot_delete_other_user_task(self, task_service_client, second_user_client):
        """
        Test that user cannot delete another user's task.
        
        Expected behavior:
        - Status code 403 (Forbidden) or 404 (Not Found)
        - Task still exists
        """
        logger.info("Testing cannot delete other user's task")
        
        # User 1 creates a task
        task_data = {
            "title": "Protected Task",
            "description": "User 1's task to protect"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task_id = create_response.json()["id"]
        
        # User 2 tries to delete it
        delete_response = second_user_client.delete(f"/tasks/{task_id}")
        
        logger.info(f"Delete attempt by other user: {delete_response.status_code}")
        
        # Should fail with 403 or 404
        assert delete_response.status_code in (403, 404), (
            f"Expected 403 or 404, got {delete_response.status_code}. "
            f"Users should not be able to delete other users' tasks."
        )
        
        # Verify task still exists
        get_response = task_service_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200, (
            "Task should still exist after unauthorized delete attempt"
        )
        
        logger.info("Cannot delete other user's task test PASSED")
    
    def test_cannot_view_other_user_task(self, task_service_client, second_user_client):
        """
        Test that user cannot view another user's task details.
        
        Expected behavior:
        - Status code 403 (Forbidden) or 404 (Not Found)
        """
        logger.info("Testing cannot view other user's task")
        
        # User 1 creates a task
        task_data = {
            "title": "Private Task",
            "description": "User 1's private task"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task_id = create_response.json()["id"]
        
        # User 2 tries to view it
        view_response = second_user_client.get(f"/tasks/{task_id}")
        
        logger.info(f"View attempt by other user: {view_response.status_code}")
        
        # Should fail with 403 or 404
        assert view_response.status_code in (403, 404), (
            f"Expected 403 or 404, got {view_response.status_code}. "
            f"Users should not be able to view other users' tasks."
        )
        
        logger.info("Cannot view other user's task test PASSED")
