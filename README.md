# AI Fluency Test Suite

Automated test suite for Identity Service and Task Service microservices with JWT-based authentication.

## Quick Start

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. **Clone and navigate to project:**
   ```bash
   cd ai-fluency
   ```

2. **Create `.env` file from template:**
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your test credentials:
   ```
   IDENTITY_SERVICE_URL=https://identity-service-365603594789.europe-west1.run.app/api/v1
   TASK_SERVICE_URL=https://task-service-365603594789.europe-west1.run.app/api/v1
   TEST_USERNAME=your_username
   TEST_PASSWORD=your_password
   ```

3. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

4. **Run tests:**
   ```bash
   uv run pytest
   ```
   
   Or with verbose output:
   ```bash
   uv run pytest -v
   ```

### Project Structure

```
ai-fluency/
├── config/                # Configuration and HTTP utilities
│   ├── __init__.py
│   ├── config.py          # Environment configuration loader
│   ├── http_client.py     # HTTP client with Bearer token support
│   └── auth.py            # User registration and JWT authentication
├── tests/                 # Test suite (57 tests)
│   ├── __init__.py
│   ├── test_identity_service_health.py      # Health endpoint
│   ├── test_identity_service_registration.py # User registration (8 tests)
│   ├── test_identity_service_login.py       # User login/auth (8 tests)
│   ├── test_identity_service_user.py        # User info endpoint (7 tests)
│   ├── test_task_service_health.py          # Task service health
│   ├── test_task_service_crud.py            # Task CRUD operations (5 tests)
│   ├── test_jwt_security.py                 # JWT validation (5 tests)
│   ├── test_authorization.py                # Access control/RBAC (6 tests)
│   ├── test_input_validation.py             # Input validation (10 tests)
│   └── test_data_integrity.py               # Data integrity (6 tests)
├── conftest.py            # pytest fixtures (session-scoped auth clients)
├── pyproject.toml         # Project metadata, dependencies, pytest config
├── uv.lock                # Dependency lock file
├── .env.example           # Environment configuration template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

### Configuration

All configuration is managed via `.env` file (see `.env.example` for template).

Required variables:
- `IDENTITY_SERVICE_URL` - Base URL for Identity Service
- `TASK_SERVICE_URL` - Base URL for Task Service

Note: Test user credentials are auto-generated during test setup.

### Running Tests

**All tests:**
```bash
uv run pytest
```

**Specific test file:**
```bash
uv run pytest tests/test_identity_service_health.py
```

**With coverage:**
```bash
uv sync --extra dev  # Install coverage plugin first
uv run pytest --cov=config --cov=tests --cov-report=html
```

**With HTML report:**
```bash
uv sync --extra dev  # Install pytest-html first
uv run pytest --html=reports/test_report.html --self-contained-html
```

**With JSON report:**
```bash
uv sync --extra dev  # Install pytest-json-report first
uv run pytest --json-report --json-report-file=reports/test_report.json
```

**Full reporting (coverage + HTML + JSON):**
```bash
uv sync --extra dev
uv run pytest --cov=config --cov=tests --cov-report=html --html=reports/test_report.html --self-contained-html --json-report --json-report-file=reports/test_report.json
```

**Watch mode (requires pytest-watch):**
```bash
uv run pytest-watch
```

### Test Coverage Summary

**Total: 63 tests passing**

| Category | Count | Tests |
|----------|-------|-------|
| **Health Checks** | 2 | Identity Service, Task Service |
| **Identity Service** | 23 | Registration, Login, User Info |
| **CRUD Operations** | 5 | Create, List, Get, Update, Delete |
| **JWT Security** | 5 | Token validation, format, bearer prefix |
| **Authorization** | 6 | Ownership, isolation, access control |
| **Input Validation** | 10 | Required fields, types, boundaries, injection |
| **Data Integrity** | 6 | Timestamps, IDs, field persistence |
| **Performance** | 6 | Response times, concurrency, load testing |

### Project Phases

#### Phase 1: Framework & Health Endpoint ✓
- [x] Project structure and dependencies
- [x] Configuration management with .env
- [x] HTTP client with Bearer token support
- [x] Authentication module (JWT login)
- [x] pytest fixtures for authenticated clients
- [x] First health endpoint test

#### Phase 2: Task Service Tests ✓
- [x] Task Service health endpoint tests
- [x] Task CRUD operations tests
  - [x] Create task
  - [x] List all tasks
  - [x] Retrieve specific task
  - [x] Update task
  - [x] Delete task
- [x] All 7 tests passing end-to-end

#### Phase 3: Security & Integrity ✓
- [x] JWT validation tests (5 tests)
  - No token / empty token rejection
  - Invalid token format handling
  - Bearer prefix verification
- [x] Authorization (RBAC) tests (6 tests)
  - Task ownership verification
  - Cross-user access prevention
  - Task list isolation per user
- [x] Input validation tests (10 tests)
  - Missing required fields
  - Type validation and coercion
  - Boundary conditions (long strings, empty values)
  - Security payloads (XSS, SQL injection)
  - Invalid UUIDs
- [x] Data integrity tests (6 tests)
  - Timestamp immutability (created_at)
  - User/Task ID immutability
  - Boolean field persistence
  - Optional field handling
  - Partial update field preservation
- [x] All 27 Phase 3 tests passing

#### Phase 4: Identity Service Tests ✓
- [x] User registration tests (8 tests)
  - [x] Successful registration
  - [x] Duplicate email prevention
  - [x] Email format validation
  - [x] Password requirements (minimum length, non-empty)
  - [x] Required field validation (email, password)
  - [x] Registered user can login
- [x] User login and authentication tests (8 tests)
  - [x] Successful login with valid credentials
  - [x] Wrong password rejection
  - [x] Non-existent user rejection
  - [x] Missing field validation
  - [x] Email case sensitivity handling
  - [x] Token validity for requests
  - [x] Multiple login sessions
- [x] User info and account tests (7 tests)
  - [x] Get current user info (/auth/me endpoint)
  - [x] Authentication requirement enforcement
  - [x] Invalid token rejection
  - [x] User email consistency
  - [x] User ID consistency across requests
  - [x] Created timestamp immutability
  - [x] User ID uniqueness
- [x] All 23 Phase 4 tests passing

#### Phase 5: Reporting & CI/CD ✓
- [x] Test report generation (HTML/JSON output)
  - [x] pytest-html for interactive HTML reports
  - [x] pytest-json-report for JSON test output
- [x] GitHub Actions CI/CD pipeline
  - [x] Automated test runs on push/PR
  - [x] Multi-version Python testing (3.9, 3.10, 3.11, 3.12)
  - [x] Coverage report uploads to Codecov
  - [x] PR comment with test results
- [x] Test coverage reports
  - [x] pytest-cov for code coverage analysis
  - [x] HTML coverage reports (htmlcov/)
- [x] Performance and load testing (6 tests)
  - [x] Task creation response time (< 500ms)
  - [x] List tasks response time (< 1000ms)
  - [x] Concurrent task creation (10 threads, < 10% failure)
  - [x] Concurrent task reads (10 threads, < 10% failure)
  - [x] Login endpoint performance (< 300ms)
  - [x] User info endpoint performance (< 200ms)
- [x] All 6 Phase 5 performance tests passing
