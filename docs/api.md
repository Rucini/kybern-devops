# REST API Documentation

Base URL: `/api`
All protected routes require an `Authorization` header containing a valid JWT token.

`Authorization: Bearer <token>`

## Auth Endpoints

### POST `/api/auth/login`
Authenticates a user.
- **Request Body:** `{ "username": "...", "password": "..." }`
- **Response:** `200 OK`
  ```json
  {
    "access_token": "eyJhb...",
    "user": { "id": 1, "username": "admin", "email": "admin@example.com", "role": "admin" }
  }
  ```

### POST `/api/auth/register`
Registers a new user.
- **Request Body:** `{ "username": "...", "email": "...", "password": "..." }`
- **Response:** `201 Created`

## Main Endpoints

### GET `/api/main/dashboard`
Returns dashboard statistics.
- **Requires:** Valid JWT
- **Response:** `200 OK`
  ```json
  {
    "open_tickets": 2,
    "in_progress_tickets": 1,
    "resolved_tickets": 5,
    "recent_tickets": [...]
  }
  ```

## Ticket Endpoints

### GET `/api/tickets/`
List tickets for the current user.
- **Query Params:** `page`
- **Response:** `200 OK` `{ "items": [...], "total": 10, "pages": 1, "current_page": 1 }`

### POST `/api/tickets/`
Create a ticket. Requires `multipart/form-data`.
- **Form Fields:** `title`, `description`, `category`, `priority`, `attachment` (optional file)
- **Response:** `201 Created` `{ "message": "...", "ticket": {...} }`

### GET `/api/tickets/<id>`
Get ticket details.
- **Response:** `200 OK` `{ ...ticket, "comments": [...] }`

### POST `/api/tickets/<id>/comments`
Add a comment to a ticket.
- **Request Body:** `{ "body": "..." }`
- **Response:** `201 Created`

### POST `/api/tickets/<id>/close`
Closes the ticket.
- **Response:** `200 OK`

### GET `/api/tickets/download/<filename>`
Download an attachment.
- **Response:** File stream

## Admin Endpoints

Requires Admin privileges.

### GET `/api/admin/tickets`
List all tickets. Pagination and filtering supported.

### PUT `/api/admin/tickets/<id>/assign`
Assign ticket to a user.
- **Request Body:** `{ "assignee_id": 2 }`

### PUT `/api/admin/tickets/<id>/status`
Change ticket status.
- **Request Body:** `{ "status": "In Progress" }`

### DELETE `/api/admin/tickets/<id>`
Delete a ticket.

### GET `/api/admin/users`
List all users.

### POST `/api/admin/users/<id>/reset_password`
Reset a user's password to `password123`.
