"""
Module 4: Model Selection & Training Module
Train demand forecasting models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelTraining:
    """Train multiple predictive models for demand forecasting"""
    
    def __init__(self):
        self.models = {}
        self.model_performance = {}
        self.model_dir = '../models'
    
    def train_multiple_models(self, data, models_to_train=['random_forest', 'gradient_boosting', 'arima'], test_size=0.2):
        """
        Train multiple models
        
        Args:
            data: Feature-engineered DataFrame
            models_to_train: List of model names to train
            test_size: Proportion of data for testing
            
        Returns:
            dict: Training results with models and metadata
        """
        logger.info(f"Starting model training for {len(models_to_train)} models")
        
        start_time = time.time()
        trained_models = {}
        
        # Prepare data
        X, y = self._prepare_data(data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, shuffle=False)
        
        split_info = {
            'train_size': len(X_train),
            'test_size': len(X_test),
            'feature_count': X_train.shape[1]
        }
        
        # Train each model
        for model_name in models_to_train:
            try:
                logger.info(f"Training {model_name} model")
                
                if model_name == 'random_forest':
                    model, metrics = self._train_random_forest(X_train, y_train, X_test, y_test)
                elif model_name == 'gradient_boosting':
                    model, metrics = self._train_gradient_boosting(X_train, y_train, X_test, y_test)
                elif model_name == 'linear_regression':
                    model, metrics = self._train_linear_regression(X_train, y_train, X_test, y_test)
                elif model_name == 'arima':
                    # ARIMA is handled separately due to time series nature
                    continue
                else:
                    logger.warning(f"Unknown model: {model_name}")
                    continue
                
                trained_models[model_name] = model
                self.model_performance[model_name] = metrics
                
                logger.info(f"{model_name} trained - MAE: {metrics['mae']:.2f}")
                
                # Save model
                self._save_model(model, model_name)
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                continue
        
        training_time = time.time() - start_time
        
        logger.info(f"Model training completed in {training_time:.2f} seconds")
        
        return {
            'models': trained_models,
            'training_time': training_time,
            'split_info': split_info,
            'performance': self.model_performance
        }
    
    def _prepare_data(self, data):
        """Prepare features and target for training"""
        target_col = 'demand' if 'demand' in data.columns else 'sales'
        
        # Drop non-feature columns (including string columns and both target columns)
        # IMPORTANT: Also exclude quantity, revenue, and other columns that are derived from the target
        exclude_cols = ['date', 'temp_category', 'precipitation_category', 'location', 
                       'holiday_name', 'country', 'product_id', 'category', 'demand', 'sales',
                       'quantity', 'revenue', 'product_name', 'store', 'customer_segment']
        feature_cols = [col for col in data.columns if col not in exclude_cols]
        
        # Remove NaN values
        clean_data = data[feature_cols].bfill().ffill().fillna(0)
        
        # Select only numeric columns
        numeric_cols = clean_data.select_dtypes(include=['int64', 'float64']).columns
        clean_data = clean_data[numeric_cols]
        
        # Get target
        y = data[target_col]
        
        return clean_data, y
    
    def _train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train Random Forest model"""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, predictions)
        
        return model, metrics
    
    def _train_gradient_boosting(self, X_train, y_train, X_test, y_test):
        """Train Gradient Boosting model"""
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, predictions)
        
        return model, metrics
    
    def _train_linear_regression(self, X_train, y_train, X_test, y_test):
        """Train Linear Regression model"""
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Evaluate
        predictions = model.predict(X_test)
        metrics = self._calculate_metrics(y_test, predictions)
        
        return model, metrics
    
    def _calculate_metrics(self, y_true, y_pred):
        """Calculate evaluation metrics"""
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        # Calculate R²
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - y_true.mean()) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        return {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2': float(r2)
        }
    
    def _save_model(self, model, model_name):
        """Save trained model to disk"""
        try:
            import os
            os.makedirs(self.model_dir, exist_ok=True)
            
            filepath = f"{self.model_dir}/{model_name}_model.pkl"
            joblib.dump(model, filepath)
            
            logger.info(f"Model saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
    
    def load_model(self, model_name):
        """Load trained model from disk"""
        try:
            filepath = f"{self.model_dir}/{model_name}_model.pkl"
            model = joblib.load(filepath)
            
            logger.info(f"Model loaded: {filepath}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None
    
    def tune_hyperparameters(self, model_name, X_train, y_train):
        """
        Perform hyperparameter tuning using GridSearchCV
        
        Args:
            model_name: Name of the model to tune
            X_train: Training features
            y_train: Training target
            
        Returns:
            Best model and parameters
        """
        logger.info(f"Tuning hyperparameters for {model_name}")
        
        if model_name == 'random_forest':
            model = RandomForestRegressor(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 15, 20],
                'min_samples_split': [2, 5, 10]
            }
        
        elif model_name == 'gradient_boosting':
            model = GradientBoostingRegressor(random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            }
        
        else:
            logger.warning(f"Hyperparameter tuning not available for {model_name}")
            return None, None
        
        # Perform grid search
        grid_search = GridSearchCV(
            model,
            param_grid,
            cv=5,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        return grid_search.best_estimator_, grid_search.best_params_