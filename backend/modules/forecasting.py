"""
Module 5: Forecasting & Prediction Module
Generate future inventory demand forecasts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Forecasting:
    """Generate demand forecasts using trained models"""
    
    def __init__(self):
        self.forecast_history = []
    
    def generate_forecast(self, model, features_data, horizon_days=30):
        """
        Generate demand forecast for specified horizon
        
        Args:
            model: Trained machine learning model
            features_data: DataFrame with features
            horizon_days: Number of days to forecast
            
        Returns:
            dict: Forecast results with predictions and confidence intervals
        """
        try:
            logger.info(f"Generating {horizon_days}-day forecast")
            
            # Get last known data point
            last_row = features_data.iloc[-1:].copy()
            last_date = last_row['date'].values[0]
            
            # Generate forecast dates
            forecast_dates = pd.date_range(
                start=last_date + timedelta(days=1),
                periods=horizon_days,
                freq='D'
            )
            
            # Prepare forecast features
            forecast_features = self._prepare_forecast_features(
                features_data,
                last_row,
                forecast_dates
            )
            
            # Get the feature names that the model was trained on
            # by removing target and non-feature columns from training data
            exclude_cols = ['date', 'demand', 'sales', 'location', 'holiday_name', 
                          'country', 'product_id', 'category', 'temp_category', 
                          'precipitation_category', 'quantity', 'revenue', 
                          'product_name', 'store', 'customer_segment',
                          'year', 'month', 'day', 'day_of_week', 'day_of_year',
                          'week_of_year', 'quarter']
            training_features = features_data.drop(columns=exclude_cols, errors='ignore')
            training_features = training_features.select_dtypes(include=['int64', 'float64'])
            
            # Remove extra columns from forecast features
            forecast_features = forecast_features.drop(columns=['year', 'month', 'day', 'day_of_week', 
                                                                'day_of_year', 'week_of_year', 'quarter'], 
                                                      errors='ignore')
            
            # Ensure forecast features match training features exactly
            for col in training_features.columns:
                if col not in forecast_features.columns:
                    forecast_features[col] = 0
            
            # Keep only the columns that were in training, in the same order
            forecast_features = forecast_features[training_features.columns]
            
            # Generate predictions
            predictions = model.predict(forecast_features)
            
            # Ensure predictions are non-negative
            predictions = np.maximum(predictions, 0)
            
            # Create forecast DataFrame
            forecast_df = pd.DataFrame({
                'date': forecast_dates,
                'predicted_demand': predictions
            })
            
            # Calculate confidence intervals (using historical prediction variance)
            confidence_intervals = self._calculate_confidence_intervals(
                predictions,
                features_data
            )
            
            forecast_df['lower_bound'] = confidence_intervals['lower']
            forecast_df['upper_bound'] = confidence_intervals['upper']
            
            # Add trend and seasonality adjustments
            forecast_df = self._add_seasonal_adjustments(forecast_df)
            
            result = {
                'predictions': forecast_df,
                'confidence_intervals': confidence_intervals,
                'horizon_days': horizon_days,
                'model_type': type(model).__name__,
                'generated_at': datetime.now().isoformat()
            }
            
            # Store forecast history
            self.forecast_history.append({
                'date': datetime.now().isoformat(),
                'horizon': horizon_days,
                'forecast': forecast_df
            })
            
            logger.info(f"Forecast generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            raise
    
    def _prepare_forecast_features(self, historical_data, last_row, forecast_dates):
        """
        Prepare feature matrix for forecasting
        
        Args:
            historical_data: Historical feature data
            last_row: Last row of historical data
            forecast_dates: Dates to forecast
            
        Returns:
            DataFrame: Feature matrix for prediction
        """
        try:
            # Get recent demand values for lag features
            target_col = 'demand' if 'demand' in historical_data.columns else 'sales'
            recent_demand = historical_data[target_col].tail(30).values
            
            # Get the last row as a dictionary
            last_values = last_row.iloc[0].to_dict()
            
            # Start with last row and expand for forecast horizon
            forecast_rows = []
            
            # Use recent average as baseline for predictions
            baseline_demand = historical_data[target_col].tail(30).mean()
            
            for i, date in enumerate(forecast_dates):
                # Create a new row based on last values
                row = last_values.copy()
                row['date'] = date
                
                # Update date-related features
                row['year'] = date.year
                row['month'] = date.month
                row['day'] = date.day
                row['day_of_week'] = date.dayofweek
                row['day_of_year'] = date.dayofyear
                row['week_of_year'] = date.isocalendar().week
                row['quarter'] = date.quarter
                row['is_weekend'] = 1 if date.dayofweek >= 5 else 0
                
                # Update cyclical features
                row['month_sin'] = np.sin(2 * np.pi * date.month / 12)
                row['month_cos'] = np.cos(2 * np.pi * date.month / 12)
                row['day_of_week_sin'] = np.sin(2 * np.pi * date.dayofweek / 7)
                row['day_of_week_cos'] = np.cos(2 * np.pi * date.dayofweek / 7)
                
                # Update trend
                row['trend'] = len(historical_data) + i + 1
                row['trend_squared'] = row['trend'] ** 2
                
                # Update lag features with recent values
                if 'demand_lag_1' in row:
                    if i == 0:
                        row['demand_lag_1'] = recent_demand[-1] if len(recent_demand) > 0 else baseline_demand
                    else:
                        row['demand_lag_1'] = baseline_demand  # Use baseline for future lags
                
                if 'demand_lag_2' in row:
                    row['demand_lag_2'] = recent_demand[-2] if len(recent_demand) > 1 else baseline_demand
                
                if 'demand_lag_3' in row:
                    row['demand_lag_3'] = recent_demand[-3] if len(recent_demand) > 2 else baseline_demand
                
                if 'demand_lag_7' in row:
                    row['demand_lag_7'] = recent_demand[-7] if len(recent_demand) > 6 else baseline_demand
                
                if 'demand_lag_14' in row:
                    row['demand_lag_14'] = recent_demand[-14] if len(recent_demand) > 13 else baseline_demand
                
                # Update moving averages with recent data
                if 'demand_ma_7' in row:
                    row['demand_ma_7'] = recent_demand[-7:].mean() if len(recent_demand) >= 7 else baseline_demand
                
                if 'demand_ma_14' in row:
                    row['demand_ma_14'] = recent_demand[-14:].mean() if len(recent_demand) >= 14 else baseline_demand
                
                if 'demand_ma_30' in row:
                    row['demand_ma_30'] = recent_demand.mean() if len(recent_demand) > 0 else baseline_demand
                
                forecast_rows.append(row)
            
            # Create DataFrame from rows
            forecast_df = pd.DataFrame(forecast_rows)
            
            # Drop non-feature columns (must match model training exclusions)
            exclude_cols = ['date', 'demand', 'sales', 'location', 'holiday_name', 
                          'country', 'product_id', 'category', 'temp_category', 
                          'precipitation_category', 'quantity', 'revenue', 
                          'product_name', 'store', 'customer_segment']
            
            X_forecast = forecast_df.drop(columns=exclude_cols, errors='ignore')
            
            # Select only numeric columns
            numeric_cols = X_forecast.select_dtypes(include=['int64', 'float64']).columns
            X_forecast = X_forecast[numeric_cols]
            
            return X_forecast.fillna(0)
            
        except Exception as e:
            logger.error(f"Error preparing forecast features: {str(e)}")
            raise
    
    def _calculate_confidence_intervals(self, predictions, historical_data):
        """
        Calculate confidence intervals for predictions
        
        Args:
            predictions: Predicted values
            historical_data: Historical feature data
            
        Returns:
            dict: Lower and upper bounds
        """
        try:
            # Calculate prediction uncertainty based on historical variance
            target_col = 'demand' if 'demand' in historical_data.columns else 'sales'
            historical_std = historical_data[target_col].std()
            
            # Confidence level (95%)
            z_score = 1.96
            
            # Calculate bounds
            lower_bound = predictions - (z_score * historical_std * 0.5)
            upper_bound = predictions + (z_score * historical_std * 0.5)
            
            # Ensure bounds are non-negative
            lower_bound = np.maximum(lower_bound, 0)
            
            return {
                'lower': lower_bound,
                'upper': upper_bound,
                'confidence_level': 0.95
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence intervals: {str(e)}")
            return {
                'lower': predictions * 0.8,
                'upper': predictions * 1.2,
                'confidence_level': 0.95
            }
    
    def _add_seasonal_adjustments(self, forecast_df):
        """
        Add seasonal adjustments to forecast
        
        Args:
            forecast_df: DataFrame with predictions
            
        Returns:
            DataFrame: Adjusted forecast
        """
        try:
            # Define seasonal multipliers
            seasonal_multipliers = {
                'month': {
                    1: 0.9,   # January - post-holiday dip
                    2: 0.85,  # February
                    3: 0.95,  # March
                    4: 1.0,   # April
                    5: 1.05,  # May
                    6: 1.1,   # June - summer
                    7: 1.15,  # July
                    8: 1.1,   # August
                    9: 1.05,  # September
                    10: 1.1,  # October
                    11: 1.2,  # November - pre-holiday
                    12: 1.3   # December - holiday peak
                },
                'day_of_week': {
                    0: 1.0,   # Monday
                    1: 1.05,  # Tuesday
                    2: 1.1,   # Wednesday
                    3: 1.05,  # Thursday
                    4: 1.15,  # Friday
                    5: 1.2,   # Saturday
                    6: 0.9    # Sunday
                }
            }
            
            # Apply month multiplier
            forecast_df['month_multiplier'] = forecast_df['date'].dt.month.map(
                seasonal_multipliers['month']
            )
            
            # Apply day of week multiplier
            forecast_df['dow_multiplier'] = forecast_df['date'].dt.dayofweek.map(
                seasonal_multipliers['day_of_week']
            )
            
            # Apply combined multiplier (average of both)
            forecast_df['combined_multiplier'] = (
                forecast_df['month_multiplier'] + forecast_df['dow_multiplier']
            ) / 2
            
            # Adjust predictions
            forecast_df['seasonal_adjusted'] = (
                forecast_df['predicted_demand'] * forecast_df['combined_multiplier']
            ).round(0)
            
            # Update main prediction with seasonal adjustment
            forecast_df['predicted_demand'] = forecast_df['seasonal_adjusted']
            
            # Recalculate bounds with seasonal adjustment
            forecast_df['lower_bound'] = (forecast_df['lower_bound'] * forecast_df['combined_multiplier']).round(0)
            forecast_df['upper_bound'] = (forecast_df['upper_bound'] * forecast_df['combined_multiplier']).round(0)
            
            return forecast_df
            
        except Exception as e:
            logger.error(f"Error adding seasonal adjustments: {str(e)}")
            return forecast_df
    
    def generate_rolling_forecast(self, model, features_data, window_size=30, horizon_days=7):
        """
        Generate rolling forecast with periodic updates
        
        Args:
            model: Trained model
            features_data: Historical feature data
            window_size: Size of rolling window
            horizon_days: Forecast horizon
            
        Returns:
            DataFrame: Rolling forecast results
        """
        try:
            logger.info(f"Generating rolling forecast (window: {window_size}, horizon: {horizon_days})")
            
            forecasts = []
            
            # Slide through data
            for i in range(len(features_data) - window_size, len(features_data)):
                window_data = features_data.iloc[:i+1]
                
                # Generate forecast
                forecast = self.generate_forecast(model, window_data, horizon_days)
                forecasts.append(forecast['predictions'])
            
            # Combine forecasts
            rolling_forecast = pd.concat(forecasts)
            
            logger.info("Rolling forecast generated")
            return rolling_forecast
            
        except Exception as e:
            logger.error(f"Error generating rolling forecast: {str(e)}")
            raise
    
    def compare_forecasts(self, forecast1, forecast2):
        """
        Compare two forecasts
        
        Args:
            forecast1: First forecast results
            forecast2: Second forecast results
            
        Returns:
            dict: Comparison metrics
        """
        try:
            df1 = forecast1['predictions']
            df2 = forecast2['predictions']
            
            # Align forecasts
            common_dates = pd.merge(df1, df2, on='date', suffixes=('_1', '_2'))
            
            # Calculate differences
            common_dates['difference'] = (
                common_dates['predicted_demand_1'] - common_dates['predicted_demand_2']
            )
            common_dates['abs_difference'] = common_dates['difference'].abs()
            common_dates['pct_difference'] = (
                common_dates['difference'] / common_dates['predicted_demand_1'] * 100
            )
            
            comparison = {
                'mean_difference': float(common_dates['abs_difference'].mean()),
                'max_difference': float(common_dates['abs_difference'].max()),
                'mean_pct_difference': float(common_dates['pct_difference'].mean()),
                'correlation': float(common_dates['predicted_demand_1'].corr(
                    common_dates['predicted_demand_2']
                )),
                'forecast1_total': float(common_dates['predicted_demand_1'].sum()),
                'forecast2_total': float(common_dates['predicted_demand_2'].sum())
            }
            
            logger.info("Forecast comparison completed")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing forecasts: {str(e)}")
            raise