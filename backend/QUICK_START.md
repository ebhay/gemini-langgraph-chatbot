# Quick Start Guide

## 1. Run Setup Script

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## 2. Configure Environment

Edit `.env` file and add:

### Required
```env
JWT_SECRET_KEY=<generate_with_command_below>
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=<gmail_app_password>
SMTP_FROM_EMAIL=your_email@gmail.com
```

### Generate JWT Secret
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Get Gmail App Password
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication
3. Go to "App passwords"
4. Generate password for "Mail"
5. Copy 16-character password to SMTP_PASSWORD

## 3. Start Server

```bash
python run.py
```

Server runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

## 4. Test API

```bash
python test_api.py
```

## 5. Example Requests

### Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Chat
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "user_input": "Hello, my name is John",
    "session_id": "default"
  }'
```

## Troubleshooting

### Port already in use
```bash
lsof -ti:8000 | xargs kill -9
```

### Database locked
```bash
rm chat.db
python run.py
```

### Email not sending
- Check Gmail app password
- Verify 2FA is enabled
- Check SMTP settings in .env

## Features to Test

1. User signup and login
2. Chat with memory
3. Profile extraction (say "I am 25 years old")
4. Hospital finder (say "Find hospitals in Delhi")
5. Reminders (say "Remind me to drink water")
6. Session management
7. Notifications (wait 10 seconds after reminder)

## Production Deployment

### Railway
```bash
railway login
railway init
railway add
railway up
```

### Render
1. Connect GitHub repo
2. Set environment variables
3. Deploy

### Docker
```bash
docker build -t chatbot-backend .
docker run -p 8000:8000 chatbot-backend
```

## Support

Check README_SETUP.md for detailed instructions
Check IMPLEMENTATION_SUMMARY.md for architecture details
