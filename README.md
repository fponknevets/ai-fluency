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
├── config/
│   ├── __init__.py
│   ├── config.py          # Configuration loader from .env
│   ├── http_client.py     # HTTP client with Bearer token support
│   └── auth.py            # JWT authentication
├── tests/
│   ├── __init__.py
│   └── test_identity_service_health.py  # Health endpoint tests
├── fixtures/              # Test data and fixtures (future use)
├── conftest.py            # pytest configuration and shared fixtures
├── pyproject.toml         # Project metadata and dependencies (uv)
├── .env.example           # Configuration template
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
uv run pytest --cov=tests
```

**Watch mode (requires pytest-watch):**
```bash
uv run pytest-watch
```

### Test Coverage Summary

**Total: 57 tests passing**

| Category | Count | Tests |
|----------|-------|-------|
| **Health Checks** | 2 | Identity Service, Task Service |
| **Identity Service** | 23 | Registration, Login, User Info |
| **CRUD Operations** | 5 | Create, List, Get, Update, Delete |
| **JWT Security** | 5 | Token validation, format, bearer prefix |
| **Authorization** | 6 | Ownership, isolation, access control |
| **Input Validation** | 10 | Required fields, types, boundaries, injection |
| **Data Integrity** | 6 | Timestamps, IDs, field persistence |

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

#### Phase 5: Reporting & CI/CD (planned)
- [ ] Test report generation (HTML/JSON output)
- [ ] GitHub Actions CI/CD pipeline
- [ ] Test coverage reports
- [ ] Performance and load testing
