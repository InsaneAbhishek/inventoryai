"""
Database connection and models for Inventory Demand Forecasting System
"""

from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database connection and operations"""
    
    def __init__(self, mongo_uri, db_name):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.bcrypt = Bcrypt()
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            
            # Create indexes
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create database indexes"""
        try:
            # Users collection indexes
            self.db.users.create_index("email", unique=True)
            self.db.users.create_index("username", unique=True)
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning: {str(e)}")
    
    # User Operations
    def create_user(self, username, email, password, full_name=None):
        """
        Create a new user
        
        Args:
            username: Unique username
            email: User email address
            password: Plain text password (will be hashed)
            full_name: User's full name (optional)
            
        Returns:
            dict: Created user document or None if failed
        """
        try:
            # Hash password
            hashed_password = self.bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Create user document
            user = {
                'username': username,
                'email': email.lower(),
                'password': hashed_password,
                'full_name': full_name or username,
                'created_at': datetime.utcnow(),
                'last_login': None,
                'is_active': True,
                'profile': {
                    'company': '',
                    'phone': '',
                    'role': 'user'
                }
            }
            
            # Insert user
            result = self.db.users.insert_one(user)
            user['_id'] = result.inserted_id
            
            logger.info(f"User created successfully: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            if 'duplicate key error' in str(e).lower():
                return None  # User already exists
            raise
    
    def find_user_by_email(self, email):
        """Find user by email"""
        try:
            return self.db.users.find_one({'email': email.lower()})
        except Exception as e:
            logger.error(f"Error finding user by email: {str(e)}")
            return None
    
    def find_user_by_username(self, username):
        """Find user by username"""
        try:
            return self.db.users.find_one({'username': username})
        except Exception as e:
            logger.error(f"Error finding user by username: {str(e)}")
            return None
    
    def find_user_by_id(self, user_id):
        """Find user by ID"""
        try:
            from bson import ObjectId
            return self.db.users.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            logger.error(f"Error finding user by ID: {str(e)}")
            return None
    
    def verify_password(self, user, password):
        """Verify user password"""
        try:
            return self.bcrypt.check_password_hash(user['password'], password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        try:
            from bson import ObjectId
            self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login': datetime.utcnow()}}
            )
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
    
    def update_password(self, user_id, new_password):
        """Update user password"""
        try:
            from bson import ObjectId
            hashed_password = self.bcrypt.generate_password_hash(new_password).decode('utf-8')
            result = self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password': hashed_password}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating password: {str(e)}")
            return False
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile"""
        try:
            from bson import ObjectId
            self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'profile': profile_data}}
            )
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    # Data Operations
    def save_user_data(self, user_id, data_type, data):
        """
        Save user's processed data
        
        Args:
            user_id: User ID
            data_type: Type of data (raw, preprocessed, features, forecast, etc.)
            data: Data to save
            
        Returns:
            bool: Success status
        """
        try:
            from bson import ObjectId
            
            document = {
                'user_id': ObjectId(user_id),
                'data_type': data_type,
                'data': data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Upsert document
            self.db.user_data.update_one(
                {
                    'user_id': ObjectId(user_id),
                    'data_type': data_type
                },
                {'$set': document},
                upsert=True
            )
            
            logger.info(f"Data saved for user {user_id}: {data_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user data: {str(e)}")
            return False
    
    def get_user_data(self, user_id, data_type):
        """Get user's data by type"""
        try:
            from bson import ObjectId
            doc = self.db.user_data.find_one({
                'user_id': ObjectId(user_id),
                'data_type': data_type
            })
            return doc['data'] if doc else None
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
    
    def save_model(self, user_id, model_name, model_data, metrics):
        """Save trained model information"""
        try:
            from bson import ObjectId
            
            document = {
                'user_id': ObjectId(user_id),
                'model_name': model_name,
                'model_data': model_data,
                'metrics': metrics,
                'created_at': datetime.utcnow()
            }
            
            self.db.models.insert_one(document)
            logger.info(f"Model saved: {model_name} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return False
    
    def get_user_models(self, user_id):
        """Get all models for a user"""
        try:
            from bson import ObjectId
            models = self.db.models.find({'user_id': ObjectId(user_id)})
            return list(models)
        except Exception as e:
            logger.error(f"Error getting user models: {str(e)}")
            return []
    
    def save_alert_config(self, user_id, config):
        """Save user's alert configuration"""
        try:
            from bson import ObjectId
            
            document = {
                'user_id': ObjectId(user_id),
                'config': config,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            self.db.alert_config.update_one(
                {'user_id': ObjectId(user_id)},
                {'$set': document},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving alert config: {str(e)}")
            return False
    
    def get_alert_config(self, user_id):
        """Get user's alert configuration"""
        try:
            from bson import ObjectId
            doc = self.db.alert_config.find_one({'user_id': ObjectId(user_id)})
            return doc['config'] if doc else None
        except Exception as e:
            logger.error(f"Error getting alert config: {str(e)}")
            return None
    
    def save_alert(self, user_id, alert_data):
        """Save an alert record"""
        try:
            from bson import ObjectId
            
            document = {
                'user_id': ObjectId(user_id),
                'alert': alert_data,
                'created_at': datetime.utcnow()
            }
            
            self.db.alerts.insert_one(document)
            return True
        except Exception as e:
            logger.error(f"Error saving alert: {str(e)}")
            return False
    
    def get_user_alerts(self, user_id, limit=20):
        """Get recent alerts for a user"""
        try:
            from bson import ObjectId
            alerts = self.db.alerts.find(
                {'user_id': ObjectId(user_id)}
            ).sort('created_at', -1).limit(limit)
            return list(alerts)
        except Exception as e:
            logger.error(f"Error getting user alerts: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")