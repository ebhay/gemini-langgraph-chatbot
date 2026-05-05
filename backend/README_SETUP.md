# Backend Setup Guide

## Prerequisites
- Python 3.10+
- Gmail account for email notifications

## Installation Steps

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Virtual Environment
Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and fill in the values:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

DATABASE_URL=sqlite:///./chat.db

JWT_SECRET_KEY=your_secret_key_here_use_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_FROM_EMAIL=your_email@gmail.com
SMTP_FROM_NAME=Gemini Chatbot

CORS_ORIGINS=http://localhost:3000,http://localhost:8000

MAX_HISTORY_LIMIT=5
NOTIFICATION_POLL_INTERVAL=10

RATE_LIMIT_MAX_RETRIES=3
RATE_LIMIT_BACKOFF_BASE=5
```

### 5. Gmail App Password Setup
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security > App Passwords
4. Generate new app password for "Mail"
5. Copy the 16-character password to `SMTP_PASSWORD` in `.env`

### 6. Generate JWT Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output to `JWT_SECRET_KEY` in `.env`

### 7. Run the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- POST `/auth/signup` - Register new user
- POST `/auth/login` - Login user
- GET `/auth/me` - Get current user info
- POST `/auth/logout` - Logout user

### Chat
- POST `/api/chat` - Send message (requires auth)
- GET `/api/profile` - Get user profile (requires auth)
- POST `/api/profile` - Update user profile (requires auth)
- GET `/api/sessions` - Get all sessions (requires auth)
- GET `/api/sessions/{session_id}` - Get session history (requires auth)
- DELETE `/api/sessions/{session_id}` - Delete session (requires auth)
- GET `/api/notifications` - Get unread notifications (requires auth)
- POST `/api/notifications/read/{notif_id}` - Mark notification as read (requires auth)
- DELETE `/api/notifications/{notif_id}` - Delete notification (requires auth)

### Health
- GET `/` - API info
- GET `/health` - Health check

## Testing

### Test Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123","full_name":"Test User"}'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Test Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"user_input":"Hello, my name is John","session_id":"default"}'
```

## Database Schema

### Users Table
- id (Primary Key)
- email (Unique)
- username (Unique)
- password_hash
- full_name
- is_active
- is_verified
- created_at
- updated_at
- last_login

### Conversations Table
- id (Primary Key)
- user_id (Foreign Key)
- session_id
- user_input
- bot_response
- created_at

### User Profiles Table
- id (Primary Key)
- user_id (Foreign Key, Unique)
- age
- city
- country
- occupation
- interests
- preferences
- additional_data (JSON)
- created_at
- updated_at

### Notifications Table
- id (Primary Key)
- user_id (Foreign Key)
- message
- notification_type
- is_read
- is_emailed
- created_at

## Features Implemented

1. User Authentication (JWT)
2. Email Notifications (Gmail SMTP)
3. Multi-user Support
4. Session Management
5. Profile Management
6. Memory System (Short-term + Long-term)
7. LangGraph Orchestration
8. Hospital Finder Tool
9. Reminder Scheduler
10. Background Tasks
11. Performance Logging
12. Rate Limit Handling

## Production Deployment

For production, replace SQLite with PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@host:port/database
```

Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

## Troubleshooting

### Email not sending
- Check Gmail app password is correct
- Ensure 2FA is enabled on Gmail account
- Check SMTP settings in .env

### JWT errors
- Ensure JWT_SECRET_KEY is set
- Check token expiration time

### Database errors
- Delete chat.db and restart to recreate tables
- Check DATABASE_URL format

### Gemini API errors
- Verify API key is valid
- Check rate limits
- Ensure model name is correct
