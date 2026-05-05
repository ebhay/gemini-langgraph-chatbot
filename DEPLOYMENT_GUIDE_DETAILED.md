# 🚀 Comprehensive Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
   - [Railway](#deploy-to-railway)
   - [Render](#deploy-to-render)
   - [Google Cloud Run](#deploy-to-google-cloud-run)
3. [Frontend Deployment](#frontend-deployment)
   - [Vercel](#deploy-to-vercel)
   - [Netlify](#deploy-to-netlify)
4. [Database Setup](#database-setup)
5. [Environment Variables](#environment-variables)
6. [Post-Deployment](#post-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))
- ✅ GitHub account (for connecting repositories)
- ✅ Domain name (optional, but recommended)
- ✅ SMTP credentials (optional, for email notifications)

---

## Backend Deployment

### Deploy to Railway

Railway is the easiest option for deploying the FastAPI backend.

#### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"

#### Step 2: Deploy from GitHub
1. Click "Deploy from GitHub repo"
2. Select your repository
3. Railway will auto-detect it's a Python project

#### Step 3: Configure Environment Variables
In the Railway dashboard, go to "Variables" and add:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
JWT_SECRET_KEY=your_secret_key_here_generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
DATABASE_URL=postgresql://user:pass@host:port/dbname
CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-custom-domain.com
MAX_HISTORY_LIMIT=5
RATE_LIMIT_MAX_RETRIES=3
RATE_LIMIT_BACKOFF_BASE=5
```

**Generate JWT Secret:**
```bash
openssl rand -hex 32
```

#### Step 4: Add PostgreSQL Database
1. In Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL`
4. No manual configuration needed!

#### Step 5: Configure Start Command
In Railway settings, set:
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Root Directory:** `backend`

#### Step 6: Deploy
1. Click "Deploy"
2. Wait for build to complete (~2-3 minutes)
3. Railway will provide a URL like `https://your-app.up.railway.app`

#### Step 7: Run Database Migrations
In Railway terminal:
```bash
cd backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

### Deploy to Render

Render offers a free tier with automatic HTTPS.

#### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

#### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `gemini-chatbot-api`
   - **Region:** Choose closest to your users
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Step 3: Add PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name it `gemini-chatbot-db`
3. Copy the "Internal Database URL"

#### Step 4: Set Environment Variables
In your web service, go to "Environment" and add:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
JWT_SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://...  # From step 3
CORS_ORIGINS=https://your-frontend.vercel.app
PYTHON_VERSION=3.11.0
```

#### Step 5: Deploy
1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Your API will be at `https://your-app.onrender.com`

#### Step 6: Initialize Database
Use Render Shell:
```bash
cd backend
python -c "from database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

### Deploy to Google Cloud Run

For production-grade deployment with auto-scaling.

#### Step 1: Install Google Cloud SDK
```bash
# macOS
brew install google-cloud-sdk

# Windows
# Download from https://cloud.google.com/sdk/docs/install

# Linux
curl https://sdk.cloud.google.com | bash
```

#### Step 2: Initialize and Login
```bash
gcloud init
gcloud auth login
```

#### Step 3: Create Dockerfile
Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### Step 4: Build and Push Container
```bash
cd backend

# Set project ID
export PROJECT_ID=your-gcp-project-id

# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/gemini-chatbot

# Deploy to Cloud Run
gcloud run deploy gemini-chatbot \
  --image gcr.io/$PROJECT_ID/gemini-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key,JWT_SECRET_KEY=your_secret
```

#### Step 5: Set Up Cloud SQL (PostgreSQL)
```bash
# Create Cloud SQL instance
gcloud sql instances create gemini-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create chatbot --instance=gemini-db

# Get connection name
gcloud sql instances describe gemini-db --format="value(connectionName)"
```

#### Step 6: Connect Cloud Run to Cloud SQL
```bash
gcloud run services update gemini-chatbot \
  --add-cloudsql-instances=your-connection-name \
  --set-env-vars DATABASE_URL=postgresql://user:pass@/chatbot?host=/cloudsql/your-connection-name
```

---

## Frontend Deployment

### Deploy to Vercel

Vercel is optimized for Next.js applications.

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Login to Vercel
```bash
vercel login
```

#### Step 3: Deploy from CLI
```bash
cd frontend
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name?** gemini-chatbot
- **Directory?** ./
- **Override settings?** No

#### Step 4: Set Environment Variables
```bash
vercel env add NEXT_PUBLIC_API_URL
# Enter: https://your-backend.railway.app

vercel env add NEXT_PUBLIC_APP_NAME
# Enter: Gemini Chatbot

vercel env add NEXT_PUBLIC_APP_DESCRIPTION
# Enter: AI Chatbot with Memory
```

#### Step 5: Deploy to Production
```bash
vercel --prod
```

Your app will be live at `https://your-project.vercel.app`

#### Alternative: Deploy via Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL` = Your backend URL
6. Click "Deploy"

---

### Deploy to Netlify

Alternative to Vercel with similar features.

#### Step 1: Create netlify.toml
Create `frontend/netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

#### Step 2: Deploy via Netlify CLI
```bash
npm install -g netlify-cli
cd frontend
netlify login
netlify init
netlify deploy --prod
```

#### Step 3: Set Environment Variables
In Netlify dashboard:
1. Go to "Site settings" → "Environment variables"
2. Add:
   - `NEXT_PUBLIC_API_URL` = Your backend URL
   - `NEXT_PUBLIC_APP_NAME` = Gemini Chatbot

---

## Database Setup

### PostgreSQL (Production)

#### Railway PostgreSQL
- Automatically provisioned
- No configuration needed
- Connection string auto-set

#### Render PostgreSQL
1. Create database in Render dashboard
2. Copy "Internal Database URL"
3. Set as `DATABASE_URL` environment variable

#### Cloud SQL (GCP)
```bash
# Create instance
gcloud sql instances create gemini-db \
  --database-version=POSTGRES_14 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create chatbot --instance=gemini-db

# Create user
gcloud sql users create chatbot-user \
  --instance=gemini-db \
  --password=your-secure-password
```

### SQLite (Development Only)
SQLite is included by default for local development. **Do not use in production.**

---

## Environment Variables

### Backend (.env)

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# Optional
GEMINI_MODEL=gemini-2.0-flash-exp
DATABASE_URL=postgresql://user:pass@host:port/dbname
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=https://your-frontend.vercel.app,https://custom-domain.com
MAX_HISTORY_LIMIT=5
NOTIFICATION_POLL_INTERVAL=10
RATE_LIMIT_MAX_RETRIES=3
RATE_LIMIT_BACKOFF_BASE=5

# SMTP (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Gemini Chatbot
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=Gemini Chatbot
NEXT_PUBLIC_APP_DESCRIPTION=AI Chatbot with Memory
```

---

## Post-Deployment

### 1. Verify Backend Health
```bash
curl https://your-backend-url.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "healthy",
  "scheduler": "healthy",
  "gemini": "healthy"
}
```

### 2. Test API Endpoints
```bash
# Test signup
curl -X POST https://your-backend-url.com/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Test1234"}'

# Test chat (with token from signup)
curl -X POST https://your-backend-url.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"user_input":"Hello","session_id":"test"}'
```

### 3. Check Performance Metrics
```bash
curl https://your-backend-url.com/metrics
```

### 4. Monitor Logs

**Railway:**
- Dashboard → Deployments → View Logs

**Render:**
- Dashboard → Logs tab

**Google Cloud Run:**
```bash
gcloud run services logs read gemini-chatbot --limit=50
```

### 5. Set Up Custom Domain

**Vercel:**
1. Go to Project Settings → Domains
2. Add your domain
3. Update DNS records as instructed

**Railway:**
1. Go to Settings → Domains
2. Add custom domain
3. Update DNS: CNAME to `your-app.up.railway.app`

---

## Troubleshooting

### Backend Issues

#### "GEMINI_API_KEY not found"
- Verify environment variable is set in deployment platform
- Check for typos in variable name
- Restart the service after adding variables

#### "JWT_SECRET_KEY must be set"
- Generate a secret: `openssl rand -hex 32`
- Add to environment variables
- Redeploy

#### Database Connection Errors
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- Check database is running
- Verify network connectivity
- For Cloud SQL, ensure Cloud SQL Proxy is configured

#### "Rate limit exceeded"
- Check Gemini API quota
- Verify `RATE_LIMIT_MAX_RETRIES` is set
- Consider upgrading Gemini API plan

### Frontend Issues

#### "Failed to fetch"
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is running
- Check browser console for errors

#### "401 Unauthorized"
- Token may be expired
- Clear localStorage and login again
- Check JWT_ACCESS_TOKEN_EXPIRE_MINUTES

#### Build Failures
- Check Node.js version (requires 18+)
- Clear `.next` folder and rebuild
- Verify all dependencies are installed

### Performance Issues

#### Slow Response Times
1. Check `/metrics` endpoint
2. Review bottlenecks in profiling report
3. Consider:
   - Upgrading database tier
   - Using faster Gemini model
   - Implementing caching
   - Optimizing database queries

#### High Memory Usage
- Check for memory leaks in background tasks
- Implement conversation history cleanup
- Monitor with `/metrics` endpoint

---

## Security Checklist

- [ ] JWT_SECRET_KEY is strong and unique
- [ ] CORS_ORIGINS is set to specific domains (not *)
- [ ] Database credentials are secure
- [ ] HTTPS is enabled (automatic on Railway/Render/Vercel)
- [ ] Rate limiting is enabled
- [ ] Input validation is working
- [ ] Error messages don't expose sensitive info

---

## Monitoring & Maintenance

### Daily
- Check error logs
- Monitor response times via `/metrics`

### Weekly
- Review performance metrics
- Check database size
- Update dependencies if needed

### Monthly
- Rotate JWT secrets
- Review and optimize database
- Update Gemini model if new versions available

---

## Cost Estimates

### Free Tier (Development)
- **Railway:** $5 credit/month (enough for small projects)
- **Render:** Free tier available (sleeps after inactivity)
- **Vercel:** Free for personal projects
- **Gemini API:** Free tier: 15 requests/minute

### Production (Low Traffic)
- **Railway:** ~$10-20/month
- **Render:** ~$7/month (starter plan)
- **Vercel:** Free (Pro at $20/month for teams)
- **Database:** ~$7-15/month
- **Gemini API:** Pay-as-you-go (~$0.10/1K requests)

**Total:** ~$25-50/month for production deployment

---

## Support

- **Documentation:** [README.md](README.md)
- **Issues:** GitHub Issues
- **Gemini API:** [Google AI Studio](https://aistudio.google.com)
- **Railway:** [railway.app/help](https://railway.app/help)
- **Render:** [render.com/docs](https://render.com/docs)

---

**Last Updated:** 2026-05-05  
**Version:** 2.0
