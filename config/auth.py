"""Authentication module for obtaining JWT tokens."""
import logging
import uuid
from .http_client import HTTPClient

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


def register_test_user(email: str, password: str, service_url: str) -> dict:
    """
    Register a new test user with the Identity Service.
    
    Args:
        email: Email for the new user
        password: Password for the new user (min 8 chars)
        service_url: Base URL of Identity Service
    
    Returns:
        User object dict with id, email, created_at, updated_at
    
    Raises:
        AuthenticationError: If registration fails
    """
    client = HTTPClient(base_url=service_url)
    
    try:
        logger.info(f"Registering test user: {email}")
        response = client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )
        
        if response.status_code not in (200, 201):
            error_msg = f"Registration failed with status {response.status_code}"
            logger.error(f"{error_msg}: {response.text}")
            raise AuthenticationError(error_msg)
        
        user = response.json()
        logger.info(f"User registered successfully: {user.get('email')}")
        return user
    
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        logger.error(f"Registration request failed: {e}")
        raise AuthenticationError(f"Failed to register: {e}") from e
    finally:
        client.close()


def login_user(email: str, password: str, service_url: str) -> str:
    """
    Login and obtain JWT token from Identity Service.
    
    Args:
        email: User email
        password: User password
        service_url: Base URL of Identity Service
    
    Returns:
        JWT token string (access_token)
    
    Raises:
        AuthenticationError: If login fails
    """
    client = HTTPClient(base_url=service_url)
    
    try:
        logger.info(f"Authenticating user: {email}")
        response = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code != 200:
            error_msg = f"Authentication failed with status {response.status_code}"
            logger.error(f"{error_msg}: {response.text}")
            raise AuthenticationError(error_msg)
        
        data = response.json()
        token = data.get("access_token")
        
        if not token:
            logger.error(f"No access_token in response: {data}")
            raise AuthenticationError("No access_token found in authentication response")
        
        logger.info("Authentication successful")
        return token
    
    except Exception as e:
        if isinstance(e, AuthenticationError):
            raise
        logger.error(f"Authentication request failed: {e}")
        raise AuthenticationError(f"Failed to authenticate: {e}") from e
    finally:
        client.close()


def get_or_create_test_user_token(service_url: str, email: str = None, password: str = None) -> str:
    """
    Get or create a test user and return JWT token.
    
    If email/password not provided, generates new ones.
    Attempts to register the user; if already exists (409), attempts to login.
    
    Args:
        service_url: Base URL of Identity Service
        email: Optional email for test user (generates one if not provided)
        password: Optional password for test user (generates one if not provided)
    
    Returns:
        JWT token string
    
    Raises:
        AuthenticationError: If registration and login both fail
    """
    if not email:
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    if not password:
        password = f"TestPassword{uuid.uuid4().hex[:8]}"
    
    logger.info(f"Getting or creating test user: {email}")
    
    # Try to register first
    try:
        register_test_user(email, password, service_url)
    except AuthenticationError as e:
        # If user already exists (409), that's ok - we'll try to login
        if "409" in str(e) or "already exists" in str(e):
            logger.info(f"User already exists, proceeding to login")
        else:
            logger.warning(f"Registration failed: {e}, attempting login anyway")
    
    # Login with the credentials
    token = login_user(email, password, service_url)
    return token
