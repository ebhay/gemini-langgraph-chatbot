# API Documentation

Base URL: `http://localhost:8000`

## Authentication

All endpoints under `/api/*` require Bearer token authentication.

### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## Endpoints

### Authentication Endpoints

#### POST /auth/signup
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

**Errors:**
- 400: Email already registered
- 400: Username already taken
- 400: Invalid email format
- 400: Password too short (min 8 characters)
- 400: Username too short (min 3 characters)

#### POST /auth/login
Login with existing credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true
  }
}
```

**Errors:**
- 401: Incorrect email or password
- 403: Account is inactive

#### GET /auth/me
Get current user information.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-05-05T10:30:00Z"
}
```

**Errors:**
- 401: Invalid or expired token
- 401: User not found

#### POST /auth/logout
Logout current user.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "message": "Successfully logged out"
}
```

### Chat Endpoints

#### POST /api/chat
Send a message to the chatbot.

**Headers:** Requires authentication

**Request Body:**
```json
{
  "user_input": "Hello, my name is John and I am 25 years old",
  "session_id": "default"
}
```

**Response (200):**
```json
{
  "response": "Hello John! Nice to meet you. I've noted that you're 25 years old. How can I help you today?"
}
```

**Special Triggers:**
- "hospital" → Activates hospital finder tool
- "remind me" → Activates reminder scheduler

**Examples:**

Hospital Finder:
```json
{
  "user_input": "Find hospitals in Delhi",
  "session_id": "default"
}
```

Reminder:
```json
{
  "user_input": "Remind me to drink water",
  "session_id": "default"
}
```

**Errors:**
- 400: Empty user input
- 401: Authentication required
- 500: AI service error

#### GET /api/profile
Get user profile data.

**Headers:** Requires authentication

**Response (200):**
```json
{
  "age": 25,
  "city": "New York",
  "country": "USA",
  "occupation": "Software Engineer",
  "interests": "coding, reading",
  "preferences": "dark mode",
  "name": "John"
}
```

**Note:** Profile is automatically populated from conversations when user mentions personal facts.

#### POST /api/profile
Update user profile data.

**Headers:** Requires authentication

**Request Body:**
```json
{
  "key": "city",
  "value": "San Francisco"
}
```

**Response (200):**
```json
{
  "status": "success"
}
```

**Standard Fields:**
- age (integer)
- city (string)
- country (string)
- occupation (string)
- interests (string)
- preferences (string)

**Custom Fields:** Any other key-value pairs are stored in additional_data

#### GET /api/sessions
Get all chat sessions for current user.

**Headers:** Requires authentication

**Response (200):**
```json
[
  {
    "id": "default",
    "last_active": "2026-05-05T10:30:00Z",
    "first_message": "Hello, my name is John"
  },
  {
    "id": "session_123",
    "last_active": "2026-05-04T15:20:00Z",
    "first_message": "Find hospitals in Delhi"
  }
]
```

#### GET /api/sessions/{session_id}
Get full conversation history for a session.

**Headers:** Requires authentication

**Path Parameters:**
- session_id: Session identifier

**Response (200):**
```json
[
  {
    "role": "user",
    "text": "Hello, my name is John",
    "created_at": "2026-05-05T10:30:00Z"
  },
  {
    "role": "bot",
    "text": "Hello John! How can I help you today?",
    "created_at": "2026-05-05T10:30:01Z"
  },
  {
    "role": "user",
    "text": "I am 25 years old",
    "created_at": "2026-05-05T10:31:00Z"
  },
  {
    "role": "bot",
    "text": "Thank you for sharing that, John. I've noted that you're 25 years old.",
    "created_at": "2026-05-05T10:31:02Z"
  }
]
```

#### DELETE /api/sessions/{session_id}
Delete a chat session and all its messages.

**Headers:** Requires authentication

**Path Parameters:**
- session_id: Session identifier

**Response (200):**
```json
{
  "status": "success"
}
```

**Errors:**
- 401: Authentication required
- 500: Database error

#### GET /api/notifications
Get unread notifications for current user.

**Headers:** Requires authentication

**Response (200):**
```json
[
  {
    "id": 1,
    "message": "Reminder: drink water",
    "created_at": "2026-05-05T10:40:00Z",
    "type": "reminder"
  },
  {
    "id": 2,
    "message": "Reminder: Your task is complete!",
    "created_at": "2026-05-05T10:45:00Z",
    "type": "reminder"
  }
]
```

**Note:** Notifications are created by the reminder scheduler after 10 seconds delay.

#### POST /api/notifications/read/{notif_id}
Mark a notification as read.

**Headers:** Requires authentication

**Path Parameters:**
- notif_id: Notification ID

**Response (200):**
```json
{
  "status": "success"
}
```

**Errors:**
- 404: Notification not found
- 401: Authentication required

#### DELETE /api/notifications/{notif_id}
Delete a notification.

**Headers:** Requires authentication

**Path Parameters:**
- notif_id: Notification ID

**Response (200):**
```json
{
  "status": "success"
}
```

**Errors:**
- 404: Notification not found
- 401: Authentication required

### Health Endpoints

#### GET /
API information.

**Response (200):**
```json
{
  "message": "Gemini LangGraph Chatbot API",
  "version": "1.0.0",
  "status": "running"
}
```

#### GET /health
Health check endpoint.

**Response (200):**
```json
{
  "status": "healthy"
}
```

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

## Rate Limiting

Gemini API has rate limits. The backend implements exponential backoff:
- Retry 1: Wait 5 seconds
- Retry 2: Wait 10 seconds
- Retry 3: Wait 20 seconds
- After 3 retries: Return rate limit error

## Authentication Flow

1. User signs up: POST /auth/signup
2. Receive JWT token in response
3. Store token securely (localStorage, secure cookie)
4. Include token in Authorization header for all /api/* requests
5. Token expires after 7 days (configurable)
6. User logs in again when token expires

## Session Management

- Sessions are user-scoped
- Each user can have multiple sessions
- Session IDs are strings (e.g., "default", "session_123")
- Sessions persist across logins
- Delete sessions to clear history

## Profile Extraction

The chatbot automatically extracts facts from conversations:

User says: "I am 25 years old"
Bot extracts: {"age": "25"}
Stored in user profile

User says: "I live in New York"
Bot extracts: {"city": "New York"}
Stored in user profile

## Tools

### Hospital Finder
Triggered by: "hospital" keyword in user input
API: OpenStreetMap Nominatim
Returns: List of hospitals near specified location
Fallback: Static hospital names if API fails

### Reminder Scheduler
Triggered by: "remind me" keyword in user input
Delay: 10 seconds
Action: Creates notification + sends email
Email: Sent to user's registered email address

## Email Notifications

Emails are sent for:
1. Welcome email on signup
2. Reminder notifications
3. Password reset (template ready)

Email format: HTML + plain text
SMTP: Gmail with app password

## Performance

Target metrics:
- Chat response: <15 seconds (p95)
- Database queries: <100ms
- Email delivery: <5 seconds
- Background tasks: 10 seconds delay

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## WebSocket Support

Not implemented. Use polling for notifications:
- Poll GET /api/notifications every 10 seconds
- Mark as read after displaying

## Future Enhancements

- Refresh tokens
- Email verification
- Password reset flow
- WebSocket support
- File upload
- Voice messages
- Multi-language support
- Custom tools
- Analytics dashboard
