"""
Module 2: Data Preprocessing Module
Clean and format raw data for forecasting
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class DataPreprocessing:
    """Clean and format raw data for machine learning modeling"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def process_data(self, raw_data, options=None):
        """
        Complete preprocessing pipeline
        
        Args:
            raw_data: Raw sales DataFrame
            options: Dictionary of preprocessing options
            
        Returns:
            pandas.DataFrame: Preprocessed data
        """
        if options is None:
            options = {
                'handle_missing': True,
                'remove_outliers': True,
                'encode_categorical': True,
                'scale_features': True
            }
        
        logger.info("Starting data preprocessing")
        
        # Create a copy to avoid modifying original
        df = raw_data.copy()
        
        # Step 1: Handle missing values
        if options['handle_missing']:
            df = self.handle_missing_values(df)
            logger.info("Missing values handled")
        
        # Step 2: Remove outliers
        if options['remove_outliers']:
            df = self.remove_outliers(df)
            logger.info("Outliers removed")
        
        # Step 3: Encode categorical variables
        if options['encode_categorical']:
            df = self.encode_categorical(df)
            logger.info("Categorical variables encoded")
        
        # Step 4: Scale numerical features
        if options['scale_features']:
            df = self.scale_numerical(df)
            logger.info("Numerical features scaled")
        
        # Step 5: Ensure time-series format
        df = self.format_timeseries(df)
        logger.info("Time-series format applied")
        
        logger.info(f"Preprocessing complete. Final shape: {df.shape}")
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        try:
            # Check for missing values
            missing = df.isnull().sum()
            
            if missing.sum() == 0:
                return df
            
            logger.info(f"Found missing values: {missing[missing > 0].to_dict()}")
            
            # Handle numeric columns with mean/median
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df[col].isnull().sum() > 0:
                    # Use median for robust statistics
                    df[col].fillna(df[col].median(), inplace=True)
            
            # Handle categorical columns with mode
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if df[col].isnull().sum() > 0:
                    df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
            
            # Handle date columns
            if 'date' in df.columns:
                df['date'] = df['date'].ffill()
            
            logger.info("Missing values filled")
            return df
            
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            raise
    
    def remove_outliers(self, df):
        """Remove outliers using IQR method"""
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            # Exclude date and id columns
            cols_to_check = [col for col in numeric_cols 
                           if col not in ['date', 'product_id', 'id']]
            
            original_count = len(df)
            
            for col in cols_to_check:
                if col in df.columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    # Cap outliers instead of removing (better for time series)
                    df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
                    df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
            
            outliers_removed = original_count - len(df)
            logger.info(f"Outliers capped in {len(cols_to_check)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error removing outliers: {str(e)}")
            return df
    
    def encode_categorical(self, df):
        """Encode categorical variables"""
        try:
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            for col in categorical_cols:
                if col not in ['date']:
                    # Use label encoding for simplicity
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    
                    # Handle new categories by fitting first
                    df[col] = df[col].astype(str)
                    df[col] = self.label_encoders[col].fit_transform(df[col])
            
            logger.info(f"Encoded {len(categorical_cols)} categorical columns")
            return df
            
        except Exception as e:
            logger.error(f"Error encoding categorical variables: {str(e)}")
            raise
    
    def scale_numerical(self, df):
        """Scale numerical features"""
        try:
            # Get numerical columns (excluding encoded categoricals that look numeric)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            # IMPORTANT: Exclude target variables from scaling
            exclude_cols = ['date', 'is_holiday', 'sales', 'demand', 'quantity', 'revenue']
            
            cols_to_scale = [col for col in numeric_cols 
                           if col not in exclude_cols and 
                           df[col].nunique() > 10]  # Only scale continuous variables
            
            if cols_to_scale:
                df[cols_to_scale] = self.scaler.fit_transform(df[cols_to_scale])
                logger.info(f"Scaled {len(cols_to_scale)} numerical columns (excluding target variables)")
            
            return df
            
        except Exception as e:
            logger.error(f"Error scaling numerical features: {str(e)}")
            return df
    
    def format_timeseries(self, df):
        """Format data as time series"""
        try:
            # Ensure date column exists and is datetime
            if 'date' not in df.columns:
                if 'index' in df.columns:
                    df['date'] = pd.to_datetime(df['index'])
                else:
                    df['date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
            else:
                df['date'] = pd.to_datetime(df['date'])
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            # Create demand column if not exists (sales = demand for simplicity)
            if 'demand' not in df.columns:
                df['demand'] = df.get('sales', df.get('quantity', 100))
            
            # Set date as index for time series operations
            df.set_index('date', inplace=False)
            
            logger.info("Time series formatting complete")
            return df
            
        except Exception as e:
            logger.error(f"Error formatting time series: {str(e)}")
            raise
    
    def create_train_test_split(self, df, test_size=0.2):
        """
        Create train/test split for time series data
        
        Args:
            df: Preprocessed DataFrame
            test_size: Proportion of data for testing
            
        Returns:
            tuple: (train_df, test_df, split_info)
        """
        try:
            # For time series, we use the last portion for testing
            split_idx = int(len(df) * (1 - test_size))
            
            train_df = df.iloc[:split_idx].copy()
            test_df = df.iloc[split_idx:].copy()
            
            split_info = {
                'train_size': len(train_df),
                'test_size': len(test_df),
                'train_start': train_df['date'].min().strftime('%Y-%m-%d'),
                'train_end': train_df['date'].max().strftime('%Y-%m-%d'),
                'test_start': test_df['date'].min().strftime('%Y-%m-%d'),
                'test_end': test_df['date'].max().strftime('%Y-%m-%d')
            }
            
            logger.info(f"Train/test split created: {len(train_df)} train, {len(test_df)} test")
            return train_df, test_df, split_info
            
        except Exception as e:
            logger.error(f"Error creating train/test split: {str(e)}")
            raise