# Frontend Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
cd frontend-new
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

Open http://localhost:3000

## Production Build

```bash
npm run build
npm start
```

## Features

- Login/Signup pages
- Chat interface with sidebar
- Session management
- Profile editor
- Notifications
- Dark mode
- Responsive design

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Zustand (state management)
- Axios (API client)
- React Markdown

## File Structure

```
app/
  layout.tsx       - Root layout
  page.tsx         - Home (redirect)
  globals.css      - Global styles
  login/
    page.tsx       - Auth page
  chat/
    page.tsx       - Chat page

components/
  Sidebar.tsx      - Sessions & notifications
  ChatArea.tsx     - Messages & input
  ProfileModal.tsx - Profile editor

lib/
  api.ts           - API client
  store.ts         - State management
  utils.ts         - Utilities
```

## Deployment

### Vercel
```bash
vercel
```

### Netlify
```bash
npm run build
netlify deploy --prod
```

### Docker
```bash
docker build -t chatbot-frontend .
docker run -p 3000:3000 chatbot-frontend
```

## Environment Variables

Required:
- `NEXT_PUBLIC_API_URL` - Backend API URL

Optional:
- `NEXT_PUBLIC_APP_NAME` - App name
- `NEXT_PUBLIC_APP_DESCRIPTION` - App description
