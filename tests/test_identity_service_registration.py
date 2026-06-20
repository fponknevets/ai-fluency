"""Tests for Identity Service registration."""
import pytest
import logging
import uuid

logger = logging.getLogger(__name__)


class TestIdentityServiceRegistration:
    """Test suite for user registration."""
    
    def test_register_new_user_success(self):
        """
        Test successful user registration.
        
        Expected behavior:
        - Status code 201 (Created)
        - Response contains user object with email, id, timestamps
        """
        logger.info("Testing successful user registration")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Generate unique email
        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123"
        
        response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 201, (
            f"Expected 201, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        user = response.json()
        logger.info(f"User registered: {user}")
        
        # Verify response structure
        assert "id" in user, "Response should contain user id"
        assert "email" in user, "Response should contain email"
        assert user["email"] == unique_email, "Email should match request"
        assert "created_at" in user, "Response should contain created_at"
        assert "updated_at" in user, "Response should contain updated_at"
        
        client.close()
        logger.info("Successful registration test PASSED")
    
    def test_register_duplicate_email_fails(self):
        """
        Test that registering with duplicate email fails.
        
        Expected behavior:
        - Status code 400 or 409 (Conflict)
        """
        logger.info("Testing duplicate email registration failure")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Create unique email
        unique_email = f"unique_{uuid.uuid4().hex[:8]}@example.com"
        password = "SecurePassword123"
        
        # Register first user
        register1_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert register1_response.status_code == 201, "First registration should succeed"
        
        # Try to register again with same email
        register2_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": "DifferentPassword456"}
        )
        
        logger.info(f"Duplicate registration response status: {register2_response.status_code}")
        
        assert register2_response.status_code in (400, 409), (
            f"Expected 400 or 409 for duplicate email, got {register2_response.status_code}. "
            f"Response: {register2_response.text}"
        )
        
        client.close()
        logger.info("Duplicate email failure test PASSED")
    
    def test_register_missing_email(self):
        """
        Test that registration fails with missing email.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing missing email validation")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/register",
            json={"password": "SomePassword123"}
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for missing email, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Missing email validation test PASSED")
    
    def test_register_missing_password(self):
        """
        Test that registration fails with missing password.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing missing password validation")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/register",
            json={"email": f"test_{uuid.uuid4().hex[:8]}@example.com"}
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for missing password, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Missing password validation test PASSED")
    
    def test_register_invalid_email_format(self):
        """
        Test that registration fails with invalid email format.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing invalid email format validation")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/register",
            json={"email": "not-an-email", "password": "Password123"}
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for invalid email format, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Invalid email format test PASSED")
    
    def test_register_password_too_short(self):
        """
        Test that registration fails with password below minimum length.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        - Minimum password length is 8 characters
        """
        logger.info("Testing password minimum length validation")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/register",
            json={
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": "short"  # Less than 8 characters
            }
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for password too short, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Password minimum length test PASSED")
    
    def test_register_empty_password(self):
        """
        Test that registration fails with empty password.
        
        Expected behavior:
        - Status code 422 (Validation Error)
        """
        logger.info("Testing empty password validation")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        response = client.post(
            "/auth/register",
            json={
                "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
                "password": ""
            }
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        assert response.status_code == 422, (
            f"Expected 422 for empty password, got {response.status_code}. "
            f"Response: {response.text}"
        )
        
        client.close()
        logger.info("Empty password validation test PASSED")
    
    def test_registered_user_can_login(self):
        """
        Test that newly registered user can immediately login.
        
        Expected behavior:
        - Registration succeeds (201)
        - Login with same credentials succeeds (200)
        - Response contains access_token
        """
        logger.info("Testing newly registered user can login")
        
        from config.http_client import HTTPClient
        from config.config import IDENTITY_SERVICE_URL
        
        client = HTTPClient(base_url=IDENTITY_SERVICE_URL)
        
        # Register user
        unique_email = f"login_test_{uuid.uuid4().hex[:8]}@example.com"
        password = "LoginTestPassword123"
        
        register_response = client.post(
            "/auth/register",
            json={"email": unique_email, "password": password}
        )
        assert register_response.status_code == 201, "Registration should succeed"
        
        # Login with registered credentials
        login_response = client.post(
            "/auth/login",
            json={"email": unique_email, "password": password}
        )
        
        logger.info(f"Login response status: {login_response.status_code}")
        
        assert login_response.status_code == 200, (
            f"Expected 200 for login, got {login_response.status_code}. "
            f"Response: {login_response.text}"
        )
        
        token_data = login_response.json()
        assert "access_token" in token_data, "Response should contain access_token"
        assert "token_type" in token_data, "Response should contain token_type"
        
        client.close()
        logger.info("Newly registered user login test PASSED")
