"""Tests for Identity Service user info endpoint."""
import pytest
import logging
import uuid

logger = logging.getLogger(__name__)


class TestIdentityServiceUserInfo:
    """Test suite for user information retrieval."""
    
    def test_get_current_user_info_with_token(self, identity_service_client):
        """
        Test retrieving current user info with valid JWT.
        
        Expected behavior:
        - Status code 200 (OK)
        - Response contains user email, id, timestamps
        """
        logger.info("Testing get current user info")
        
        response = identity_service_client.get("/auth/me")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        user_info = response.json()
        logger.info(f"User info: {user_info}")
        
        # Verify response structure
        assert "email" in user_info, "Response should contain email"
        assert "id" in user_info, "Response should contain id"
        assert "created_at" in user_info, "Response should contain created_at"
        assert "updated_at" in user_info, "Response should contain updated_at"
        
        logger.info("Get current user info test PASSED")
    
    def test_get_user_without_token(self):
        """
        Test that getting user info fails without JWT.
        
        Expected behavior:
        - Status code 401 (Unauthorized)
        """
        logger.info("Testing get user info without token")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        # Create client without token
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=None)
        
        response = client.get("/auth/me")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 401, (
            f"Expected 401 for missing token, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("No token access denial test PASSED")
    
    def test_get_user_with_invalid_token(self):
        """
        Test that getting user info fails with invalid JWT.
        
        Expected behavior:
        - Status code 401 (Unauthorized)
        """
        logger.info("Testing get user info with invalid token")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        # Create client with invalid token
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL, token="invalid.jwt.token")
        
        response = client.get("/auth/me")
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 401, (
            f"Expected 401 for invalid token, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Invalid token rejection test PASSED")
    
    def test_user_email_matches_registration(self):
        """
        Test that user info email matches registration email.
        
        Expected behavior:
        - Email in /auth/me response matches registration email
        """
        logger.info("Testing user email consistency")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        from config.auth import get_or_create_test_user_token
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register with specific email
        specific_email = f"consistency_test_{uuid.uuid4().hex[:8]}@example.com"
        password = "ConsistencyPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": specific_email, "password": password}
        )
        assert register_response.status_code == 201
        registered_user = register_response.json()
        registered_email = registered_user["email"]
        
        # Login to get token
        login_response = client.post(
            "/auth/login",
            json={"email": specific_email, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get user info
        auth_client = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=token)
        me_response = auth_client.get("/auth/me")
        
        assert me_response.status_code == 200
        user_info = me_response.json()
        
        # Verify email consistency
        assert user_info["email"] == registered_email, (
            f"Email in /auth/me should match registration email. "
            f"Expected: {registered_email}, Got: {user_info['email']}"
        )
        
        logger.info("User email consistency test PASSED")
        
        client.close()
        auth_client.close()
    
    def test_user_id_consistency(self):
        """
        Test that user ID is consistent across requests.
        
        Expected behavior:
        - User ID from registration matches ID from /auth/me
        """
        logger.info("Testing user ID consistency")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register user
        unique_email = f"id_test_{uuid.uuid4().hex[:8]}@example.com"
        password = "IdTestPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert register_response.status_code == 201
        registered_id = register_response.json()["id"]
        
        # Login
        login_response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get user info
        auth_client = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=token)
        me_response = auth_client.get("/auth/me")
        assert me_response.status_code == 200
        
        me_id = me_response.json()["id"]
        
        # Verify ID consistency
        assert me_id == registered_id, (
            f"User ID from /auth/me should match registration. "
            f"Expected: {registered_id}, Got: {me_id}"
        )
        
        logger.info("User ID consistency test PASSED")
        
        client.close()
        auth_client.close()
    
    def test_user_timestamps_immutable(self):
        """
        Test that user created_at timestamp is immutable.
        
        Expected behavior:
        - created_at remains unchanged across multiple /auth/me calls
        - updated_at may change
        """
        logger.info("Testing user timestamp immutability")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        import time
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register user
        unique_email = f"ts_test_{uuid.uuid4().hex[:8]}@example.com"
        password = "TimestampTestPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert register_response.status_code == 201
        original_created_at = register_response.json()["created_at"]
        
        # Login
        login_response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": password}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get user info
        auth_client = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=token)
        me_response1 = auth_client.get("/auth/me")
        assert me_response1.status_code == 200
        user_info1 = me_response1.json()
        
        # Wait a moment
        time.sleep(1)
        
        # Get user info again
        me_response2 = auth_client.get("/auth/me")
        assert me_response2.status_code == 200
        user_info2 = me_response2.json()
        
        logger.info(f"First created_at: {user_info1['created_at']}")
        logger.info(f"Second created_at: {user_info2['created_at']}")
        
        # Verify created_at is immutable
        assert user_info1["created_at"] == user_info2["created_at"], (
            "created_at should not change"
        )
        assert user_info1["created_at"] == original_created_at, (
            "created_at from /auth/me should match registration"
        )
        
        logger.info("User timestamp immutability test PASSED")
        
        client.close()
        auth_client.close()
    
    def test_different_users_have_different_ids(self):
        """
        Test that different users have unique IDs.
        
        Expected behavior:
        - Each registered user has a unique ID
        """
        logger.info("Testing user ID uniqueness")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register first user
        email1 = f"unique_id_test1_{uuid.uuid4().hex[:8]}@example.com"
        password1 = "Password123"
        
        register1 = client.post(
            "/auth/register",
            json={"email": email1, "password": password1}
        )
        assert register1.status_code == 201
        user_id1 = register1.json()["id"]
        
        # Register second user
        email2 = f"unique_id_test2_{uuid.uuid4().hex[:8]}@example.com"
        password2 = "Password456"
        
        register2 = client.post(
            "/auth/register",
            json={"email": email2, "password": password2}
        )
        assert register2.status_code == 201
        user_id2 = register2.json()["id"]
        
        # Verify IDs are different
        assert user_id1 != user_id2, (
            f"Different users should have different IDs. "
            f"Got same ID: {user_id1}"
        )
        
        logger.info("User ID uniqueness test PASSED")
        
        client.close()
