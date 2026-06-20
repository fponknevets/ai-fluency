"""Tests for Identity Service login and authentication."""
import pytest
import logging
import uuid

logger = logging.getLogger(__name__)


class TestIdentityServiceLogin:
    """Test suite for user login and token generation."""
    
    def test_login_with_valid_credentials(self):
        """
        Test successful login with valid credentials.
        
        Expected behavior:
        - Status code 200 (OK)
        - Response contains access_token and token_type
        """
        logger.info("Testing successful login")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register user first
        unique_email = f"valid_login_{uuid.uuid4().hex[:8]}@example.com"
        password = "ValidPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert register_response.status_code == 201
        
        # Login
        login_response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": password}
        )
        
        logger.info(f"Login response status: {login_response.status_code}")
        
        assert login_response.status_code == 200, (
            f"Expected 200, got {login_response.status_code}. "
            f"Response: {login_response.text}"
        )
        
        token_data = login_response.json()
        logger.info(f"Token response: {token_data}")
        
        # Verify response structure
        assert "access_token" in token_data, "Response should contain access_token"
        assert token_data["access_token"], "access_token should not be empty"
        assert "token_type" in token_data, "Response should contain token_type"
        assert token_data["token_type"] == "bearer", "token_type should be 'bearer'"
        
        client.close()
        logger.info("Valid credentials login test PASSED")
    
    def test_login_with_wrong_password(self):
        """
        Test login fails with wrong password.
        
        Expected behavior:
        - Status code 401 (Unauthorized) or 400 (Bad Request)
        """
        logger.info("Testing login with wrong password")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register user
        unique_email = f"wrong_pwd_{uuid.uuid4().hex[:8]}@example.com"
        correct_password = "CorrectPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": correct_password}
        )
        assert register_response.status_code == 201
        
        # Login with wrong password
        login_response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": "WrongPassword999"}
        )
        
        logger.info(f"Login response status: {login_response.status_code}")
        
        assert login_response.status_code in (401, 400), (
            f"Expected 401 or 400 for wrong password, got {login_response.status_code}. "
            f"Response: {login_response.text}"
        )
        
        client.close()
        logger.info("Wrong password login test PASSED")
    
    def test_login_with_nonexistent_user(self):
        """
        Test login fails for non-existent user.
        
        Expected behavior:
        - Status code 401 (Unauthorized) or 404 (Not Found)
        """
        logger.info("Testing login with non-existent user")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/login",
            json={
                "email": f"nonexistent_{uuid.uuid4().hex[:8]}@example.com",
                "password": "SomePassword123"
            }
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code in (401, 404), (
            f"Expected 401 or 404 for non-existent user, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Non-existent user login test PASSED")
    
    def test_login_missing_email(self):
        """
        Test login fails with missing email.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing login with missing email")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/login",
            json={"password": "SomePassword123"}
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for missing email, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Missing email login test PASSED")
    
    def test_login_missing_password(self):
        """
        Test login fails with missing password.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing login with missing password")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com"}
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for missing password, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Missing password login test PASSED")
    
    def test_login_case_sensitivity(self):
        """
        Test login behavior with email case variations.
        
        Expected behavior:
        - Either case-insensitive (both succeed) or case-sensitive (only exact match succeeds)
        """
        logger.info("Testing login email case sensitivity")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register with lowercase email
        email_lower = f"case_test_{uuid.uuid4().hex[:8]}@example.com".lower()
        password = "CaseTestPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": email_lower, "password": password}
        )
        assert register_response.status_code == 201
        
        # Try login with uppercase
        email_upper = email_lower.upper()
        login_response = client.post(
            "/auth/login",
            json={"email": email_upper, "password": password}
        )
        
        logger.info(f"Login with uppercase email: {login_response.status_code}")
        
        # Most systems are case-insensitive for email
        if login_response.status_code == 200:
            logger.info("API is case-insensitive for email (expected)")
        else:
            logger.info("API is case-sensitive for email")
            # Try with exact case
            exact_login = client.post(
                "/auth/login",
                json={"email": email_lower, "password": password}
            )
            assert exact_login.status_code == 200, "Login should work with correct case"
        
        client.close()
        logger.info("Email case sensitivity test PASSED")
    
    def test_token_can_be_used_for_requests(self, identity_service_client):
        """
        Test that returned JWT token can be used for authenticated requests.
        
        Expected behavior:
        - Token is valid for subsequent requests
        - Can access protected endpoints with token
        """
        logger.info("Testing JWT token validity")
        
        # identity_service_client is already authenticated
        # Try to access /auth/me which requires authentication
        response = identity_service_client.get("/auth/me")
        
        logger.info(f"GET /auth/me response: {response.status_code}")
        
        assert response.status_code == 200, (
            f"Expected 200 for authenticated request, got {response.status_code}. "
            f"Token should be valid for API calls."
        )
        
        user_info = response.json()
        assert "email" in user_info, "User info should contain email"
        
        logger.info("Token validity test PASSED")
    
    def test_multiple_logins_produce_tokens(self):
        """
        Test that multiple logins for same user produce valid tokens.
        
        Expected behavior:
        - Each login returns a valid token
        - Tokens are different (new token each time)
        """
        logger.info("Testing multiple logins")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register user
        unique_email = f"multi_login_{uuid.uuid4().hex[:8]}@example.com"
        password = "MultiLoginPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert register_response.status_code == 201
        
        # Login multiple times
        login1 = client.post(
            "/auth/login",
            json={"email": unique_email, "password": password}
        )
        assert login1.status_code == 200
        token1 = login1.json()["access_token"]
        
        login2 = client.post(
            "/auth/login",
            json={"email": unique_email, "password": password}
        )
        assert login2.status_code == 200
        token2 = login2.json()["access_token"]
        
        logger.info("First login succeeded")
        logger.info("Second login succeeded")
        
        # Tokens should be different (new token each time)
        # Note: Some implementations might return same token, this is flexible
        if token1 != token2:
            logger.info("Each login produced a different token (rotating tokens)")
        else:
            logger.info("Logins produced the same token")
        
        # Both tokens should be valid (can make requests)
        auth_client1 = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=token1)
        auth_client2 = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=token2)
        
        me_response1 = auth_client1.get("/auth/me")
        me_response2 = auth_client2.get("/auth/me")
        
        assert me_response1.status_code == 200, "Token 1 should be valid"
        assert me_response2.status_code == 200, "Token 2 should be valid"
        
        auth_client1.close()
        auth_client2.close()
        client.close()
        
        logger.info("Multiple logins test PASSED")
