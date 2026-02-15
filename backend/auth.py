"""
Authentication routes for user registration and login
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from config import Config
from database import Database
from models.user import User
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def get_db():
    """Get database instance"""
    # Import app to get the shared database instance
    import app as flask_app
    return flask_app.db

@auth_bp.route('/')
def index():
    """Landing page"""
    return render_template('landing.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            full_name = data.get('full_name', '').strip() or username
            confirm_password = data.get('confirm_password', '')
            
            # Validation
            if not username or not email or not password:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'All fields are required'}), 400
                flash('All fields are required', 'error')
                return render_template('register.html')
            
            if password != confirm_password:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Passwords do not match'}), 400
                flash('Passwords do not match', 'error')
                return render_template('register.html')
            
            if len(password) < 6:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
                flash('Password must be at least 6 characters', 'error')
                return render_template('register.html')
            
            # Check if user already exists
            db = get_db()
            if db.find_user_by_email(email):
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Email already registered'}), 400
                flash('Email already registered', 'error')
                return render_template('register.html')
            
            if db.find_user_by_username(username):
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Username already taken'}), 400
                flash('Username already taken', 'error')
                return render_template('register.html')
            
            # Create user
            user = db.create_user(username, email, password, full_name)
            
            if user:
                logger.info(f"New user registered: {username}")
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Registration successful! Please login.',
                        'redirect': url_for('auth.login')
                    })
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            else:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Registration failed'}), 500
                flash('Registration failed. Please try again.', 'error')
                return render_template('register.html')
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            if request.is_json:
                return jsonify({'success': False, 'error': 'Registration failed'}), 500
            flash('Registration failed. Please try again.', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            
            email = data.get('email', '').strip()
            password = data.get('password', '')
            remember = data.get('remember', False)
            
            # Validation
            if not email or not password:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Email and password are required'}), 400
                flash('Email and password are required', 'error')
                return render_template('login.html')
            
            # Find user
            db = get_db()
            user_data = db.find_user_by_email(email)
            
            if not user_data:
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
                flash('Invalid email or password', 'error')
                return render_template('login.html')
            
            # Verify password
            if not db.verify_password(user_data, password):
                if request.is_json:
                    return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
                flash('Invalid email or password', 'error')
                return render_template('login.html')
            
            # Create user object and login
            user = User.from_db(user_data)
            login_user(user, remember=bool(remember))
            
            # Update last login
            db.update_last_login(user.id)
            
            logger.info(f"User logged in: {user.username}")
            
            next_page = request.args.get('next')
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful!',
                    'redirect': next_page or url_for('main.dashboard')
                })
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            if request.is_json:
                return jsonify({'success': False, 'error': 'Login failed'}), 500
            flash('Login failed. Please try again.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

@auth_bp.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def update_profile():
    """Get or update user profile"""
    db = get_db()
    
    if request.method == 'PUT':
        try:
            data = request.get_json()
            profile_data = {
                'company': data.get('company', ''),
                'phone': data.get('phone', ''),
                'role': data.get('role', 'user')
            }
            
            success = db.update_user_profile(current_user.id, profile_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update profile'
                }), 500
                
        except Exception as e:
            logger.error(f"Profile update error: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500
    
    # GET request - return profile
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

@auth_bp.route('/api/user')
@login_required
def get_current_user():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

@auth_bp.route('/api/check-auth')
def check_auth():
    """Check if user is authenticated"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    return jsonify({
        'authenticated': False
    })

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        # Validation
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Current password and new password are required'
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'error': 'New password must be at least 6 characters'
            }), 400
        
        # Get database
        db = get_db()
        
        # Get current user data
        user_data = db.find_user_by_email(current_user.email)
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Verify current password
        if not db.verify_password(user_data, current_password):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Update password
        success = db.update_password(current_user.id, new_password)
        
        if success:
            logger.info(f"Password changed for user: {current_user.username}")
            return jsonify({
                'success': True,
                'message': 'Password changed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to change password'
            }), 500
            
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to change password'
        }), 500