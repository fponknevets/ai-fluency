"""pytest configuration and shared fixtures."""
import logging
import pytest
from config.config import IDENTITY_SERVICE_URL, TASK_SERVICE_URL
from config.auth import get_or_create_test_user_token
from config.http_client import HTTPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def identity_service_jwt():
    """Obtain JWT token for Identity Service via auto-registration (session scope)."""
    logger.info("Setting up Identity Service test user")
    token = get_or_create_test_user_token(IDENTITY_SERVICE_URL)
    logger.info("Identity Service JWT token obtained successfully")
    return token


@pytest.fixture(scope="session")
def identity_service_client(identity_service_jwt):
    """Provide authenticated HTTP client for Identity Service."""
    client = HTTPClient(base_url=IDENTITY_SERVICE_URL, token=identity_service_jwt)
    yield client
    client.close()


@pytest.fixture(scope="session")
def task_service_jwt(identity_service_jwt):
    """Provide JWT token for Task Service (reuses Identity Service JWT)."""
    logger.info("Task Service using Identity Service JWT")
    return identity_service_jwt


@pytest.fixture(scope="session")
def task_service_client(task_service_jwt):
    """Provide authenticated HTTP client for Task Service."""
    client = HTTPClient(base_url=TASK_SERVICE_URL, token=task_service_jwt)
    yield client
    client.close()


def pytest_configure(config):
    """Called after command line options have been parsed."""
    logger.info("=" * 80)
    logger.info("Test Suite Configuration")
    logger.info(f"Identity Service URL: {IDENTITY_SERVICE_URL}")
    logger.info(f"Task Service URL: {TASK_SERVICE_URL}")
    logger.info("=" * 80)
