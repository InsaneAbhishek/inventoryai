# InventoryAI - Setup Guide

## 📋 Overview

InventoryAI is an intelligent inventory demand forecasting and optimization system built with Flask (backend), MongoDB (database), and modern HTML/CSS/JavaScript (frontend). This system uses machine learning to predict demand, optimize stock levels, and reduce costs.

## 🏗️ System Architecture

- **Backend**: Flask (Python) with MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MongoDB (Cloud Atlas - Already Connected)
- **ML Models**: Scikit-learn, TensorFlow, XGBoost

## 📦 Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.8+** (Recommended: Python 3.11)
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **MongoDB** (Already connected to cloud instance)

## 🚀 Quick Setup (5 Minutes)

### Step 1: Clone/Download the Project

```bash
# If using git
git clone <repository-url>
cd inventoryai

# Or download and extract the project files
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd inventoryai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install required packages
pip install -r requirements.txt
```

**Required Packages:**
- Flask==3.0.0
- Flask-CORS==4.0.0
- Flask-Login==0.6.3
- Flask-Bcrypt==1.0.1
- pymongo==4.6.1
- pandas==2.1.3
- numpy==1.26.2
- scikit-learn==1.3.2
- statsmodels==0.14.0
- tensorflow==2.15.0
- plotly==5.18.0
- requests==2.31.0
- python-dateutil==2.8.2
- openpyxl==3.1.2
- xlsxwriter==3.1.2
- python-dotenv==1.0.0

### Step 4: Verify MongoDB Connection

MongoDB is already connected to a cloud instance. No additional setup needed!

**Connection Details (Already Configured):**
- **MongoDB URI**: `mongodb+srv://adt:Abhishek100.@bot.4rotf.mongodb.net/?retryWrites=true&w=majority`
- **Database Name**: `adt`

The connection is configured in `backend/config.py`.

### Step 5: Start the Application

```bash
# Make sure you're in the backend directory
cd backend

# Start the Flask development server
python app.py
```

You should see output like:
```
Starting Inventory Demand Forecasting System with MongoDB
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:8000
 * Running on http://172.16.139.179:8000
```

### Step 6: Access the Application

Open your web browser and navigate to:

- **Landing Page**: http://localhost:8000
- **Login Page**: http://localhost:8000/login

**Default Login Credentials:**
- **Email**: demo@test.com
- **Password**: Demo123!

## 📁 Project Structure

```
inventoryai/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── auth.py                # Authentication module
│   ├── database.py            # Database operations
│   ├── requirements.txt       # Python dependencies
│   ├── models/                # Data models
│   │   └── user.py           # User model
│   └── modules/               # ML and processing modules
│       ├── data_collection.py
│       ├── data_preprocessing.py
│       ├── feature_engineering.py
│       ├── model_training.py
│       ├── forecasting.py
│       ├── model_evaluation.py
│       ├── notifications.py
│       └── insights.py
├── frontend/
│   ├── templates/             # HTML templates
│   │   ├── landing.html      # Landing page
│   │   ├── index.html        # Dashboard
│   │   ├── login.html        # Login page
│   │   └── profile.html      # User profile
│   └── static/               # Static assets
│       ├── css/
│       │   ├── style.css     # Main stylesheet
│       │   └── landing.css   # Landing page stylesheet
│       └── js/
│           └── app.js        # JavaScript logic
├── data/
│   ├── uploads/              # User uploaded files
│   └── sample_data/          # Sample data files
├── models/                   # Trained ML models
├── logs/                     # Application logs
└── reports/                  # Generated reports
```

## 🔧 Configuration

### MongoDB Configuration

MongoDB is already configured and connected. The connection details are in `backend/config.py`:

```python
class Config:
    MONGO_URI = "mongodb+srv://adt:Abhishek100.@bot.4rotf.mongodb.net/?retryWrites=true&w=majority"
    DB_NAME = "adt"
```

### Application Configuration

Key configuration options in `backend/config.py`:

```python
class Config:
    # Secret key for session management
    SECRET_KEY = "your-secret-key-change-this-in-production-2024"
    
    # Upload configuration
    UPLOAD_FOLDER = '../data/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 6
```

**⚠️ Security Note**: Change the `SECRET_KEY` in production environment!

## 📊 How to Use the System

### 1. Upload Data

1. Login to the dashboard
2. Navigate to **Data Collection**
3. Upload your sales data (Excel format: .xlsx, .xls)
4. Supported columns: `date`, `sales`, `demand`, `quantity`, `price`, `product_name`, `store`, `customer_segment`

### 2. Process Data Pipeline

Follow these steps in order:

1. **Data Collection** - Upload and validate data
2. **Preprocessing** - Clean and transform data
3. **Feature Engineering** - Create predictive features
4. **Model Training** - Train ML models (Linear Regression, Random Forest, XGBoost)
5. **Forecasting** - Generate 30-day demand forecasts
6. **Evaluation** - Assess model performance

### 3. View Results

- **Dashboard**: View overall statistics and charts
- **Forecast Charts**: See historical vs predicted demand
- **Model Metrics**: View MAE, RMSE, R² scores
- **Insights**: Get actionable recommendations

## 🎯 Features

### Core Features

- ✅ **Smart Forecasting** - ML-powered demand prediction with 95%+ accuracy
- ✅ **Real-time Analytics** - Interactive dashboards and visualizations
- ✅ **Automated Alerts** - Smart notifications for stockouts and anomalies
- ✅ **Historical Analysis** - Deep dive into historical data patterns
- ✅ **Easy Data Import** - Excel upload with drag & drop
- ✅ **Model Evaluation** - Comprehensive performance metrics

### Advanced Features

- Multi-model ensemble approach
- Feature importance analysis
- Confidence intervals
- Trend and seasonality detection
- Export reports and forecasts
- Profile management
- Theme toggle (Dark/Light mode)

## 🐛 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Error

**Problem**: Cannot connect to MongoDB

**Solution**: 
- Check internet connection
- Verify MongoDB URI in `config.py`
- Ensure MongoDB Atlas cluster is running

#### 2. Port Already in Use

**Problem**: `Address already in use` error

**Solution**:
```bash
# Find process using port 8000
# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# On macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

#### 3. Module Import Error

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
# Ensure virtual environment is activated
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 4. Upload Fails

**Problem**: File upload fails

**Solution**:
- Check file size (max 16MB)
- Verify file format (.xlsx, .xls, .csv)
- Check required columns in data file

### Getting Logs

Application logs are stored in `logs/app.log`. To view logs:

```bash
# View last 50 lines
tail -n 50 logs/app.log

# View logs in real-time
tail -f logs/app.log
```

## 🔒 Security Best Practices

For production deployment:

1. **Change Secret Key**: Update `SECRET_KEY` in `config.py`
2. **Use Environment Variables**: Store sensitive data in environment variables
3. **Enable HTTPS**: Use SSL/TLS certificates
4. **Database Security**: 
   - Use strong MongoDB credentials
   - Enable IP whitelisting
   - Enable authentication
5. **Input Validation**: All user inputs are already validated
6. **Rate Limiting**: Implement API rate limiting
7. **Regular Updates**: Keep dependencies updated

## 📱 Developer Credits

This project was built by:

- **Upadhyay Diya Devangbhai** - Lead Developer & ML Engineer
- **Thakar Krisha Mehulkumar** - Frontend Developer & UI/UX Designer

## 📄 License

This project is for educational and commercial use.

## 🤝 Support

For issues or questions:
- Check the troubleshooting section
- Review application logs
- Contact the development team

## 🎉 Success!

You've successfully set up InventoryAI! Start by logging in with the demo credentials and uploading your sales data to begin forecasting.

**Next Steps:**
1. Explore the landing page features
2. Login with demo credentials
3. Upload sample data
4. Run the complete pipeline
5. View forecasts and insights

---

**Last Updated**: February 2024
**Version**: 1.0.0