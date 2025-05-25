# 🚀 Sniper Bot Deployment Guide

This guide will walk you through deploying your Sniper Bot webapp to various platforms, with a focus on Netlify.

## 📋 Prerequisites

- Git repository with your code
- GitHub account
- Netlify account (free tier available)

## 🎯 Option 1: Deploy to Netlify (Recommended)

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to Git:**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Verify required files exist:**
   - `requirements.txt` ✅
   - `netlify.toml` ✅
   - `runtime.txt` ✅
   - `src/streamlit_app.py` ✅

### Step 2: Deploy to Netlify

1. **Go to [Netlify](https://netlify.com) and sign in**

2. **Click "New site from Git"**

3. **Connect your GitHub repository:**
   - Choose GitHub as your Git provider
   - Select your sniper_bot repository
   - Choose the main branch

4. **Configure build settings:**
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `.`
   - **Important:** Add these environment variables in Netlify dashboard:
     ```
     PYTHON_VERSION=3.9
     ```

5. **Deploy the site**
   - Click "Deploy site"
   - Wait for the build to complete (5-10 minutes)

### Step 3: Configure Streamlit for Netlify

Since Netlify doesn't natively support Streamlit, we'll use alternative approaches:

#### Option A: Use Streamlit Cloud (Easier)

1. **Go to [Streamlit Cloud](https://streamlit.io/cloud)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Select your repository and specify:**
   - Main file path: `src/streamlit_app.py`
   - Python version: 3.9
5. **Deploy**

#### Option B: Use Heroku (More Control)

1. **Install Heroku CLI**
2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app:**
   ```bash
   heroku create your-sniper-bot-app
   ```

4. **Set buildpacks:**
   ```bash
   heroku buildpacks:set heroku/python
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

## 🔧 Option 2: Deploy to Railway

1. **Go to [Railway](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your repository**
5. **Railway will auto-detect Python and deploy**

## 🐳 Option 3: Deploy with Docker

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deploy to any Docker-compatible platform:

- **Google Cloud Run**
- **AWS ECS**
- **Azure Container Instances**
- **DigitalOcean App Platform**

## 🛠️ Local Testing

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/streamlit_app.py

# Open browser to http://localhost:8501
```

## 🔍 Troubleshooting

### Common Issues:

1. **Build fails due to dependencies:**
   - Remove or comment out `TA-Lib` from requirements.txt
   - Ensure all packages are compatible with Python 3.9

2. **Memory issues:**
   - Consider using lighter ML models
   - Implement lazy loading for large datasets

3. **Timeout issues:**
   - Add progress bars for long-running operations
   - Implement caching with `@st.cache_data`

### Performance Optimization:

1. **Add caching to expensive operations:**
   ```python
   @st.cache_data
   def load_data():
       # Your data loading code
       pass
   ```

2. **Use session state for persistence:**
   ```python
   if 'data' not in st.session_state:
       st.session_state.data = load_data()
   ```

## 🌐 Custom Domain Setup

### For Netlify:
1. Go to Site settings → Domain management
2. Add custom domain
3. Configure DNS records

### For Streamlit Cloud:
1. Custom domains available on paid plans
2. Configure CNAME record pointing to your app

## 📊 Monitoring & Analytics

### Add Google Analytics:
```python
# Add to your Streamlit app
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

## 🔐 Security Considerations

1. **Environment Variables:**
   - Store API keys in platform environment variables
   - Never commit secrets to Git

2. **HTTPS:**
   - All major platforms provide HTTPS by default
   - Ensure all external API calls use HTTPS

3. **Input Validation:**
   - Validate all user inputs
   - Sanitize file uploads

## 📈 Scaling Considerations

1. **Database:**
   - Consider using cloud databases for persistence
   - PostgreSQL, MongoDB Atlas, or Firebase

2. **File Storage:**
   - Use cloud storage for large files
   - AWS S3, Google Cloud Storage, or Cloudinary

3. **Caching:**
   - Implement Redis for session caching
   - Use CDN for static assets

## 🎉 Go Live Checklist

- [ ] Code is tested locally
- [ ] All dependencies are in requirements.txt
- [ ] Environment variables are configured
- [ ] Error handling is implemented
- [ ] Performance is optimized
- [ ] Security measures are in place
- [ ] Monitoring is set up
- [ ] Custom domain is configured (optional)
- [ ] SSL certificate is active
- [ ] Backup strategy is in place

## 📞 Support

If you encounter issues:

1. Check the platform-specific logs
2. Verify all dependencies are compatible
3. Test locally first
4. Check the platform's documentation
5. Consider using a simpler deployment option initially

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone <your-repo>
cd sniper_bot

# Install dependencies
pip install -r requirements.txt

# Test locally
streamlit run src/streamlit_app.py

# Deploy to Streamlit Cloud (easiest)
# Just connect your GitHub repo at streamlit.io/cloud

# Deploy to Heroku
heroku create your-app-name
git push heroku main
```

---

**Happy Deploying! 🎯** 