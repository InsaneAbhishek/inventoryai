"""
Intelligent Inventory Demand Forecasting and Optimization System
Complete Backend Application with MongoDB Authentication and all 10 modules
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, redirect, url_for, flash, Blueprint
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
import json
import os
import logging
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import traceback
import pandas as pd
import numpy as np

# Import configuration and database
from config import Config
from database import Database
from models.user import User

# Import ML modules
from modules.data_collection import DataCollection
from modules.data_preprocessing import DataPreprocessing
from modules.feature_engineering import FeatureEngineering
from modules.model_training import ModelTraining
from modules.forecasting import Forecasting
from modules.model_evaluation import ModelEvaluation
from modules.notifications import Notifications
from modules.insights import ActionableInsights

# Import authentication blueprints
from auth import auth_bp

# Initialize Flask app
app = Flask(__name__, 
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Configure CORS to support credentials
CORS(app, 
     supports_credentials=True,
     resources={r"/api/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     expose_headers=["Content-Type"])

# Load configuration
app.config.from_object(Config)

# Initialize database
db = Database(app.config['MONGO_URI'], app.config['DB_NAME'])

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user from database"""
    user_data = db.find_user_by_id(user_id)
    if user_data:
        return User.from_db(user_data)
    return None

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Initialize modules
data_collection = DataCollection()
data_preprocessing = DataPreprocessing()
feature_engineering = FeatureEngineering()
model_training = ModelTraining()
forecasting = Forecasting()
model_evaluation = ModelEvaluation()
notifications = Notifications()
insights = ActionableInsights()

# Global storage for processed data (will be moved to MongoDB)
processed_data = {}
trained_models = {}

# Create main routes blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('index.html')

@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

# API Routes
@main_bp.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules': ['data_collection', 'preprocessing', 'feature_engineering', 
                   'model_training', 'forecasting', 'evaluation', 'notifications', 'insights']
    })

@main_bp.route('/api/user')
@login_required
def get_user():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    })

# Module 1: Data Collection Endpoints
@main_bp.route('/api/upload', methods=['POST'])
@login_required
def upload_data():
    """Upload sales data file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            # Process the uploaded file
            result = data_collection.import_sales_data(filepath)
            
            # Save to MongoDB
            user_id = current_user.id
            db.save_user_data(user_id, 'raw', result.to_dict('records'))
            
            # Update local storage
            processed_data[user_id] = {}
            processed_data[user_id]['raw'] = result
            
            logger.info(f"Data uploaded successfully by user {user_id}: {filename}")
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': filename,
                'records': len(result),
                'preview': result.head(10).to_dict('records')
            })
        
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/external-data', methods=['POST'])
@login_required
def fetch_external_data():
    """Fetch weather and holiday data"""
    try:
        user_id = current_user.id
        data = request.json
        start_date = data.get('start_date', '2024-01-01')
        end_date = data.get('end_date', '2024-12-31')
        location = data.get('location', 'New York')
        
        # Fetch external data
        weather_data = data_collection.fetch_weather_data(start_date, end_date, location)
        holiday_data = data_collection.fetch_holiday_data(start_date, end_date)
        
        if user_id not in processed_data:
            processed_data[user_id] = {}
        
        processed_data[user_id]['weather'] = weather_data
        processed_data[user_id]['holidays'] = holiday_data
        
        logger.info(f"External data fetched for user {user_id}")
        return jsonify({
            'success': True,
            'weather_records': len(weather_data),
            'holiday_records': len(holiday_data),
            'weather_data': weather_data.to_dict('records') if len(weather_data) > 0 else [],
            'holiday_data': holiday_data.to_dict('records') if len(holiday_data) > 0 else []
        })
    
    except Exception as e:
        logger.error(f"Error fetching external data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 2: Data Preprocessing Endpoints
@main_bp.route('/api/preprocess', methods=['POST'])
@login_required
def preprocess_data():
    """Preprocess the raw data"""
    try:
        user_id = current_user.id
        
        if user_id not in processed_data or 'raw' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'No raw data available. Please upload data first.'}), 400
        
        data = request.json
        options = {
            'handle_missing': data.get('handle_missing', True),
            'remove_outliers': data.get('remove_outliers', True),
            'encode_categorical': data.get('encode_categorical', True),
            'scale_features': data.get('scale_features', True)
        }
        
        # Preprocess data
        preprocessed = data_preprocessing.process_data(
            processed_data[user_id]['raw'], 
            options
        )
        
        processed_data[user_id]['preprocessed'] = preprocessed
        
        # Save to MongoDB
        db.save_user_data(user_id, 'preprocessed', preprocessed.to_dict('records'))
        
        logger.info(f"Data preprocessed successfully for user {user_id}")
        return jsonify({
            'success': True,
            'message': 'Data preprocessed successfully',
            'records': len(preprocessed),
            'columns': list(preprocessed.columns),
            'preview': preprocessed.head(10).to_dict('records')
        })
    
    except Exception as e:
        logger.error(f"Error preprocessing data: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 3: Feature Engineering Endpoints
@main_bp.route('/api/engineer-features', methods=['POST'])
@login_required
def engineer_features():
    """Generate features for modeling"""
    try:
        user_id = current_user.id
        
        if user_id not in processed_data or 'preprocessed' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'No preprocessed data available'}), 400
        
        data = request.json
        options = {
            'create_lags': data.get('create_lags', True),
            'moving_averages': data.get('moving_averages', True),
            'date_features': data.get('date_features', True),
            'weather_features': data.get('weather_features', True),
            'holiday_features': data.get('holiday_features', True)
        }
        
        # Engineer features
        features = feature_engineering.create_features(
            processed_data[user_id]['preprocessed'],
            processed_data[user_id].get('weather', pd.DataFrame()),
            processed_data[user_id].get('holidays', pd.DataFrame()),
            options
        )
        
        processed_data[user_id]['features'] = features
        
        # Save to MongoDB
        db.save_user_data(user_id, 'features', features.to_dict('records'))
        
        logger.info(f"Features engineered successfully for user {user_id}")
        return jsonify({
            'success': True,
            'message': 'Features created successfully',
            'features_count': len(features.columns),
            'features': list(features.columns),
            'preview': features.head(10).to_dict('records')
        })
    
    except Exception as e:
        logger.error(f"Error engineering features: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 4: Model Training Endpoints
@main_bp.route('/api/train', methods=['POST'])
@login_required
def train_models():
    """Train forecasting models"""
    try:
        user_id = current_user.id
        
        if user_id not in processed_data or 'features' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'No feature data available'}), 400
        
        data = request.json
        models_to_train = data.get('models', ['random_forest', 'gradient_boosting', 'linear_regression'])
        test_size = data.get('test_size', 0.2)
        
        # Train models
        training_results = model_training.train_multiple_models(
            processed_data[user_id]['features'],
            models_to_train,
            test_size
        )
        
        if user_id not in trained_models:
            trained_models[user_id] = {}
        
        trained_models[user_id].update(training_results['models'])
        processed_data[user_id]['train_test_split'] = training_results['split_info']
        
        # Save to MongoDB
        for model_name, model in training_results['models'].items():
            # In production, you'd serialize the model properly
            # For now, we save metadata with performance info
            db.save_model(user_id, model_name, {}, training_results.get('performance', {}).get(model_name, {}))
        
        logger.info(f"Models trained successfully for user {user_id}: {list(trained_models[user_id].keys())}")
        return jsonify({
            'success': True,
            'message': 'Models trained successfully',
            'models': list(trained_models[user_id].keys()),
            'training_time': training_results['training_time'],
            'split_info': training_results['split_info']
        })
    
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 5: Forecasting Endpoints
@main_bp.route('/api/forecast', methods=['POST'])
@login_required
def generate_forecast():
    """Generate demand forecasts"""
    try:
        user_id = current_user.id
        
        if user_id not in trained_models or not trained_models[user_id]:
            return jsonify({'success': False, 'error': 'No trained models available'}), 400
        
        data = request.json
        horizon = data.get('horizon', 30)  # days
        model_name = data.get('model', 'random_forest')
        
        if model_name not in trained_models[user_id]:
            return jsonify({'success': False, 'error': f'Model {model_name} not found'}), 400
        
        # Generate forecast
        forecast_results = forecasting.generate_forecast(
            trained_models[user_id][model_name],
            processed_data[user_id]['features'],
            horizon
        )
        
        processed_data[user_id]['forecast'] = forecast_results
        
        # Save to MongoDB
        db.save_user_data(user_id, 'forecast', forecast_results['predictions'].to_dict('records'))
        
        logger.info(f"Forecast generated for user {user_id}: {horizon} days using {model_name}")
        
        # Convert confidence intervals to serializable format
        confidence_intervals = forecast_results.get('confidence_intervals', {})
        if 'lower' in confidence_intervals and hasattr(confidence_intervals['lower'], 'tolist'):
            confidence_intervals['lower'] = confidence_intervals['lower'].tolist()
        if 'upper' in confidence_intervals and hasattr(confidence_intervals['upper'], 'tolist'):
            confidence_intervals['upper'] = confidence_intervals['upper'].tolist()
        
        return jsonify({
            'success': True,
            'model_used': model_name,
            'horizon': horizon,
            'forecast': forecast_results['predictions'].to_dict('records'),
            'confidence_intervals': confidence_intervals,
            'summary': {
                'total_demand': float(forecast_results['predictions']['predicted_demand'].sum()),
                'avg_daily_demand': float(forecast_results['predictions']['predicted_demand'].mean()),
                'peak_demand': float(forecast_results['predictions']['predicted_demand'].max()),
                'peak_date': forecast_results['predictions'].loc[
                    forecast_results['predictions']['predicted_demand'].idxmax(), 'date'
                ].strftime('%Y-%m-%d')
            }
        })
    
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 6: Model Evaluation Endpoints
@main_bp.route('/api/evaluate', methods=['POST'])
@login_required
def evaluate_models():
    """Evaluate model performance"""
    try:
        user_id = current_user.id
        
        if user_id not in trained_models or not trained_models[user_id]:
            return jsonify({'success': False, 'error': 'No trained models available'}), 400
        
        # Evaluate all trained models
        evaluation_results = model_evaluation.evaluate_all_models(
            trained_models[user_id],
            processed_data[user_id].get('train_test_split', {})
        )
        
        logger.info(f"Models evaluated successfully for user {user_id}")
        return jsonify({
            'success': True,
            'evaluations': evaluation_results['evaluations'],
            'best_model': evaluation_results['best_model'],
            'comparison': evaluation_results['comparison']
        })
    
    except Exception as e:
        logger.error(f"Error evaluating models: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 7: Dashboard Data Endpoints
@main_bp.route('/api/dashboard-data')
@login_required
def get_dashboard_data():
    """Get all data for dashboard"""
    try:
        user_id = current_user.id
        
        dashboard_data = {
            'has_data': user_id in processed_data and bool(processed_data[user_id]),
            'data_status': {
                'raw': user_id in processed_data and 'raw' in processed_data[user_id],
                'preprocessed': user_id in processed_data and 'preprocessed' in processed_data[user_id],
                'features': user_id in processed_data and 'features' in processed_data[user_id],
                'models_trained': user_id in trained_models and len(trained_models[user_id]) > 0,
                'forecast': user_id in processed_data and 'forecast' in processed_data[user_id]
            },
            'summary': {}
        }
        
        # Add data summaries
        if user_id in processed_data:
            if 'raw' in processed_data[user_id]:
                dashboard_data['summary']['raw_records'] = len(processed_data[user_id]['raw'])
            
            if 'forecast' in processed_data[user_id]:
                forecast = processed_data[user_id]['forecast']['predictions']
                dashboard_data['summary']['forecast_summary'] = {
                    'total_demand': float(forecast['predicted_demand'].sum()),
                    'avg_daily': float(forecast['predicted_demand'].mean()),
                    'peak_demand': float(forecast['predicted_demand'].max()),
                    'horizon': len(forecast)
                }
        
        dashboard_data['trained_models'] = list(trained_models.get(user_id, {}).keys())
        
        return jsonify(dashboard_data)
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/historical-chart-data')
@login_required
def get_historical_chart_data():
    """Get historical data for charts"""
    try:
        user_id = current_user.id
        
        if user_id not in processed_data or 'raw' not in processed_data[user_id]:
            return jsonify({'success': True, 'dates': [], 'sales': [], 'demand': []})
        
        data = processed_data[user_id]['raw']
        
        # Aggregate by date
        if 'date' in data.columns:
            chart_data = data.groupby('date').agg({
                'sales': 'sum',
                'demand': 'sum' if 'demand' in data.columns else lambda x: 0
            }).reset_index()
        else:
            return jsonify({'success': True, 'dates': [], 'sales': [], 'demand': []})
        
        return jsonify({
            'success': True,
            'dates': chart_data['date'].dt.strftime('%Y-%m-%d').tolist(),
            'sales': chart_data['sales'].tolist(),
            'demand': chart_data['demand'].tolist()
        })
    
    except Exception as e:
        logger.error(f"Error getting chart data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/forecast-chart-data')
@login_required
def get_forecast_chart_data():
    """Get forecast data for charts"""
    try:
        user_id = current_user.id
        
        if user_id not in processed_data or 'forecast' not in processed_data[user_id]:
            return jsonify({'success': True, 'dates': [], 'predicted_demand': [], 'lower_bound': [], 'upper_bound': []})
        
        forecast = processed_data[user_id]['forecast']['predictions']
        
        return jsonify({
            'success': True,
            'dates': forecast['date'].dt.strftime('%Y-%m-%d').tolist(),
            'predicted_demand': forecast['predicted_demand'].tolist(),
            'lower_bound': forecast.get('lower_bound', []).tolist(),
            'upper_bound': forecast.get('upper_bound', []).tolist()
        })
    
    except Exception as e:
        logger.error(f"Error getting forecast chart data: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 9: Notifications Endpoints
@main_bp.route('/api/configure-alerts', methods=['POST'])
@login_required
def configure_alerts():
    """Configure inventory alerts"""
    try:
        user_id = current_user.id
        data = request.json
        
        alert_config = {
            'low_stock_threshold': data.get('low_stock_threshold', 100),
            'email_enabled': data.get('email_enabled', False),
            'email_address': data.get('email_address', ''),
            'sms_enabled': data.get('sms_enabled', False),
            'phone_number': data.get('phone_number', ''),
            'alert_frequency': data.get('alert_frequency', 'daily')
        }
        
        # Save to database
        db.save_alert_config(user_id, alert_config)
        
        if user_id not in processed_data:
            processed_data[user_id] = {}
        
        processed_data[user_id]['alert_config'] = alert_config
        
        logger.info(f"Alerts configured for user {user_id}: {alert_config}")
        return jsonify({
            'success': True,
            'message': 'Alerts configured successfully',
            'config': alert_config
        })
    
    except Exception as e:
        logger.error(f"Error configuring alerts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/send-alerts', methods=['POST'])
@login_required
def send_alerts():
    """Send inventory alerts"""
    try:
        user_id = current_user.id
        
        if user_id not in processed_data or 'forecast' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'No forecast data available'}), 400
        
        if 'alert_config' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'Alerts not configured'}), 400
        
        # Check for low stock conditions
        alert_results = notifications.check_and_send_alerts(
            processed_data[user_id]['forecast']['predictions'],
            processed_data[user_id]['alert_config']
        )
        
        # Save alert to database
        if alert_results['alerts_sent'] > 0:
            db.save_alert(user_id, {
                'type': 'inventory',
                'count': alert_results['alerts_generated'],
                'items': alert_results['low_stock_items']
            })
        
        return jsonify({
            'success': True,
            'alerts_sent': alert_results['alerts_sent'],
            'low_stock_items': alert_results['low_stock_items']
        })
    
    except Exception as e:
        logger.error(f"Error sending alerts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Module 10: Insights Endpoints
@main_bp.route('/api/insights')
@login_required
def get_insights():
    """Get actionable insights"""
    try:
        user_id = current_user.id
        
        # Check if raw data exists
        if user_id not in processed_data or 'raw' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'Please upload data first'}), 400
        
        # Check if forecast exists
        if 'forecast' not in processed_data[user_id]:
            return jsonify({'success': False, 'error': 'Please generate forecast first before viewing insights'}), 400
        
        # Generate insights
        insights_results = insights.generate_insights(
            processed_data[user_id]['raw'],
            processed_data[user_id]['forecast']['predictions']
        )
        
        logger.info(f"Insights generated for user {user_id}")
        return jsonify({
            'success': True,
            'abc_analysis': insights_results['abc_analysis'],
            'reorder_points': insights_results['reorder_points'],
            'recommendations': insights_results['recommendations'],
            'optimization_summary': insights_results['optimization_summary']
        })
    
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/export-report', methods=['POST'])
@login_required
def export_report():
    """Export analysis report"""
    try:
        user_id = current_user.id
        data = request.json
        report_type = data.get('type', 'forecast')
        
        # Generate report
        report_file = insights.generate_report(
            processed_data.get(user_id, {}),
            trained_models.get(user_id, {}),
            report_type
        )
        
        return send_file(report_file, as_attachment=True)
    
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Utility functions
def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Root route - Landing page
@app.route('/')
def landing():
    """Serve the landing page"""
    return render_template('landing.html')

# Register main blueprint AFTER all routes are defined
app.register_blueprint(main_bp)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('../logs', exist_ok=True)
    os.makedirs('../models', exist_ok=True)
    os.makedirs('../reports', exist_ok=True)
    
    logger.info("Starting Inventory Demand Forecasting System with MongoDB")
    app.run(host='0.0.0.0', port=8000, debug=True)