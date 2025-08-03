# API Documentation & Justifications

This document describes all API endpoints for the Django REST project, including their purpose and design justification.

---

## Authentication & User Management

### POST `/register/`
- **Purpose:** Register a new user.
- **Justification:** Enables onboarding of new users with validation and secure password handling.

### POST `/login/`
- **Purpose:** Obtain JWT access and refresh tokens for authentication.
- **Justification:** Uses JWT for stateless, secure authentication suitable for modern REST APIs.

### POST `/token/refresh/`
- **Purpose:** Refresh JWT access token using a valid refresh token.
- **Justification:** Allows session extension without re-authentication, improving UX and security.

### GET `/me/`
- **Purpose:** Retrieve details of the authenticated user.
- **Justification:** Lets users view their own profile securely.

---

## Project Management

### GET/POST `/projects/`
- **Purpose:** List all projects or create a new project.
- **Justification:** Centralizes project creation and listing for organization and planning.

### GET/PUT/DELETE `/projects/<int:pk>/`
- **Purpose:** Retrieve, update, or delete a specific project.
- **Justification:** Enables full lifecycle management of projects.

### GET `/projects/<int:pk>/total_hours/`
- **Purpose:** Get total hours logged for a project.
- **Justification:** Tracks effort and progress for reporting and billing.

### GET `/projects/<int:pk>/progress/`
- **Purpose:** Get progress percentage of a project.
- **Justification:** Provides a quick overview of project completion for stakeholders.

---

## Milestone Management

### GET/POST `/milestones/`
- **Purpose:** List all milestones or create a new milestone.
- **Justification:** Supports project breakdown into manageable phases.

### GET/PUT/DELETE `/milestones/<int:pk>/`
- **Purpose:** Retrieve, update, or delete a specific milestone.
- **Justification:** Enables tracking and management of project milestones.

---

## Task Management

### GET/POST `/tasks/`
- **Purpose:** List all tasks or create a new task.
- **Justification:** Facilitates detailed work planning and assignment.

### GET/PUT/DELETE `/tasks/<int:pk>/`
- **Purpose:** Retrieve, update, or delete a specific task.
- **Justification:** Allows granular control over individual work items.

### POST `/tasks/<int:pk>/log_time/`
- **Purpose:** Log time spent on a task.
- **Justification:** Enables time tracking for productivity and billing.

---

## Comment Management

### GET/POST `/comments/`
- **Purpose:** List all comments or add a new comment.
- **Justification:** Supports collaboration and communication on tasks/projects.

### GET/PUT/DELETE `/comments/<int:pk>/`
- **Purpose:** Retrieve, update, or delete a specific comment.
- **Justification:** Allows moderation and management of user feedback.

---

## Attachment Management

### GET/POST `/attachments/`
- **Purpose:** List all attachments or upload a new attachment.
- **Justification:** Enables sharing of files and resources related to tasks/projects.

### GET/PUT/DELETE `/attachments/<int:pk>/`
- **Purpose:** Retrieve, update, or delete a specific attachment.
- **Justification:** Provides control over project-related documents and files.

---

## Example cURL Commands

> Replace `<BASE_URL>` with your API server URL (e.g., http://localhost:8000)
> Replace `<ACCESS_TOKEN>` with your JWT access token where required

### Register
```bash
curl -X POST <BASE_URL>/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass", "email": "user@example.com"}'
```

### Login (JWT Token)
```bash
curl -X POST <BASE_URL>/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Refresh Token
```bash
curl -X POST <BASE_URL>/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}'
```

### Get Current User
```bash
curl -X GET <BASE_URL>/me/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### List/Create Projects
```bash
# List
curl -X GET <BASE_URL>/projects/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# Create
curl -X POST <BASE_URL>/projects/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Project Name", "description": "Desc"}'
```

### Project Detail/Update/Delete
```bash
# Get
curl -X GET <BASE_URL>/projects/<PROJECT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# Update
curl -X PUT <BASE_URL>/projects/<PROJECT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'

# Delete
curl -X DELETE <BASE_URL>/projects/<PROJECT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Project Total Hours
```bash
curl -X GET <BASE_URL>/projects/<PROJECT_ID>/total_hours/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Project Progress
```bash
curl -X GET <BASE_URL>/projects/<PROJECT_ID>/progress/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### List/Create Milestones
```bash
curl -X GET <BASE_URL>/milestones/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X POST <BASE_URL>/milestones/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Milestone Name", "project": <PROJECT_ID>}'
```

### Milestone Detail/Update/Delete
```bash
curl -X GET <BASE_URL>/milestones/<MILESTONE_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X PUT <BASE_URL>/milestones/<MILESTONE_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'

curl -X DELETE <BASE_URL>/milestones/<MILESTONE_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### List/Create Tasks
```bash
curl -X GET <BASE_URL>/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X POST <BASE_URL>/tasks/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Task Name", "milestone": <MILESTONE_ID>}'
```

### Task Detail/Update/Delete
```bash
curl -X GET <BASE_URL>/tasks/<TASK_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X PUT <BASE_URL>/tasks/<TASK_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'

curl -X DELETE <BASE_URL>/tasks/<TASK_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Log Time Against Task
```bash
curl -X POST <BASE_URL>/tasks/<TASK_ID>/log_time/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"hours": 2.5}'
```

### List/Create Comments
```bash
curl -X GET <BASE_URL>/comments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X POST <BASE_URL>/comments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Comment", "task": <TASK_ID>}'
```

### Comment Detail/Update/Delete
```bash
curl -X GET <BASE_URL>/comments/<COMMENT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X PUT <BASE_URL>/comments/<COMMENT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Updated Comment"}'

curl -X DELETE <BASE_URL>/comments/<COMMENT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### List/Create Attachments
```bash
curl -X GET <BASE_URL>/attachments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X POST <BASE_URL>/attachments/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@/path/to/file" \
  -F "task"=<TASK_ID>
```

### Attachment Detail/Update/Delete
```bash
curl -X GET <BASE_URL>/attachments/<ATTACHMENT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

curl -X PUT <BASE_URL>/attachments/<ATTACHMENT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@/path/to/newfile"

curl -X DELETE <BASE_URL>/attachments/<ATTACHMENT_ID>/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

---

## Design Justifications
- **RESTful Structure:** All endpoints follow REST conventions for clarity and interoperability.
- **JWT Authentication:** Ensures secure, stateless user sessions.
- **Granular Endpoints:** Separate endpoints for CRUD, time logging, and progress tracking support modularity and scalability.
- **Role-based Access:** (If implemented) Ensures only authorized users can access/modify resources.
- **Extensibility:** The API structure allows easy addition of new features (e.g., notifications, reporting).

---

For further details on request/response formats, refer to the OpenAPI/Swagger documentation generated by drf-spectacular.
