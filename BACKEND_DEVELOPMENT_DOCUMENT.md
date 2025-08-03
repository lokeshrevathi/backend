# Project Management Dashboard – Backend Development Documentation

## 1. Project Setup (Backend)
- Created a new Django project and app structure.
- Installed required packages:
  - `djangorestframework` for API development
  - `django-cors-headers` for CORS support
  - `djangorestframework-simplejwt` for JWT authentication
  - `django-filter` for filtering API results
  - `drf-spectacular` for OpenAPI documentation
  - `coverage` for test coverage
- Configured Django settings for REST Framework, authentication, and CORS.
- Defined a custom user model for extensibility.

## 2. PostgreSQL Configuration
- Updated `settings.py` to use PostgreSQL as the database backend.
- Set up database credentials and connection parameters.
- Ran migrations to initialize the database schema.

## 3. API Design and Authentication (JWT)
- Designed RESTful API endpoints for:
  - Project
  - Milestone
  - Task
  - Comment
  - Attachment
- Implemented JWT authentication for secure login and token management.
- Created registration and login endpoints.
- Enforced permissions so users can only access their own data.
- Added filtering support for tasks (by status, assignee, etc.).

## 4. Core Features
### Project Creation
- CRUD endpoints for projects.
- Only project owners can view, update, or delete their projects.

### Task Management
- Endpoints for milestones, tasks, comments, and attachments.
- Supported task assignment, status updates, and file uploads.
- Filtering for tasks by status and assignee.

### Progress Tracking
- Custom endpoint to calculate project progress percentage based on completed tasks.

### Time Logging
- Endpoint for logging hours to tasks.
- Project-level endpoint to sum total hours logged across all tasks.

## 5. Testing and Documentation
- Comprehensive API tests using DRF's `APITestCase` for all endpoints and features (see `core/tests.py`).
- Generated OpenAPI/Swagger documentation using `drf-spectacular`.
- Measured code coverage with `coverage.py` to ensure robust test validation.

---

This process resulted in a secure, feature-rich, and well-documented project management API backend. All major features are covered by automated tests and documented for easy integration.
