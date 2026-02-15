"""
Configuration for Inventory Demand Forecasting System
"""

import os
from datetime import timedelta

class Config:
    # MongoDB Configuration
    MONGO_URI = "mongodb+srv://adt:Abhishek100.@bot.4rotf.mongodb.net/?retryWrites=true&w=majority"
    DB_NAME = "adt"
    
    # Secret key for session management
    SECRET_KEY = "your-secret-key-change-this-in-production-2024"
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload configuration
    UPLOAD_FOLDER = '../data/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Password requirements
    MIN_PASSWORD_LENGTH = 6
    
    # Pagination
    ITEMS_PER_PAGE = 20