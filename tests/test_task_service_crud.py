"""Tests for Task Service CRUD operations."""
import pytest
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TestTaskServiceCRUD:
    """Test suite for Task Service CRUD operations."""
    
    def test_create_task(self, task_service_client):
        """
        Test creating a new task.
        
        Expected behavior:
        - Status code 201 (Created)
        - Response contains task object with id, user_id, timestamps
        - Task fields match request body
        """
        logger.info("Testing task creation")
        
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        response = task_service_client.post("/tasks", json=task_data)
        
        assert response.status_code == 201, (
            f"Expected status 201, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        task = response.json()
        logger.info(f"Created task: {task}")
        
        # Verify response structure
        assert "id" in task, "Task should have id"
        assert "user_id" in task, "Task should have user_id"
        assert task["title"] == task_data["title"], "Task title should match request"
        assert task["description"] == task_data["description"], "Task description should match request"
        assert task["is_completed"] is False, "New task should not be completed"
        assert "created_at" in task, "Task should have created_at timestamp"
        assert "updated_at" in task, "Task should have updated_at timestamp"
        
        logger.info("Task creation test PASSED")
    
    def test_list_tasks(self, task_service_client):
        """
        Test retrieving all tasks for current user.
        
        Expected behavior:
        - Status code 200 (OK)
        - Response is array of task objects
        - Each task has required fields
        """
        logger.info("Testing list tasks")
        
        # Create a test task first
        task_data = {
            "title": "List Test Task",
            "description": "Task for list test"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        # List all tasks
        response = task_service_client.get("/tasks")
        
        assert response.status_code == 200, (
            f"Expected status 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        tasks = response.json()
        logger.info(f"Retrieved {len(tasks)} tasks")
        
        assert isinstance(tasks, list), "Response should be a list of tasks"
        assert len(tasks) > 0, "Should have at least one task"
        
        # Verify task structure
        for task in tasks:
            assert "id" in task, "Each task should have id"
            assert "title" in task, "Each task should have title"
            assert "description" in task, "Each task should have description"
            assert "is_completed" in task, "Each task should have is_completed"
            assert "created_at" in task, "Each task should have created_at"
            assert "updated_at" in task, "Each task should have updated_at"
        
        logger.info("List tasks test PASSED")
    
    def test_get_task(self, task_service_client):
        """
        Test retrieving a specific task by ID.
        
        Expected behavior:
        - Status code 200 (OK)
        - Response contains the requested task
        - Task has all required fields
        """
        logger.info("Testing get task")
        
        # Create a test task
        task_data = {
            "title": "Get Test Task",
            "description": "Task for get test"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Get the specific task
        response = task_service_client.get(f"/tasks/{task_id}")
        
        assert response.status_code == 200, (
            f"Expected status 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        task = response.json()
        logger.info(f"Retrieved task: {task}")
        
        assert task["id"] == task_id, "Retrieved task should have correct id"
        assert task["title"] == task_data["title"], "Task title should match"
        assert task["description"] == task_data["description"], "Task description should match"
        
        logger.info("Get task test PASSED")
    
    def test_update_task(self, task_service_client):
        """
        Test updating a task.
        
        Expected behavior:
        - Status code 200 (OK)
        - Response contains updated task with modified fields
        - Unmodified fields remain unchanged
        """
        logger.info("Testing task update")
        
        # Create a test task
        task_data = {
            "title": "Original Title",
            "description": "Original description"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Update the task
        update_data = {
            "title": "Updated Title",
            "is_completed": True
        }
        response = task_service_client.put(f"/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200, (
            f"Expected status 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        updated_task = response.json()
        logger.info(f"Updated task: {updated_task}")
        
        assert updated_task["id"] == task_id, "Task id should not change"
        assert updated_task["title"] == update_data["title"], "Task title should be updated"
        assert updated_task["is_completed"] is True, "Task should be marked completed"
        assert updated_task["description"] == task_data["description"], "Description should remain unchanged"
        
        logger.info("Task update test PASSED")
    
    def test_delete_task(self, task_service_client):
        """
        Test deleting a task.
        
        Expected behavior:
        - Status code 204 (No Content)
        - Task is removed and subsequent GET returns 404
        """
        logger.info("Testing task deletion")
        
        # Create a test task
        task_data = {
            "title": "Delete Test Task",
            "description": "Task to be deleted"
        }
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        
        # Delete the task
        response = task_service_client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == 204, (
            f"Expected status 204, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        logger.info("Task deleted successfully")
        
        # Verify task is deleted
        get_response = task_service_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404, (
            "Deleted task should return 404 on subsequent GET"
        )
        
        logger.info("Task deletion test PASSED")
