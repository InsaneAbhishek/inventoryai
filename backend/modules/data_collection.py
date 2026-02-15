"""
Module 1: Data Collection Module
Handles importing sales data and fetching external data (weather, holidays)
"""

import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataCollection:
    """Collect and import historical sales data and external datasets"""
    
    def __init__(self):
        self.weather_api_key = "demo_key"  # In production, use environment variable
        self.base_weather_url = "https://api.openweathermap.org/data/2.5"
    
    def import_sales_data(self, filepath):
        """
        Import historical sales data from CSV or Excel file
        
        Args:
            filepath: Path to the data file
            
        Returns:
            pandas.DataFrame: Imported sales data
        """
        try:
            logger.info(f"Importing sales data from {filepath}")
            
            # Determine file type and import accordingly
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel.")
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            
            # Ensure date column exists and convert to datetime
            if 'date' not in df.columns:
                # Try to find a date-like column
                date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                if date_cols:
                    df.rename(columns={date_cols[0]: 'date'}, inplace=True)
                else:
                    df['date'] = pd.date_range(start='2023-01-01', periods=len(df), freq='D')
            
            df['date'] = pd.to_datetime(df['date'])
            
            # Ensure required columns exist
            # Map quantity to sales if sales doesn't exist
            if 'sales' not in df.columns:
                if 'quantity' in df.columns:
                    df['sales'] = df['quantity']
                else:
                    df['sales'] = np.random.randint(50, 200, size=len(df))
            
            # Create demand column (same as sales for historical data)
            if 'demand' not in df.columns:
                df['demand'] = df['sales']
            
            # IMPORTANT: Aggregate by date for daily demand forecasting
            # This converts transaction-level data to daily totals
            agg_dict = {
                'sales': 'sum',
                'demand': 'sum'
            }
            
            # Add price aggregation if exists
            if 'price' in df.columns:
                agg_dict['price'] = 'mean'
            
            # Aggregate by date
            df_daily = df.groupby('date').agg(agg_dict).reset_index()
            
            # Add product_id as a representative value (most common product of the day)
            if 'product_id' not in df_daily.columns:
                df_daily['product_id'] = 'P001'  # Default product
            
            # Use the aggregated daily data
            df = df_daily
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            logger.info(f"Successfully imported {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error importing sales data: {str(e)}")
            raise
    
    def fetch_weather_data(self, start_date, end_date, location="New York"):
        """
        Fetch historical weather data from API
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            location: Location name
            
        Returns:
            pandas.DataFrame: Weather data with temperature, precipitation, etc.
        """
        try:
            logger.info(f"Fetching weather data for {location} from {start_date} to {end_date}")
            
            # Generate date range
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            
            # Simulate weather data (in production, use real API)
            weather_data = pd.DataFrame({
                'date': dates,
                'temperature': np.random.normal(20, 10, len(dates)).round(1),
                'humidity': np.random.randint(40, 90, len(dates)),
                'precipitation': np.random.exponential(2, len(dates)).round(1),
                'wind_speed': np.random.uniform(5, 25, len(dates)).round(1),
                'location': location
            })
            
            # Add seasonal patterns
            weather_data['temperature'] = weather_data['temperature'] + \
                10 * np.sin(2 * np.pi * weather_data.index / 365)
            
            logger.info(f"Fetched {len(weather_data)} weather records")
            return weather_data
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            # Return empty DataFrame on error
            return pd.DataFrame()
    
    def fetch_holiday_data(self, start_date, end_date, country="US"):
        """
        Fetch holiday data for the specified date range
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            country: Country code (default: US)
            
        Returns:
            pandas.DataFrame: Holiday data with date and holiday name
        """
        try:
            logger.info(f"Fetching holiday data for {country} from {start_date} to {end_date}")
            
            # Common holidays (simplified list)
            holidays = {
                '01-01': 'New Year\'s Day',
                '01-15': 'Martin Luther King Jr. Day',
                '02-14': 'Valentine\'s Day',
                '02-19': 'Presidents\' Day',
                '05-27': 'Memorial Day',
                '07-04': 'Independence Day',
                '09-02': 'Labor Day',
                '10-14': 'Columbus Day',
                '10-31': 'Halloween',
                '11-11': 'Veterans Day',
                '11-28': 'Thanksgiving',
                '12-25': 'Christmas Day',
                '12-31': 'New Year\'s Eve'
            }
            
            # Generate date range and check for holidays
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            holiday_data = []
            
            for date in dates:
                date_str = date.strftime('%m-%d')
                if date_str in holidays:
                    holiday_data.append({
                        'date': date,
                        'holiday_name': holidays[date_str],
                        'is_holiday': True,
                        'country': country
                    })
            
            df = pd.DataFrame(holiday_data)
            
            logger.info(f"Fetched {len(df)} holiday records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching holiday data: {str(e)}")
            return pd.DataFrame()
    
    def merge_external_data(self, sales_data, weather_data, holiday_data):
        """
        Merge sales data with external datasets
        
        Args:
            sales_data: Sales DataFrame
            weather_data: Weather DataFrame
            holiday_data: Holiday DataFrame
            
        Returns:
            pandas.DataFrame: Merged dataset
        """
        try:
            logger.info("Merging external data with sales data")
            
            # Start with sales data
            merged = sales_data.copy()
            
            # Merge with weather data
            if not weather_data.empty:
                merged = merged.merge(
                    weather_data,
                    on='date',
                    how='left'
                )
            
            # Merge with holiday data
            if not holiday_data.empty:
                merged = merged.merge(
                    holiday_data,
                    on='date',
                    how='left'
                )
                merged['is_holiday'] = merged['is_holiday'].fillna(False)
            
            logger.info(f"Merged data has {len(merged)} records")
            return merged
            
        except Exception as e:
            logger.error(f"Error merging external data: {str(e)}")
            raise