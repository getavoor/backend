# Avoor API Documentation

Avoor's API, with user authentication, task management, and plancoin rewards system.

## Base URL (development)

```
http://localhost:8080
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Refresh

Access tokens can be refreshed using the refresh token endpoint.

---

## Authentication Routes

### `/api/register`

Registers a new user.

```http
POST /api/register
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 digit
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 symbol

**Response (200):**
```json
{
  "msg": "Please check your email.",
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Responses:**
- `400`: Invalid credentials, password requirements not met, or user already exists

---

### `/api/login`

Signs the user in and provides new tokens.

```http
POST /api/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "photoUrl": "https://...",
  "confirmed": true,
  "plancoins": 100,
  "currentStreak": 5,
  "longestStreak": 10,
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refreshToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Error Response:**
- `400`: Invalid login credentials

---

### Confirm Email

Confirms the user's email based on a confirmation token.

This should be called after the user receives an email and taps on the link in it.

```http
POST /api/confirm
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "token": "confirmation_token_from_email"
}
```

**Response (200):**
```json
{
  "msg": "You have confirmed your account!",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "photoUrl": "https://...",
    "confirmed": true,
    "plancoins": 0,
    "currentStreak": 0,
    "longestStreak": 0
  }
}
```

---

### Resend Confirmation Email

Resends the confirmation email for this user.

**Note:** Only works for unconfirmed users.

```http
POST /api/resend
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "msg": "OK"
}
```

---

### Refresh Access Token

Provides a new access token.

**Note:** This endpoint uses the user's **refresh token** instead of the access token.

```http
POST /api/refreshToken
```

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## User Routes

### Get Current User Info

Returns info about the user.

```http
GET /api/me
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "photoUrl": "https://...",
  "confirmed": true,
  "plancoins": 100,
  "currentStreak": 5,
  "longestStreak": 10
}
```

---

#### Delete Account

```http
DELETE /api/me
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "msg": "OK"
}
```

**Note:** This permanently deletes the user account and all associated data.

---

#### Upload Profile Picture

```http
POST /api/setPicture
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `picture`: Image file (PNG or JPG)

**Response (200):**
```json
{
  "msg": "Success",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "photoUrl": "https://storage.../profile/1/pfp12345678.jpg",
    "confirmed": true,
    "plancoins": 100,
    "currentStreak": 5,
    "longestStreak": 10
  }
}
```

**Error Responses:**
- `400`: No file uploaded, invalid file type, or image too small

**Requirements:**
- Accepted formats: PNG, JPG
- Minimum resolution: 500x500 pixels
- Images are automatically compressed and cropped to 500x500

---

## Task Management Routes

### Get All Tasks

Returns all of the user's tasks

```http
GET /api/tasks
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Complete project report",
      "description": "Finish the Q4 analysis report",
      "isCompleted": false,
      "createdAt": "2025-12-30T10:00:00",
      "completedAt": null,
      "dueDate": "2025-12-31T23:59:59",
      "priority": 3
    }
  ]
}
```

---

### Create Task

Creates a task with a provided name and description.

```http
POST /api/tasks
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "Complete project report",
  "description": "Finish the Q4 analysis report",
  "priority": 3,
  "dueDate": "2025-12-31T23:59:59"
}
```

**Fields:**
- `title` (required): Task title
- `description` (optional): Task description
- `priority` (optional): 1 (low), 2 (medium), 3 (high) - defaults to 2
- `dueDate` (optional): ISO format datetime string

**Response (200):**
```json
{
  "msg": "Success",
  "task": {
    "id": 1,
    "title": "Complete project report",
    "description": "Finish the Q4 analysis report",
    "isCompleted": false,
    "createdAt": "2025-12-30T10:00:00",
    "priority": 3
  }
}
```

**Error Response:**
- `400`: Missing title

---

### Update Task

Updates a task.

```http
PUT /api/tasks/<task_id>
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (all fields optional):**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "priority": 2,
  "isCompleted": true,
  "dueDate": "2025-12-31T23:59:59"
}
```

**Response (200):**
```json
{
  "msg": "Success"
}
```

**Error Response:**
- `404`: Task not found

**Note:** When marking a task as completed (`isCompleted: true`), the completion timestamp is automatically set.

---

### Delete Task

Deletes a task.

```http
DELETE /api/tasks/<task_id>
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "msg": "Success"
}
```

**Error Response:**
- `404`: Task not found

---

## Plancoin Routes

### Add Plancoins

```http
POST /api/plancoins/add
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "amount": 50,
  "reason": "Task completion reward"
}
```

**Fields:**
- `amount` (required): Positive integer
- `reason` (optional): Description of the transaction

**Response (200):**
```json
{
  "msg": "Success",
  "plancoins": 150
}
```

**Error Responses:**
- `400`: Missing amount or invalid amount (must be positive integer)

**Note:** Currently, plancoins are added from the client side. Server-side validation ensures integrity.

---

### Get Plancoin History

```http
GET /api/plancoins/history
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "transactions": [
    {
      "id": 1,
      "amount": 50,
      "reason": "Task completion reward",
      "createdAt": "2025-12-30T10:00:00"
    },
    {
      "id": 2,
      "amount": 100,
      "reason": "Weekly streak bonus",
      "createdAt": "2025-12-29T10:00:00"
    }
  ]
}
```

**Note:** Transactions are ordered by creation date (newest first).

---

### Get Streak Information

```http
GET /api/streak
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "currentStreak": 5,
  "longestStreak": 10,
  "lastCompletionDate": "2025-12-30"
}
```

**Note:** Streak functionality is tracked but not yet fully implemented for automatic updates.

---

## Feedback Routes

This is related to the delete account functionality.

### Send Feedback

```http
POST /api/sendFeedback
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "id": "feedback_type_id",
  "reason": "Optional detailed explanation"
}
```

**Response (200):**
```json
{
  "msg": "Success"
}
```

**Error Response:**
- `400`: Missing feedback ID

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid data)
- `403`: Unauthorized (invalid or missing token)
- `404`: Resource not found

Error responses include a descriptive message:

```json
{
  "msg": "Error description here"
}
```

---

## Authentication States

The API enforces different authentication requirements:

- **Unauthenticated**: Can register and login
- **Authenticated but unconfirmed**: Can access basic endpoints and resend confirmation
- **Authenticated and confirmed**: Full access to all features

---

## Rate Limiting & Security

- Passwords are hashed using PBKDF2-SHA512
- JWT tokens expire and must be refreshed
- Email confirmation required for full access
- Profile pictures are automatically compressed and validated
- SQL injection protection through SQLAlchemy ORM

---

## AI planning

The API includes WebSocket support via Socket.IO for AI planning (currently not implemented):

**Connect to:** `ws://localhost:8080/socket.io/`

**Available commands:**
- `enter`: Authenticate with JWT token
- `compat`: Check protocol compatibility

See `server/discovery.py` for implementation details.

---

## Development Notes

- The codebase includes commented-out restaurant management features (appears to be from a previous "Gemifood" project)
- Streak calculation is tracked but not automatically updated
- LangChain integration exists for AI-powered time planning (in `server/langchain/`)
- File storage supports both local folders and Google Cloud Storage
