# Gemini Chatbot Frontend

Production-ready Next.js frontend for Gemini LangGraph Chatbot.

## Features

- User authentication (login/signup)
- Real-time chat interface
- Session management
- Profile management
- Notification system
- Responsive design
- Dark mode
- Markdown support

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Gemini Chatbot
NEXT_PUBLIC_APP_DESCRIPTION=AI Chatbot with Memory
```

### 3. Run Development Server

```bash
npm run dev
```

Open http://localhost:3000

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend-new/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page (redirects)
│   ├── globals.css         # Global styles
│   ├── login/
│   │   └── page.tsx        # Login/signup page
│   └── chat/
│       └── page.tsx        # Chat page
├── components/
│   ├── Sidebar.tsx         # Session list, notifications
│   ├── ChatArea.tsx        # Message display, input
│   └── ProfileModal.tsx    # Profile editor
├── lib/
│   ├── api.ts              # API client
│   ├── store.ts            # Zustand state management
│   └── utils.ts            # Utility functions
├── .env.local              # Environment variables
├── package.json            # Dependencies
└── tailwind.config.ts      # Tailwind configuration
```

## API Integration

All API calls are in `lib/api.ts`:

- `authAPI.signup()` - Register user
- `authAPI.login()` - Login user
- `chatAPI.sendMessage()` - Send chat message
- `chatAPI.getSessions()` - Get session list
- `chatAPI.getProfile()` - Get user profile
- `chatAPI.getNotifications()` - Get notifications

## State Management

Using Zustand for global state:

- `user` - Current user
- `sessions` - Chat sessions
- `messages` - Current session messages
- `notifications` - Unread notifications
- `profile` - User profile data

## Styling

- Tailwind CSS for styling
- Dark mode by default
- Consistent color scheme
- Responsive design

## Deployment

### Vercel

```bash
vercel
```

### Netlify

```bash
npm run build
netlify deploy --prod --dir=.next
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_APP_NAME` - Application name
- `NEXT_PUBLIC_APP_DESCRIPTION` - Application description

## Features

### Authentication
- Login with email/password
- Signup with email/username/password
- JWT token storage
- Auto-redirect on auth

### Chat
- Real-time messaging
- Markdown rendering
- Auto-scroll to latest message
- Loading indicators
- Multi-line input (Shift+Enter)

### Sessions
- Create new sessions
- Switch between sessions
- Delete sessions
- Session history

### Profile
- View profile data
- Edit profile fields
- Auto-populated from conversations
- Custom fields support

### Notifications
- Real-time notifications
- Mark as read
- Auto-refresh every 10 seconds
- Notification count badge

## Troubleshooting

### API connection failed
- Check NEXT_PUBLIC_API_URL in .env.local
- Ensure backend is running
- Check CORS settings

### Authentication errors
- Clear localStorage
- Check token expiration
- Verify backend JWT settings

### Build errors
- Delete .next folder
- Run npm install
- Check Node.js version (18+)

## License

MIT
