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

## 6. Development Issues and Fixes

### 6.1 Docker Configuration Issues

#### Problem: Staticfiles Warning
- **Issue**: Django was showing warnings about missing `/app/staticfiles/` directory
- **Error**: `No directory at: /app/staticfiles/`
- **Root Cause**: Volume mounting was overwriting the staticfiles directory created during build
- **Solution**: 
  - Added explicit `RUN mkdir -p /app/staticfiles` in Dockerfile
  - Updated docker-compose.yml to exclude staticfiles from volume mounting
  - Added volume configuration: `- /app/staticfiles`

#### Problem: Docker Compose Version Warning
- **Issue**: Obsolete `version` field in docker-compose.yml
- **Error**: `the attribute 'version' is obsolete, it will be ignored`
- **Solution**: Removed the obsolete `version: '3.11'` field from docker-compose.yml

#### Problem: Docker Desktop API Communication Error
- **Issue**: Docker Desktop Linux engine communication failure
- **Error**: `request returned 500 Internal Server Error for API route and version`
- **Root Cause**: Docker Desktop internal communication between Windows client and Linux engine
- **Solution**: 
  - Restart Docker Desktop completely
  - Reset to factory defaults if restart doesn't work
  - Alternative: Use local PostgreSQL database for development

### 6.2 Database Configuration Issues

#### Problem: Remote Database Connection Failure
- **Issue**: Remote PostgreSQL database hostname resolution failure
- **Error**: `could not translate host name "dpg-d27dg3m3jp1c73f4p9v0-a" to address`
- **Root Cause**: Remote database service was inaccessible or deactivated
- **Solution**: 
  - Switched to local PostgreSQL database for development
  - Updated docker-compose.yml with local database service
  - Added health checks for database service

#### Problem: Database User Authentication
- **Issue**: PostgreSQL user authentication failure
- **Error**: `password authentication failed for user "project_dashboard_user"`
- **Root Cause**: Database volume contained old data with different user configuration
- **Solution**: 
  - Removed existing volumes with `docker compose down -v`
  - Recreated containers with fresh database initialization

### 6.3 JWT Authentication Issues

#### Problem: Token Validation Error
- **Issue**: JWT token validation failing with "Token has wrong type" error
- **Error**: `"Given token not valid for any token type"`
- **Root Cause**: Missing JWT configuration settings in Django settings
- **Solution**: 
  - Added comprehensive JWT settings to `settings.py`:
    ```python
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
        'ALGORITHM': 'HS256',
        'SIGNING_KEY': SECRET_KEY,
        'AUTH_HEADER_TYPES': ('Bearer',),
        'USER_ID_FIELD': 'id',
        'USER_ID_CLAIM': 'user_id',
        'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
        'TOKEN_TYPE_CLAIM': 'token_type',
    }
    ```
  - Restarted containers to apply new settings

### 6.4 API Documentation Issues

#### Problem: Outdated API Documentation
- **Issue**: API documentation didn't match actual implementation
- **Root Cause**: Field names and required fields had changed during development
- **Solution**: 
  - Updated `API_DOCUMENTATION.md` with correct field names:
    - Milestone: `title` (not `name`)
    - Task: `title` (not `name`)
    - Comment: `content` (not `text`)
    - User registration: Added required `password2` field
  - Added missing health check endpoint documentation
  - Updated all cURL examples with correct field names and required fields
  - Added response status codes section

### 6.5 Testing and Validation

#### Problem: API Test Failures
- **Issue**: Test script was using incorrect field names and missing required fields
- **Root Cause**: Test data didn't match actual API requirements
- **Solution**: 
  - Updated `test_api.py` with correct field names
  - Added required fields for all API calls
  - Created `debug_token.py` for JWT token validation testing
  - Verified all 18 API endpoints are working correctly

## 7. Current System Status

### 7.1 Working Endpoints (18 total)
✅ **Authentication**: Register, Login, Token Refresh, User Details  
✅ **Projects**: Create, Read, Update, Delete, Progress, Total Hours  
✅ **Milestones**: Create, Read, Update, Delete  
✅ **Tasks**: Create, Read, Update, Delete, Log Time  
✅ **Comments**: Create, Read, Update, Delete  
✅ **Attachments**: Create, Read, Update, Delete  
✅ **System**: Health Check  

### 7.2 Infrastructure
✅ **Docker**: Local PostgreSQL database with health checks  
✅ **JWT**: Fully configured with proper token validation  
✅ **CORS**: Configured for frontend integration  
✅ **Static Files**: WhiteNoise serving with proper configuration  

### 7.3 Development Tools
✅ **Management Scripts**: `docker-commands.sh` and `docker-commands.bat`  
✅ **Testing**: Comprehensive API test suite  
✅ **Documentation**: Updated API documentation with accurate examples  
✅ **Debugging**: Token validation debug script  

## 8. Lessons Learned

1. **Docker Configuration**: Always exclude build-time generated directories from volume mounts
2. **JWT Setup**: Complete JWT configuration is essential for token validation
3. **Database Management**: Local development databases are more reliable than remote services
4. **Documentation**: Keep API documentation synchronized with implementation
5. **Testing**: Comprehensive testing helps catch configuration issues early

---

This process resulted in a secure, feature-rich, and well-documented project management API backend. All major features are covered by automated tests and documented for easy integration.
