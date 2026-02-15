"""
User model for Flask-Login authentication
"""

from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.full_name = user_data.get('full_name', user_data['username'])
        self._is_active = user_data.get('is_active', True)
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
        self.profile = user_data.get('profile', {})
    
    @property
    def is_active(self):
        """Return if user is active"""
        return self._is_active
    
    @staticmethod
    def from_db(user_data):
        """Create User instance from database document"""
        if user_data:
            return User(user_data)
        return None
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return self.id
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self._is_active,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'profile': self.profile
        }