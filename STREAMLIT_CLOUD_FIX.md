# 🔧 Streamlit Cloud Deployment Fix

## ✅ Problem Solved!

The error you encountered:
```
ImportError: libGL.so.1: cannot open shared object file: No such file or directory
```

This happened because **OpenCV requires system libraries** that aren't installed by default on Streamlit Cloud.

## 🎯 Solution Applied

I've added the necessary files to fix this:

### 1. `packages.txt` ✅
```
libgl1-mesa-glx
libglib2.0-0
```

This tells Streamlit Cloud to install the system libraries OpenCV needs.

### 2. `.streamlit/config.toml` ✅
```toml
[server]
headless = true
enableCORS = false
maxUploadSize = 200
```

This configures Streamlit for cloud deployment.

### 3. Changes Pushed to GitHub ✅
All files have been committed and pushed to your repository.

---

## 🚀 Next Steps

### Option 1: Reboot Your Streamlit App (Recommended)

1. Go to your Streamlit Cloud dashboard: https://share.streamlit.io/
2. Find your app: `deepfake-shield-for-journalism`
3. Click the **"⋮" menu** (three dots)
4. Select **"Reboot app"**
5. Wait 2-3 minutes for redeployment

### Option 2: Redeploy from Scratch

If rebooting doesn't work:

1. Go to https://share.streamlit.io/
2. Delete the existing app
3. Click **"New app"**
4. Configure:
   - Repository: `janhavitupe/Deepfake-Shield-for-Journalism`
   - Branch: `main`
   - Main file: `dashboard.py`
5. Click **"Deploy"**

---

## 📋 What Streamlit Cloud Will Do

When you reboot/redeploy, Streamlit Cloud will:

1. ✅ Pull latest code from GitHub (including `packages.txt`)
2. ✅ Install system packages from `packages.txt`:
   - `libgl1-mesa-glx` (OpenGL library for OpenCV)
   - `libglib2.0-0` (GLib library for OpenCV)
3. ✅ Install Python packages from `requirements.txt`
4. ✅ Start your Streamlit app

---

## 🎉 Expected Result

After reboot, you should see:

```
[16:XX:XX] 📦 Processing dependencies...
[16:XX:XX] 📦 Installing system packages from packages.txt...
[16:XX:XX] ✅ Installed libgl1-mesa-glx
[16:XX:XX] ✅ Installed libglib2.0-0
[16:XX:XX] 📦 Installing Python packages...
[16:XX:XX] ✅ All dependencies installed!
[16:XX:XX] 🎈 Your app is live!
```

Your app will be accessible at:
```
https://deepfake-shield-for-journalism-[random-id].streamlit.app
```

---

## ⚠️ Important Notes

### Model File Warning

Your app might encounter another issue: **Missing model file**

The `dfdc/deepfake_shield_model.pkl` file is excluded by `.gitignore` because it's too large for Git.

**Solutions:**

#### Option A: Use Git LFS (Recommended)
```bash
# Install Git LFS
git lfs install

# Track the model file
git lfs track "*.pkl"

# Add and commit
git add .gitattributes
git add dfdc/deepfake_shield_model.pkl
git commit -m "Add model file with Git LFS"
git push origin main
```

#### Option B: Download Model on Startup

Update `dashboard.py` to download the model if it doesn't exist:

```python
@st.cache_resource
def load_model():
    model_path = Path("dfdc/deepfake_shield_model.pkl")
    
    if not model_path.exists():
        st.warning("Model not found. Training model...")
        # Train model or download from cloud storage
        # For now, return None and show warning
        return None
    
    return joblib.load(model_path)
```

#### Option C: Use Cloud Storage

Upload model to:
- Google Drive
- Dropbox
- AWS S3
- Hugging Face Hub

Then download it in the app on startup.

---

## 🐛 Troubleshooting

### If OpenCV Error Persists

1. **Check packages.txt is in root directory**
   ```
   Deepfake-Shield-for-Journalism/
   ├── packages.txt  ← Must be here
   ├── dashboard.py
   └── requirements.txt
   ```

2. **Verify packages.txt content**
   ```
   libgl1-mesa-glx
   libglib2.0-0
   ```
   (No extra spaces or characters)

3. **Check Streamlit Cloud logs**
   - Look for "Installing system packages from packages.txt"
   - If not found, packages.txt wasn't detected

### If Model Not Found Error

```
⚠️ Model not found. Please train the model first.
```

**Solution**: Follow Option A, B, or C above to include the model file.

### If Out of Memory Error

```
MemoryError: Unable to allocate array
```

**Causes:**
- Streamlit Cloud free tier: 1 GB RAM limit
- Large model file
- Processing large videos

**Solutions:**
1. Reduce model size
2. Process smaller videos
3. Upgrade to Streamlit Cloud paid tier
4. Use alternative platform (Hugging Face, Railway)

### If App Keeps Sleeping

```
😴 This app has gone to sleep due to inactivity
```

**Normal behavior for free tier:**
- Apps sleep after 7 days of inactivity
- Wake up automatically when visited
- Takes 30-60 seconds to wake

**Solution**: Upgrade to paid tier for always-on apps

---

## 📊 Deployment Checklist

Before deploying, ensure:

- ✅ `packages.txt` exists in root directory
- ✅ `requirements.txt` has all dependencies
- ✅ `.streamlit/config.toml` exists
- ✅ Model file is accessible (Git LFS or download)
- ✅ No large video files in repo (use .gitignore)
- ✅ All changes committed and pushed to GitHub

---

## 🎯 Quick Commands

### Check what's in your repo:
```bash
git ls-files
```

### Verify packages.txt is tracked:
```bash
git ls-files | grep packages.txt
```

### Force push if needed:
```bash
git push origin main --force
```

### Check file sizes:
```bash
du -sh dfdc/deepfake_shield_model.pkl
```

---

## 📞 Still Having Issues?

### Check Streamlit Cloud Status
- https://status.streamlit.io/

### Review Logs
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. Click "Manage app"
4. View "Logs" tab
5. Look for error messages

### Common Log Messages

**Success:**
```
✅ Installed libgl1-mesa-glx
✅ Installed libglib2.0-0
🎈 Your app is live!
```

**Failure:**
```
❌ ImportError: libGL.so.1
❌ FileNotFoundError: dfdc/deepfake_shield_model.pkl
❌ MemoryError
```

---

## 🎉 Success Indicators

Your app is working when you see:

1. ✅ No import errors in logs
2. ✅ Dashboard loads with three pages
3. ✅ Model performance metrics display
4. ✅ Video upload works
5. ✅ Classification produces results

---

## 📚 Additional Resources

- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **OpenCV on Streamlit**: https://docs.streamlit.io/knowledge-base/dependencies/libgl
- **Git LFS Guide**: https://git-lfs.github.com/
- **Deployment Guide**: See `DEPLOYMENT_GUIDE.md` in your repo

---

**Last Updated**: February 17, 2026  
**Status**: ✅ Fix applied and pushed to GitHub  
**Action Required**: Reboot your Streamlit Cloud app

---

*The fix has been applied. Simply reboot your app on Streamlit Cloud and it should work!* 🚀
