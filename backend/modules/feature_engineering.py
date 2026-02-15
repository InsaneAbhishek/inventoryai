"""
Module 3: Feature Engineering Module
Generate and select relevant forecasting features
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FeatureEngineering:
    """Generate and select relevant forecasting features"""
    
    def __init__(self):
        self.feature_names = []
    
    def create_features(self, data, weather_data=pd.DataFrame(), holiday_data=pd.DataFrame(), options=None):
        """
        Complete feature engineering pipeline
        
        Args:
            data: Preprocessed DataFrame
            weather_data: Weather DataFrame
            holiday_data: Holiday DataFrame
            options: Dictionary of feature creation options
            
        Returns:
            pandas.DataFrame: DataFrame with engineered features
        """
        if options is None:
            options = {
                'create_lags': True,
                'moving_averages': True,
                'date_features': True,
                'weather_features': True,
                'holiday_features': True
            }
        
        logger.info("Starting feature engineering")
        
        # Create a copy to avoid modifying original
        df = data.copy()
        
        # Step 1: Create lagged features
        if options['create_lags']:
            df = self.create_lagged_features(df)
            logger.info("Lagged features created")
        
        # Step 2: Create moving average features
        if options['moving_averages']:
            df = self.create_moving_averages(df)
            logger.info("Moving average features created")
        
        # Step 3: Create date-related features
        if options['date_features']:
            df = self.create_date_features(df)
            logger.info("Date features created")
        
        # Step 4: Create weather features
        if options['weather_features'] and not weather_data.empty:
            df = self.create_weather_features(df, weather_data)
            logger.info("Weather features created")
        
        # Step 5: Create holiday features
        if options['holiday_features'] and not holiday_data.empty:
            df = self.create_holiday_features(df, holiday_data)
            logger.info("Holiday features created")
        
        # Step 6: Create trend and seasonality features
        df = self.create_trend_features(df)
        logger.info("Trend features created")
        
        # Step 7: Handle missing values from lag features
        df = df.bfill().ffill()
        
        # Store feature names
        self.feature_names = [col for col in df.columns if col not in ['date']]
        
        logger.info(f"Feature engineering complete. Total features: {len(self.feature_names)}")
        return df
    
    def create_lagged_features(self, df):
        """Create lagged sales/demand features"""
        try:
            target_col = 'demand' if 'demand' in df.columns else 'sales'
            
            # Create lags for different time periods
            lags = [1, 2, 3, 7, 14, 30]  # Day, week, bi-week, month
            
            for lag in lags:
                df[f'{target_col}_lag_{lag}'] = df[target_col].shift(lag)
            
            logger.info(f"Created {len(lags)} lagged features")
            return df
            
        except Exception as e:
            logger.error(f"Error creating lagged features: {str(e)}")
            raise
    
    def create_moving_averages(self, df):
        """Create moving average features"""
        try:
            target_col = 'demand' if 'demand' in df.columns else 'sales'
            
            # Different window sizes
            windows = [3, 7, 14, 30]
            
            for window in windows:
                df[f'{target_col}_ma_{window}'] = df[target_col].rolling(window=window).mean()
                df[f'{target_col}_std_{window}'] = df[target_col].rolling(window=window).std()
            
            # Exponential moving average
            df[f'{target_col}_ema_7'] = df[target_col].ewm(span=7).mean()
            
            logger.info(f"Created moving average features with windows: {windows}")
            return df
            
        except Exception as e:
            logger.error(f"Error creating moving averages: {str(e)}")
            raise
    
    def create_date_features(self, df):
        """Extract date-related features"""
        try:
            # Ensure date column exists
            if 'date' not in df.columns:
                if df.index.name == 'date':
                    df = df.reset_index()
                else:
                    df['date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
            
            df['date'] = pd.to_datetime(df['date'])
            
            # Extract date components
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['day'] = df['date'].dt.day
            df['day_of_week'] = df['date'].dt.dayofweek
            df['day_of_year'] = df['date'].dt.dayofyear
            df['week_of_year'] = df['date'].dt.isocalendar().week
            df['quarter'] = df['date'].dt.quarter
            
            # Create binary features
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
            df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
            df['is_quarter_start'] = df['date'].dt.is_quarter_start.astype(int)
            df['is_quarter_end'] = df['date'].dt.is_quarter_end.astype(int)
            
            # Create cyclical features for seasonality
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
            
            logger.info("Date features created")
            return df
            
        except Exception as e:
            logger.error(f"Error creating date features: {str(e)}")
            raise
    
    def create_weather_features(self, df, weather_data):
        """Create weather-related features"""
        try:
            # Merge weather data
            if not weather_data.empty and 'date' in df.columns:
                df = df.merge(weather_data, on='date', how='left')
                
                # Create weather interaction features
                if 'temperature' in df.columns:
                    df['temp_squared'] = df['temperature'] ** 2
                    
                    # Temperature bins
                    df['temp_category'] = pd.cut(
                        df['temperature'],
                        bins=[-np.inf, 10, 20, 30, np.inf],
                        labels=['cold', 'cool', 'warm', 'hot']
                    )
                    
                    # Hot day indicator
                    df['is_hot_day'] = (df['temperature'] > 25).astype(int)
                
                if 'precipitation' in df.columns:
                    # Rainy day indicator
                    df['is_rainy_day'] = (df['precipitation'] > 0).astype(int)
                    df['precipitation_category'] = pd.cut(
                        df['precipitation'],
                        bins=[-np.inf, 0, 5, 10, np.inf],
                        labels=['no_rain', 'light', 'moderate', 'heavy']
                    )
                
                logger.info("Weather features merged and created")
            
            return df
            
        except Exception as e:
            logger.error(f"Error creating weather features: {str(e)}")
            return df
    
    def create_holiday_features(self, df, holiday_data):
        """Create holiday-related features"""
        try:
            if not holiday_data.empty and 'date' in df.columns:
                df = df.merge(holiday_data, on='date', how='left')
                
                # Create holiday flag
                df['is_holiday'] = df['is_holiday'].fillna(False).astype(int)
                
                # Create pre-holiday and post-holiday flags
                df['is_pre_holiday'] = df['is_holiday'].shift(-1).fillna(0).astype(int)
                df['is_post_holiday'] = df['is_holiday'].shift(1).fillna(0).astype(int)
                
                logger.info("Holiday features created")
            
            return df
            
        except Exception as e:
            logger.error(f"Error creating holiday features: {str(e)}")
            return df
    
    def create_trend_features(self, df):
        """Create trend and seasonality features"""
        try:
            target_col = 'demand' if 'demand' in df.columns else 'sales'
            
            # Create linear trend
            df['trend'] = np.arange(len(df))
            
            # Create quadratic trend
            df['trend_squared'] = df['trend'] ** 2
            
            # Create momentum features (rate of change)
            df['demand_change'] = df[target_col].diff()
            df['demand_change_pct'] = df[target_col].pct_change() * 100
            
            # Create volatility features
            df['demand_volatility_7'] = df[target_col].rolling(window=7).std()
            df['demand_volatility_14'] = df[target_col].rolling(window=14).std()
            
            # Create demand relative to moving average
            df['demand_ma_ratio_7'] = df[target_col] / df[f'{target_col}_ma_7']
            
            logger.info("Trend features created")
            return df
            
        except Exception as e:
            logger.error(f"Error creating trend features: {str(e)}")
            raise
    
    def select_features(self, df, method='correlation', n_features=20):
        """
        Select most important features
        
        Args:
            df: DataFrame with features
            method: Selection method ('correlation', 'variance')
            n_features: Number of features to select
            
        Returns:
            pandas.DataFrame: DataFrame with selected features
        """
        try:
            target_col = 'demand' if 'demand' in df.columns else 'sales'
            
            if method == 'correlation':
                # Calculate correlation with target
                correlations = df.corr()[target_col].abs().sort_values(ascending=False)
                
                # Select top features
                selected_features = correlations.head(n_features).index.tolist()
                
                logger.info(f"Selected {len(selected_features)} features using correlation")
                return df[selected_features]
            
            elif method == 'variance':
                # Calculate variance for each feature
                variances = df.var().sort_values(ascending=False)
                
                # Select top features
                selected_features = variances.head(n_features).index.tolist()
                
                logger.info(f"Selected {len(selected_features)} features using variance")
                return df[selected_features]
            
            else:
                logger.warning(f"Unknown selection method: {method}, returning all features")
                return df
                
        except Exception as e:
            logger.error(f"Error selecting features: {str(e)}")
            return df