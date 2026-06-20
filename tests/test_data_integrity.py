"""Tests for data integrity and consistency."""
import pytest
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TestDataIntegrity:
    """Test suite for data consistency and integrity."""
    
    def test_created_at_immutable(self, task_service_client):
        """
        Test that created_at timestamp is immutable.
        
        Expected behavior:
        - created_at remains unchanged after update
        - updated_at changes to reflect update time
        """
        logger.info("Testing created_at immutability")
        
        # Create task
        task_data = {"title": "Original", "description": "Test"}
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task = create_response.json()
        task_id = task["id"]
        original_created_at = task["created_at"]
        original_updated_at = task["updated_at"]
        
        logger.info(f"Created at: {original_created_at}")
        logger.info(f"Updated at: {original_updated_at}")
        
        # Update task
        update_data = {"title": "Modified"}
        update_response = task_service_client.put(f"/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        
        # Verify timestamps
        assert updated_task["created_at"] == original_created_at, (
            "created_at should not change on update"
        )
        
        assert updated_task["updated_at"] >= original_updated_at, (
            "updated_at should reflect update time (>= original)"
        )
        
        # They should typically be different
        if updated_task["updated_at"] == original_updated_at:
            logger.warning("updated_at was not changed (same millisecond?)")
        else:
            logger.info(f"Updated at changed to: {updated_task['updated_at']}")
        
        logger.info("created_at immutability test PASSED")
    
    def test_user_id_immutable(self, task_service_client):
        """
        Test that user_id is immutable after creation.
        
        Expected behavior:
        - user_id remains unchanged after update
        - Cannot change owner via update
        """
        logger.info("Testing user_id immutability")
        
        # Create task
        task_data = {"title": "Test", "description": "User ID test"}
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task = create_response.json()
        task_id = task["id"]
        original_user_id = task["user_id"]
        
        logger.info(f"Original user_id: {original_user_id}")
        
        # Try to update user_id (if API allows)
        import uuid
        fake_user_id = str(uuid.uuid4())
        
        update_data = {
            "title": "Updated",
            "user_id": fake_user_id  # Try to change owner
        }
        
        update_response = task_service_client.put(f"/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        
        # Verify user_id wasn't changed
        assert updated_task["user_id"] == original_user_id, (
            "user_id should not be changeable via update"
        )
        
        logger.info("user_id immutability test PASSED")
    
    def test_task_id_immutable(self, task_service_client):
        """
        Test that task_id is immutable after creation.
        
        Expected behavior:
        - id remains unchanged after update
        """
        logger.info("Testing task_id immutability")
        
        # Create task
        task_data = {"title": "Test", "description": "ID immutability test"}
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task = create_response.json()
        task_id = task["id"]
        
        logger.info(f"Original task_id: {task_id}")
        
        # Update task
        update_data = {"title": "Updated Title"}
        update_response = task_service_client.put(f"/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        
        # Verify ID didn't change
        assert updated_task["id"] == task_id, "Task ID should not change on update"
        
        logger.info("task_id immutability test PASSED")
    
    def test_boolean_field_persists_correctly(self, task_service_client):
        """
        Test that boolean is_completed field persists correctly.
        
        Expected behavior:
        - is_completed starts as False
        - Can be changed to True
        - Persists correctly on retrieval
        """
        logger.info("Testing boolean field persistence")
        
        # Create task (should start with is_completed=False)
        task_data = {"title": "Test", "description": "Boolean test"}
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task = create_response.json()
        task_id = task["id"]
        
        assert task["is_completed"] is False, "New task should have is_completed=False"
        
        # Update to True
        update_response = task_service_client.put(
            f"/tasks/{task_id}",
            json={"is_completed": True}
        )
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        assert updated_task["is_completed"] is True, "is_completed should be True after update"
        
        # Retrieve and verify persistence
        get_response = task_service_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 200
        
        retrieved_task = get_response.json()
        assert retrieved_task["is_completed"] is True, (
            "is_completed should persist as True on retrieval"
        )
        
        # Update back to False
        update_response = task_service_client.put(
            f"/tasks/{task_id}",
            json={"is_completed": False}
        )
        assert update_response.status_code == 200
        
        final_task = update_response.json()
        assert final_task["is_completed"] is False, "is_completed should be False after update"
        
        logger.info("Boolean field persistence test PASSED")
    
    def test_optional_fields_handled_correctly(self, task_service_client):
        """
        Test that optional fields (like due_date) are handled correctly.
        
        Expected behavior:
        - Task can be created without due_date
        - due_date can be set during creation
        - due_date can be updated separately
        """
        logger.info("Testing optional fields handling")
        
        # Create without due_date
        task_data = {"title": "No Due Date", "description": "Optional field test"}
        create_response = task_service_client.post("/tasks", json=task_data)
        assert create_response.status_code == 201
        
        task = create_response.json()
        task_id = task["id"]
        
        # due_date should be None or not present
        assert task.get("due_date") is None or task.get("due_date") == "", (
            "due_date should be None/empty when not provided"
        )
        
        logger.info("Created task without due_date")
        
        # Now set due_date via update
        from datetime import datetime, timedelta
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        update_response = task_service_client.put(
            f"/tasks/{task_id}",
            json={"due_date": due_date}
        )
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        assert updated_task["due_date"] is not None, "due_date should be set after update"
        
        logger.info(f"Set due_date to: {updated_task['due_date']}")
        
        # Clear due_date by setting to None
        update_response = task_service_client.put(
            f"/tasks/{task_id}",
            json={"due_date": None}
        )
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        assert updated_task.get("due_date") is None, "due_date should be clearable"
        
        logger.info("Optional fields handling test PASSED")
    
    def test_partial_update_preserves_other_fields(self, task_service_client):
        """
        Test that partial updates don't lose other fields.
        
        Expected behavior:
        - Updating only title preserves description
        - Updating only description preserves title
        - Other fields remain unchanged
        """
        logger.info("Testing partial update field preservation")
        
        # Create task with all fields
        original_data = {
            "title": "Original Title",
            "description": "Original Description"
        }
        create_response = task_service_client.post("/tasks", json=original_data)
        assert create_response.status_code == 201
        
        task = create_response.json()
        task_id = task["id"]
        original_is_completed = task["is_completed"]
        
        # Update only title
        update_response = task_service_client.put(
            f"/tasks/{task_id}",
            json={"title": "Updated Title"}
        )
        assert update_response.status_code == 200
        
        updated_task = update_response.json()
        
        # Verify title changed but description preserved
        assert updated_task["title"] == "Updated Title", "Title should be updated"
        assert updated_task["description"] == "Original Description", (
            "Description should be preserved when only title is updated"
        )
        assert updated_task["is_completed"] == original_is_completed, (
            "is_completed should be preserved when other fields updated"
        )
        
        logger.info("Partial update field preservation test PASSED")
