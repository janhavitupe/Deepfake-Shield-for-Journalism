# 🚀 DeepFake Shield - Deployment Guide

## ❌ Why Vercel Doesn't Work

Vercel shows "404: NOT_FOUND" because:
- Vercel is for **static sites** and **serverless functions**
- Streamlit is a **long-running Python web server**
- Streamlit requires **WebSocket connections**
- No compatible entry point for Vercel

**Solution**: Use a platform designed for Python web apps!

---

## ✅ Recommended: Streamlit Cloud (FREE)

### Best option for Streamlit apps!

**Steps:**

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Deploy Your App**
   - Click "New app"
   - Repository: `janhavitupe/Deepfake-Shield-for-Journalism`
   - Branch: `main`
   - Main file path: `dashboard.py`
   - Click "Deploy"

3. **Wait for Deployment** (2-5 minutes)
   - Streamlit will install dependencies
   - Your app will be live at: `https://[your-app-name].streamlit.app`

**Pros:**
- ✅ **FREE** for public repositories
- ✅ Designed specifically for Streamlit
- ✅ Auto-deploys on git push
- ✅ No configuration needed
- ✅ Built-in SSL/HTTPS
- ✅ Easy to manage

**Cons:**
- ⚠️ Limited resources (1 GB RAM)
- ⚠️ Apps sleep after inactivity
- ⚠️ Public repos only for free tier

---

## 🤗 Alternative: Hugging Face Spaces (FREE)

### Great for ML/AI applications!

**Steps:**

1. **Create Space**
   - Go to: https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `deepfake-shield`
   - License: Choose appropriate
   - SDK: Select **Streamlit**

2. **Upload Files**
   - Upload all project files
   - Or connect your GitHub repo

3. **Configure**
   - Hugging Face will auto-detect `requirements.txt`
   - App will be live at: `https://huggingface.co/spaces/[username]/deepfake-shield`

**Pros:**
- ✅ **FREE** hosting
- ✅ Good for ML/AI apps
- ✅ Generous resources
- ✅ Community visibility

---

## 🚂 Alternative: Railway (FREE Tier)

### Modern deployment platform

**Steps:**

1. **Create Account**
   - Go to: https://railway.app/
   - Sign up with GitHub

2. **Create Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose: `janhavitupe/Deepfake-Shield-for-Journalism`

3. **Configure**
   - Railway auto-detects Python
   - Add start command: `streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0`

4. **Deploy**
   - Railway will build and deploy
   - Get your URL from dashboard

**Configuration File** (optional - `railway.json`):
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Pros:**
- ✅ Free tier available ($5 credit/month)
- ✅ Easy deployment
- ✅ Good performance
- ✅ Custom domains

**Cons:**
- ⚠️ Limited free tier
- ⚠️ Requires credit card after trial

---

## 🎨 Alternative: Render (FREE Tier)

### Simple cloud platform

**Steps:**

1. **Create Account**
   - Go to: https://render.com/
   - Sign up with GitHub

2. **New Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect GitHub repo

3. **Configure**
   - Name: `deepfake-shield`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment

**Configuration File** (optional - `render.yaml`):
```yaml
services:
  - type: web
    name: deepfake-shield
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0
    plan: free
```

**Pros:**
- ✅ Free tier available
- ✅ Easy setup
- ✅ Auto-deploy on push

**Cons:**
- ⚠️ Free tier spins down after inactivity
- ⚠️ Slower cold starts

---

## 💰 Alternative: Heroku (PAID)

### Traditional PaaS platform

**Note**: Heroku no longer has a free tier (as of Nov 2022)

**Steps:**

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login**
   ```bash
   heroku login
   ```

3. **Create App**
   ```bash
   heroku create deepfake-shield
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

**Required Files:**

**`Procfile`:**
```
web: streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0
```

**`setup.sh`:**
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

**Pros:**
- ✅ Reliable platform
- ✅ Good documentation
- ✅ Scalable

**Cons:**
- ❌ No free tier
- ❌ Minimum $7/month

---

## 🐳 Alternative: Docker + Any Cloud

### Most flexible option

**Create `Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Deploy to:**
- Google Cloud Run
- AWS ECS
- Azure Container Instances
- DigitalOcean App Platform

---

## 📊 Comparison Table

| Platform | Cost | Ease | Performance | Best For |
|----------|------|------|-------------|----------|
| **Streamlit Cloud** | FREE | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Quick demos, public apps |
| **Hugging Face** | FREE | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ML/AI apps, community |
| **Railway** | FREE tier | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Modern apps, good UX |
| **Render** | FREE tier | ⭐⭐⭐⭐ | ⭐⭐⭐ | Simple deployment |
| **Heroku** | $7+/mo | ⭐⭐⭐ | ⭐⭐⭐⭐ | Production apps |
| **Docker** | Varies | ⭐⭐ | ⭐⭐⭐⭐⭐ | Full control |

---

## 🎯 Recommended Approach

### For Your Use Case:

**1. Start with Streamlit Cloud** (Easiest)
- Perfect for demos and testing
- Free and fast deployment
- No configuration needed

**2. If you need more resources → Hugging Face Spaces**
- Better for ML apps
- More generous limits
- Good community

**3. For production → Railway or Render**
- More reliable
- Better performance
- Worth the cost

---

## ⚠️ Important Notes

### Model File Size
Your `deepfake_shield_model.pkl` might be too large for some platforms:
- **Streamlit Cloud**: 1 GB limit
- **Hugging Face**: 10 GB limit
- **Railway**: Generous limits

**Solution if too large:**
1. Use Git LFS for large files
2. Download model on startup
3. Use cloud storage (S3, GCS)

### Video Files
The `dfdc/raw_tmp/*.mp4` files are excluded by `.gitignore`:
- Good: Keeps repo size small
- Note: Example videos won't be in deployment
- Solution: Upload videos separately or use cloud storage

### Dependencies
Some platforms may have issues with OpenCV:
- **Solution**: Use `packages.txt` (already created)
- Contains system dependencies for OpenCV

---

## 🚀 Quick Start: Streamlit Cloud

**Fastest way to deploy:**

1. **Commit new files:**
   ```bash
   git add .streamlit/config.toml packages.txt
   git commit -m "Add Streamlit Cloud configuration"
   git push origin main
   ```

2. **Deploy:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repo
   - Click "Deploy"

3. **Done!**
   - Your app will be live in 2-5 minutes
   - Share the URL with anyone

---

## 🐛 Troubleshooting

### "Module not found" errors
- Check `requirements.txt` has all dependencies
- Ensure versions are compatible

### "Out of memory" errors
- Reduce model size
- Use smaller dataset
- Upgrade to paid tier

### "App is sleeping" message
- Normal for free tiers
- App wakes up on first visit
- Consider paid tier for always-on

### OpenCV errors
- Ensure `packages.txt` is present
- Check system dependencies are installed

---

## 📞 Support

If you encounter issues:
1. Check platform-specific documentation
2. Review deployment logs
3. Test locally first: `streamlit run dashboard.py`
4. Check GitHub Issues for similar problems

---

## 🎉 Success!

Once deployed, your app will be accessible at:
- **Streamlit Cloud**: `https://[app-name].streamlit.app`
- **Hugging Face**: `https://huggingface.co/spaces/[username]/[space-name]`
- **Railway**: `https://[app-name].up.railway.app`
- **Render**: `https://[app-name].onrender.com`

Share the link and start detecting deepfakes! 🛡️

---

**Last Updated**: February 17, 2026  
**Recommended**: Streamlit Cloud for easiest deployment
