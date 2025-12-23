# 🚀 Production Deployment Guide

## Overview
This guide covers deploying:
- **Frontend (React)** → Vercel
- **Backend (Flask)** → Render (free tier available)

---

## 📋 STEP 1: Prepare Your Code

### 1.1 Update Environment Variables

**Frontend (.env in chatbot-ui folder):**
```env
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_live_your-key
REACT_APP_API_URL=https://your-backend.onrender.com
```

**Backend (.env in root folder):**
```env
FLASK_ENV=production
FLASK_DEBUG=0
FRONTEND_URLS=https://your-app.vercel.app
GROQ_API_KEY=your-groq-api-key
CRYPTOPANIC_API_KEY=your-cryptopanic-key
BREVO_API_KEY=your-brevo-key
```

### 1.2 Push to GitHub
```bash
git add .
git commit -m "Production ready"
git push origin main
```

---

## 📋 STEP 2: Deploy Backend to Render

### 2.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### 2.2 Create New Web Service
1. Click **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name:** crypto-chatbot-api
   - **Root Directory:** (leave empty - uses root)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn flask_server:app --bind 0.0.0.0:$PORT`

### 2.3 Add Environment Variables
In Render dashboard → Environment tab, add:
```
FLASK_ENV=production
FRONTEND_URLS=https://your-vercel-app.vercel.app
GROQ_API_KEY=your-groq-key
CRYPTOPANIC_API_KEY=your-key
BREVO_API_KEY=your-key
```

### 2.4 Deploy
Click **Create Web Service** - Render will build and deploy.
Note your backend URL: `https://crypto-chatbot-api.onrender.com`

---

## 📋 STEP 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### 3.2 Import Project
1. Click **Add New** → **Project**
2. Select your GitHub repository
3. Configure:
   - **Framework Preset:** Create React App
   - **Root Directory:** `chatbot-ui`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

### 3.3 Add Environment Variables
In Vercel dashboard → Settings → Environment Variables, add:
```
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
REACT_APP_CLERK_PUBLISHABLE_KEY=pk_live_your-key
REACT_APP_API_URL=https://crypto-chatbot-api.onrender.com
```

### 3.4 Deploy
Click **Deploy** - Vercel will build and deploy.
Your app URL: `https://your-app.vercel.app`

---

## 📋 STEP 4: Update CORS in Backend

After getting your Vercel URL, update the `FRONTEND_URLS` in Render:
```
FRONTEND_URLS=https://your-app.vercel.app,https://your-custom-domain.com
```

---

## 📋 STEP 5: Supabase Production Setup

### 5.1 Run Database Schema
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. SQL Editor → New Query
3. Paste contents of `supabase_schema.sql`
4. Run

### 5.2 Configure Authentication
1. Go to Authentication → URL Configuration
2. Add your Vercel URL to **Redirect URLs**

---

## 📋 STEP 6: Clerk Production Setup

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Create production instance
3. Update allowed origins with your Vercel URL
4. Copy production publishable key

---

## ✅ Final Checklist

- [ ] Backend deployed to Render
- [ ] Backend URL noted
- [ ] Frontend deployed to Vercel
- [ ] Environment variables set in both platforms
- [ ] CORS configured with Vercel URL
- [ ] Supabase tables created
- [ ] Clerk production keys configured
- [ ] Test login/chat functionality
- [ ] Test news/trending features
- [ ] Test newsletter subscription

---

## 🔧 Troubleshooting

### CORS Errors
- Ensure `FRONTEND_URLS` in Render includes your Vercel domain
- Include both `https://` and non-www versions

### API Connection Issues
- Check `REACT_APP_API_URL` is set correctly in Vercel
- Ensure backend is running (check Render logs)

### Supabase Issues
- Verify `REACT_APP_SUPABASE_URL` and `REACT_APP_SUPABASE_ANON_KEY` are correct
- Check RLS policies allow your operations

### Clerk Auth Issues
- Verify production publishable key is used
- Check allowed origins in Clerk dashboard

---

## 📁 Files Created for Deployment

| File | Purpose |
|------|---------|
| `chatbot-ui/vercel.json` | Vercel configuration |
| `chatbot-ui/src/config/api.js` | Centralized API endpoints |
| `chatbot-ui/.env.example` | Frontend env template |
| `Procfile` | Render/Heroku start command |
| `requirements.txt` | Python dependencies |
| `.env.example` | Backend env template |

---

## 🌐 Your URLs After Deployment

| Service | URL |
|---------|-----|
| Frontend | `https://your-app.vercel.app` |
| Backend | `https://your-backend.onrender.com` |
| Supabase | `https://your-project.supabase.co` |
