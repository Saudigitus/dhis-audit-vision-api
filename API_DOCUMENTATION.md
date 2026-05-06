# DHIS2 Audit Vision API Documentation

## Overview

This document provides comprehensive API documentation for the DHIS2 Audit Vision application, a FastAPI-based system for managing DHIS2 audit data, user authentication, notifications, and webhook integrations. The API follows RESTful conventions and uses JSON for request/response payloads.

### Base URL
```
http://localhost:8000/api
```

### Authentication
Most endpoints require authentication via JWT tokens obtained from the `/auth/login` endpoint. Include the token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

Superuser privileges are required for user management endpoints.

### Response Format
All responses are in JSON format. Successful responses include relevant data, while errors return standard HTTP status codes with descriptive messages.

### Pagination
List endpoints support pagination with `page` and `pageSize` query parameters. Responses include a `pager` object with pagination metadata.

---

## Authentication Endpoints

### POST /auth/login
Authenticate a user and obtain a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Errors:**
- 401: Invalid credentials
- 403: Inactive user

### GET /auth/me
Get current authenticated user information.

**Response (200):**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### POST /auth/users
Create a new user (superuser only).

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "is_superuser": false
}
```

**Response (200):** UserRead schema

### GET /auth/users
List all users (superuser only).

**Query Parameters:**
- `skip`: int (default: 0)
- `limit`: int (default: 100)

**Response (200):** Array of UserRead

### GET /auth/users/{user_id}
Get user by ID (superuser only).

**Response (200):** UserRead schema

### PATCH /auth/users/{user_id}
Update user (superuser only).

**Request Body:** UserUpdate schema

**Response (200):** UserRead schema

### DELETE /auth/users/{user_id}
Delete user (superuser only).

**Response (200):**
```json
{
  "message": "User deleted"
}
```

---

## Audit Endpoints

### POST /audits/create/
Create a new audit record.

**Request Body:** AuditCreate schema
```json
{
  "auditType": "CREATE",
  "auditScope": "METADATA",
  "klass": "string",
  "attributes": {},
  "createdBy": "string",
  "uid": "string",
  "code": "string"
}
```

**Response (200):** AuditRead schema

### GET /audits/{id}
Get audit by ID.

**Response (200):** AuditRead schema

### GET /audits
List audits with pagination and filtering.

**Query Parameters:**
- `page`: int (default: 1)
- `pageSize`: int (default: 50)
- Additional filters based on audit fields

**Response (200):**
```json
{
  "page": 1,
  "pageSize": 50,
  "total": 100,
  "data": [AuditRead]
}
```

### DELETE /audits/{id}
Delete audit by ID.

**Response (200):**
```json
{
  "message": "audit deleted"
}
```

### GET /audits/metadata/{id}
Get audits by metadata ID (program or dataset).

**Query Parameters:**
- `type`: "PROGRAM" or "DATASET"
- `page`: int (default: 1)
- `pageSize`: int (default: 50)

**Response (200):**
```json
{
  "page": 1,
  "pageSize": 50,
  "total": 10,
  "data": [AuditRead]
}
```

---

## Audit Object Endpoints

### POST /auditObjects/create/
Create a new audit object.

**Request Body:** AuditObjectCreate schema
```json
{
  "auditId": "string",
  "objectId": "string",
  "objectData": {},
  "auditScope": "METADATA",
  "auditType": "CREATE"
}
```

**Response (200):** AuditObjectRead schema

### GET /auditObjects/{id}
Get audit object by ID.

**Response (200):** AuditObjectRead schema

### GET /auditObjects
List audit objects with pagination and filtering.

**Query Parameters:**
- `page`: int (default: 1)
- `pageSize`: int (default: 50)
- Additional filters

**Response (200):**
```json
{
  "pager": {...},
  "auditObjects": [AuditObjectRead]
}
```

### DELETE /auditObjects/{id}
Delete audit object by ID.

**Response (200):**
```json
{
  "message": "audit object deleted"
}
```

---

## Webhook Endpoints

### POST /webhooks/dhis2/event
Receive DHIS2 event webhooks and trigger audit processing.

**Request Body:** (DHIS2 webhook payload)
```json
{
  "path": "string",
  "createdAt": "2023-01-01T00:00:00.000Z",
  ...
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Webhook received successfully"
}
```

**Response (500):**
```json
{
  "status": "error",
  "message": "Failed to process webhook"
}
```

---

## Notification Endpoints

### POST /notifications/create
Create a notification configuration.

**Request Body:** NotificationConfigCreate schema
```json
{
  "subject": "string",
  "objectType": "string",
  "action": "CREATE",
  "severity": "INFO",
  "messageTemplate": "string",
  "recipients": {
    "to": ["email@example.com"],
    "cc": [],
    "bcc": []
  }
}
```

**Response (200):** NotificationConfigRead schema

### GET /notifications
List notification configurations.

**Query Parameters:**
- `page`: int (default: 1)
- `pageSize`: int (default: 20)
- Additional filters

**Response (200):**
```json
{
  "pager": {...},
  "notifications": [NotificationConfigRead]
}
```

### GET /notifications/{id}
Get notification configuration by ID.

**Response (200):** NotificationConfigRead schema

### DELETE /notifications/{id}
Delete notification configuration by ID.

**Response (204):** No content

---

## Utility Endpoints

### GET /
Health check endpoint.

**Response (200):**
```json
{
  "message": "Welcome to the FastAPI Project - Integration of dhis2 and xAPI!"
}
```

### GET /endpoints/
List all available API endpoints.

**Response (200):**
```json
{
  "endpoints": [
    {
      "path": "/api/audits",
      "methods": ["GET"],
      "name": "get_audit_objects",
      "tags": ["Audits"]
    },
    ...
  ]
}
```

### POST /runAudit
Manually trigger audit process.

**Response (200):**
```json
{
  "message": "Audit process completed successfully."
}
```

### GET /logs
List available log files.

**Response (200):**
```json
{
  "logs": ["log1.txt", "log2.txt"]
}
```

### GET /logs/{log}
Get log file contents by name.

**Response (200):** Log data as JSON

---

## Data Models

### AuditType Enum
- CREATE
- UPDATE
- DELETE

### AuditScope Enum
- METADATA
- DATA

### ActionEnum
- CREATE
- UPDATE
- DELETE

### SeverityEnum
- INFO
- WARNING
- ERROR

### Schemas

#### AuditCreate
```json
{
  "auditType": "AuditType",
  "auditScope": "AuditScope",
  "klass": "string",
  "attributes": "object",
  "createdBy": "string",
  "uid": "string",
  "code": "string"
}
```

#### AuditRead
Extends AuditCreate with:
```json
{
  "id": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### AuditObjectCreate
```json
{
  "auditId": "string",
  "objectId": "string",
  "objectData": "object",
  "auditScope": "AuditScope",
  "auditType": "AuditType"
}
```

#### AuditObjectRead
Extends AuditObjectCreate with timestamps.

#### UserCreate
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "is_superuser": "boolean"
}
```

#### UserRead
Includes user details and timestamps.

#### NotificationConfigCreate
```json
{
  "subject": "string",
  "objectType": "string",
  "action": "ActionEnum",
  "severity": "SeverityEnum",
  "messageTemplate": "string",
  "recipients": {
    "to": ["string"],
    "cc": ["string"],
    "bcc": ["string"]
  }
}
```

#### NotificationConfigRead
Extends NotificationConfigCreate with ID and timestamps.

---

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a `detail` field with descriptive information.

---

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing appropriate limits for production use.

## Versioning

Current API version: 1.0.0

For questions or support, refer to the main project README or contact the development team.