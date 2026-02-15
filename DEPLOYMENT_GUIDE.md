# InventoryAI Deployment Guide - Render (Free Hosting)

This guide will help you deploy your InventoryAI application to **Render** for free.

---

## 🚀 Why Render?

- ✅ **100% Free** - No credit card required
- ✅ **750 hours/month** - More than enough for personal projects
- ✅ **Automatic SSL** - HTTPS enabled by default
- ✅ **GitHub Integration** - Easy deployment from your repository
- ✅ **Global CDN** - Fast worldwide access
- ✅ **MongoDB Compatible** - Works perfectly with MongoDB Atlas

---

## 📋 Prerequisites

Before deploying, make sure you have:

1. **GitHub Account** - [Sign up free](https://github.com/signup)
2. **Render Account** - [Sign up free](https://render.com/register)
3. **MongoDB Atlas Account** - Already configured in your project
4. **Project Files** - All files from your workspace

---

## 🛠️ Step-by-Step Deployment

### Step 1: Prepare Your Code

All deployment files are already created in your workspace:

- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Render deployment configuration
- ✅ `.render.yaml` - Render service configuration
- ✅ `.env.example` - Environment variable template
- ✅ `.gitignore` - Files to exclude from Git

---

### Step 2: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and log in
2. Click the **+** button in the top-right corner
3. Select **New repository**
4. Repository name: `inventoryai` (or any name you prefer)
5. Description: `Intelligent Inventory Demand Forecasting System`
6. Make it **Public** (recommended)
7. Click **Create repository**

---

### Step 3: Upload Your Code

You have two options to upload your code:

#### Option A: Using GitHub Web Interface (Easier)

1. Go to your new repository on GitHub
2. Click **uploading an existing file**
3. Drag and drop all files from `/workspace` (excluding `.git` folder if exists)
4. Add a commit message: `Initial commit - InventoryAI application`
5. Click **Commit changes**

#### Option B: Using Git Command Line

```bash
# Initialize Git repository
cd /workspace
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - InventoryAI application"

# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/inventoryai.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

### Step 4: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **Sign Up**
3. Sign up with your **GitHub account** (recommended) or email
4. Verify your email if required

---

### Step 5: Connect Render to GitHub

1. Log in to Render
2. Click **New +** button in the top-right
3. Select **Web Service**
4. Click **Connect GitHub** if prompted
5. Authorize Render to access your GitHub account
6. Search for your `inventoryai` repository
7. Click **Connect**

---

### Step 6: Configure Deployment

Render will automatically detect your configuration from `.render.yaml`. Review these settings:

**Basic Settings:**
- **Name**: `inventoryai` (auto-detected)
- **Region**: Choose a region close to you
- **Branch**: `main` (or `master`)
- **Runtime**: Python (auto-detected)

**Build & Start:**
- **Build Command**: `pip install -r requirements.txt` (auto-detected)
- **Start Command**: `gunicorn backend.app:app` (auto-detected)

---

### Step 7: Set Environment Variables

1. Scroll down to **Environment Variables** section
2. Add the following variables:

#### Variable 1: MONGO_URI
- **Key**: `MONGO_URI`
- **Value**: Your MongoDB connection string
  ```
  mongodb+srv://adt:Abhishek100.@bot.4rotf.mongodb.net/inventoryai
  ```

#### Variable 2: SECRET_KEY
- **Key**: `SECRET_KEY`
- **Value**: Generate a secure secret key:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  Copy the output and paste it here.

#### Variable 3: FLASK_ENV
- **Key**: `FLASK_ENV`
- **Value**: `production`

3. Click **Save** after adding all variables

---

### Step 8: Deploy

1. Click **Create Web Service** at the bottom
2. Render will start deploying your application
3. Wait for the deployment to complete (typically 2-5 minutes)
4. You'll see a live URL like: `https://inventoryai.onrender.com`

---

### Step 9: Access Your Application

Once deployment is complete:

1. Click on your service name in Render
2. Copy the **URL** from the top of the page
3. Open it in your browser
4. You should see the landing page!

**Example URL:** `https://inventoryai.onrender.com`

---

## 🧪 Testing Your Deployed Application

### Test Basic Functionality

1. **Landing Page**
   - Navigate to your URL
   - Verify the landing page loads correctly
   - Check animations and design

2. **Login**
   - Click "Login"
   - Use demo credentials:
     - Email: `demo@test.com`
     - Password: `Demo123!`

3. **Dashboard**
   - After login, verify dashboard loads
   - Check all navigation links work

4. **Data Upload**
   - Navigate to "Data Collection"
   - Upload `demo_sales_data.xlsx` (download from your local workspace)
   - Verify success message appears

5. **Forecasting**
   - Run through the pipeline:
     - Preprocessing → Feature Engineering → Model Training → Forecasting
   - Verify charts display correctly

---

## 📊 Monitoring Your Deployment

Render provides built-in monitoring:

### View Logs
1. Go to your service in Render
2. Click **Logs** tab
3. View real-time application logs
4. Check for any errors or warnings

### View Metrics
1. Click **Metrics** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Response times
   - Request counts

---

## 🔧 Troubleshooting

### Issue 1: Deployment Fails

**Check:**
- Review the **Logs** tab for error messages
- Verify `requirements.txt` is correct
- Ensure `Procfile` exists and is correct
- Check that `backend/app.py` exists

**Common Solutions:**
- Missing dependencies in `requirements.txt`
- Incorrect `Procfile` format
- Missing environment variables

---

### Issue 2: Application Returns 500 Error

**Check:**
- Verify `MONGO_URI` is correct
- Verify MongoDB Atlas allows connections from anywhere (whitelist `0.0.0.0/0`)
- Check logs for specific error messages

**Solution:**
- Ensure MongoDB Atlas network access is configured
- Verify SECRET_KEY is set correctly

---

### Issue 3: Static Files Not Loading

**Check:**
- Verify folder structure matches expected paths
- Check if `frontend/static` folder is pushed to GitHub

**Solution:**
- Ensure all static files are committed to Git
- Verify paths in Flask app are correct

---

### Issue 4: Database Connection Failed

**Check:**
- MongoDB Atlas credentials are correct
- MongoDB Atlas allows connections from Render's IP
- Network access is configured

**Solution:**
- Go to MongoDB Atlas → Network Access
- Add IP: `0.0.0.0/0` (allows all IPs)
- Or add Render's specific IP ranges

---

## 🔄 Updating Your Application

### Make Changes Locally

1. Edit files in `/workspace`
2. Test locally

### Push to GitHub

```bash
git add .
git commit -m "Your commit message"
git push
```

### Render Auto-Deploys

Render will automatically detect changes and redeploy!

---

## 💡 Best Practices

1. **Always test locally before deploying**
2. **Use meaningful commit messages**
3. **Monitor logs regularly**
4. **Keep dependencies updated**
5. **Use environment variables for sensitive data**
6. **Enable MongoDB Atlas backups**
7. **Set up alerts for downtime**

---

## 📈 Scaling Beyond Free Tier

Render's free tier includes:
- ✅ 750 hours/month
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ 10GB bandwidth

When you need more:
- **Standard Plan**: $7/month
  - More RAM and CPU
  - Faster deployments
  - Priority support

---

## 🎉 Congratulations!

You've successfully deployed InventoryAI to Render! 

Your application is now:
- ✅ Live on the internet
- ✅ Accessible from anywhere
- ✅ Running on a free hosting platform
- ✅ Connected to MongoDB Atlas
- ✅ SSL/HTTPS enabled

---

## 📞 Need Help?

### Render Documentation
- [Deploy Flask Guide](https://render.com/docs/deploy-flask)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Troubleshooting](https://render.com/docs/troubleshooting)

### MongoDB Atlas Documentation
- [Network Access](https://www.mongodb.com/docs/atlas/security/ip-access-list/)
- [Connection Strings](https://www.mongodb.com/docs/manual/reference/connection-string/)

---

## 📝 Summary

✅ **Deployment Platform**: Render (Free)
✅ **Application URL**: `https://inventoryai.onrender.com` (or your custom name)
✅ **MongoDB**: Atlas (cloud)
✅ **SSL**: Automatic
✅ **Monitoring**: Built-in
✅ **Auto-deploy**: Enabled

Your InventoryAI application is now live and ready to use!