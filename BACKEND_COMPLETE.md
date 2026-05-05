# Complete Backend Implementation

## Overview

Full-featured production-ready backend for Gemini + LangGraph chatbot with:
- User authentication (JWT)
- Email notifications (Gmail SMTP)
- Multi-user support
- Session management
- Profile management
- Memory system (short-term + long-term)
- LangGraph orchestration
- Hospital finder tool
- Reminder scheduler
- Background tasks
- Performance logging

## File Structure

```
backend/
├── main.py                      # FastAPI app entry point
├── config.py                    # Centralized configuration
├── database.py                  # SQLAlchemy database setup
├── models.py                    # Database models (User, Conversation, Profile, Notification)
├── auth.py                      # JWT authentication utilities
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (fill in values)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── run.py                       # Development server runner
├── test_api.py                  # API testing script
├── setup.bat                    # Windows setup script
├── setup.sh                     # Linux/Mac setup script
├── alembic.ini                  # Database migration config
├── README_SETUP.md              # Detailed setup instructions
├── QUICK_START.md               # Quick start guide
├── API_DOCUMENTATION.md         # Complete API documentation
├── IMPLEMENTATION_SUMMARY.md    # Implementation details
├── routes/
│   ├── auth.py                  # Authentication endpoints
│   └── chat.py                  # Chat, profile, session, notification endpoints
└── services/
    ├── gemini_service.py        # Gemini API wrapper with retry logic
    ├── langgraph_service.py     # LangGraph orchestration
    ├── memory_service.py        # Conversation history management
    ├── profile_service.py       # User profile management
    ├── tool_service.py          # Hospital finder tool
    ├── scheduler_service.py     # Background task scheduler
    └── email_service.py         # Email notification service
```

## Quick Setup

### 1. Run Setup Script

Windows:
```bash
cd backend
setup.bat
```

Linux/Mac:
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 2. Configure .env

Edit `backend/.env` and add:

```env
JWT_SECRET_KEY=<generate_with_python_command>
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=<gmail_app_password>
SMTP_FROM_EMAIL=your_email@gmail.com
```

Generate JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Get Gmail app password:
1. Enable 2FA on Gmail
2. Go to Security > App Passwords
3. Generate password for "Mail"
4. Copy to SMTP_PASSWORD

### 3. Start Server

```bash
python run.py
```

Server: http://localhost:8000
API Docs: http://localhost:8000/docs

### 4. Test API

```bash
python test_api.py
```

## API Endpoints

### Authentication
- POST `/auth/signup` - Register user
- POST `/auth/login` - Login user
- GET `/auth/me` - Get current user
- POST `/auth/logout` - Logout user

### Chat
- POST `/api/chat` - Send message
- GET `/api/profile` - Get user profile
- POST `/api/profile` - Update profile
- GET `/api/sessions` - List sessions
- GET `/api/sessions/{id}` - Get session history
- DELETE `/api/sessions/{id}` - Delete session
- GET `/api/notifications` - Get notifications
- POST `/api/notifications/read/{id}` - Mark as read
- DELETE `/api/notifications/{id}` - Delete notification

### Health
- GET `/` - API info
- GET `/health` - Health check

## Database Schema

### users
- id, email, username, password_hash, full_name
- is_active, is_verified, created_at, updated_at, last_login

### conversations
- id, user_id, session_id, user_input, bot_response, created_at

### user_profiles
- id, user_id, age, city, country, occupation
- interests, preferences, additional_data, created_at, updated_at

### notifications
- id, user_id, message, notification_type
- is_read, is_emailed, created_at

## Features Implemented

### ✅ User Authentication
- JWT-based authentication
- Secure password hashing (bcrypt)
- Token expiration (7 days default)
- Protected routes
- User session tracking

### ✅ Email Notifications
- Gmail SMTP integration
- Welcome email on signup
- Reminder notification emails
- HTML + plain text support
- Email delivery tracking

### ✅ Multi-User Support
- User-scoped conversations
- User-scoped profiles
- User-scoped notifications
- User-scoped sessions
- Isolated user data

### ✅ Memory System
- Short-term: Last 5 conversations per session
- Long-term: User profile facts
- Automatic fact extraction
- Session-scoped history
- Profile update tracking

### ✅ LangGraph Orchestration
- Router node for intelligent routing
- Chat node for conversations
- Tool node for hospital finder
- Scheduler node for reminders
- Conditional edge routing

### ✅ Hospital Finder Tool
- OpenStreetMap Nominatim API
- Real-time data fetching
- Location extraction
- Graceful fallback

### ✅ Reminder Scheduler
- APScheduler integration
- 10-second delay
- Notification creation
- Email triggering
- User-scoped tasks

### ✅ Performance Monitoring
- Request timing middleware
- Database query timing
- Performance logging
- P95 latency tracking

### ✅ Error Handling
- Gemini API rate limit handling
- Exponential backoff (5s, 10s, 20s)
- Database transaction rollback
- User-friendly error messages
- Comprehensive logging

### ✅ Security
- Password hashing
- JWT tokens
- Protected routes
- CORS configuration
- Input validation

## Environment Variables

All variables in `.env`:

```env
GEMINI_API_KEY=                  # Your Gemini API key
GEMINI_MODEL=gemini-1.5-flash    # Model name
DATABASE_URL=sqlite:///./chat.db # Database connection
JWT_SECRET_KEY=                  # Generate with secrets.token_hex(32)
JWT_ALGORITHM=HS256              # JWT algorithm
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
SMTP_HOST=smtp.gmail.com         # SMTP server
SMTP_PORT=587                    # SMTP port
SMTP_USER=                       # Your Gmail
SMTP_PASSWORD=                   # Gmail app password
SMTP_FROM_EMAIL=                 # Your Gmail
SMTP_FROM_NAME=Gemini Chatbot    # From name
CORS_ORIGINS=*                   # Allowed origins
MAX_HISTORY_LIMIT=5              # Conversation history limit
NOTIFICATION_POLL_INTERVAL=10    # Polling interval
RATE_LIMIT_MAX_RETRIES=3         # Gemini retry attempts
RATE_LIMIT_BACKOFF_BASE=5        # Retry backoff base
```

## Testing

### Manual Testing
```bash
python test_api.py
```

Tests:
- User signup
- User login
- Chat functionality
- Profile management
- Hospital finder
- Reminder scheduler
- Session management
- Notifications

### cURL Examples

Signup:
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123","full_name":"Test User"}'
```

Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Chat:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"user_input":"Hello, my name is John","session_id":"default"}'
```

## Production Deployment

### Railway
```bash
railway login
railway init
railway add
railway up
```

Set environment variables in Railway dashboard.

### Render
1. Connect GitHub repo
2. Set environment variables
3. Deploy

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 chatbot-backend
```

### PostgreSQL for Production

Update `.env`:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

Install adapter:
```bash
pip install psycopg2-binary
```

## Performance Targets

- Chat response: <15 seconds (p95)
- Database queries: <100ms
- Email delivery: <5 seconds
- Background tasks: 10 seconds delay
- JWT token expiration: 7 days

## Documentation Files

- `README_SETUP.md` - Detailed setup instructions
- `QUICK_START.md` - Quick start guide
- `API_DOCUMENTATION.md` - Complete API reference
- `IMPLEMENTATION_SUMMARY.md` - Architecture details
- `BACKEND_COMPLETE.md` - This file

## Troubleshooting

### Email not sending
- Check Gmail app password
- Verify 2FA enabled
- Check SMTP settings

### JWT errors
- Generate new JWT_SECRET_KEY
- Check token expiration

### Database errors
- Delete chat.db and restart
- Check DATABASE_URL format

### Gemini API errors
- Verify API key
- Check rate limits
- Ensure model name correct

### Port in use
```bash
lsof -ti:8000 | xargs kill -9
```

## Next Steps

1. ✅ Fill in .env variables
2. ✅ Generate JWT secret key
3. ✅ Set up Gmail app password
4. ✅ Run setup script
5. ✅ Start server
6. ✅ Test all endpoints
7. ⬜ Deploy to production
8. ⬜ Monitor performance
9. ⬜ Add frontend integration

## Support

For issues or questions:
1. Check documentation files
2. Review error logs
3. Test with test_api.py
4. Check environment variables
5. Verify database schema

## License

MIT License

## Credits

Built with:
- FastAPI
- Google Gemini
- LangGraph
- SQLAlchemy
- APScheduler
- bcrypt
- PyJWT
