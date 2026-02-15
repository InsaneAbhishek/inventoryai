"""
Module 10: Actionable Insights & Inventory Optimization Module
Provide business recommendations based on forecasts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ActionableInsights:
    """Generate actionable insights and inventory optimization recommendations"""
    
    def __init__(self):
        self.insights_history = []
    
    def generate_insights(self, historical_data, forecast_data):
        """
        Generate comprehensive actionable insights
        
        Args:
            historical_data: Historical sales data
            forecast_data: Forecast predictions
            
        Returns:
            dict: Comprehensive insights
        """
        try:
            logger.info("Generating actionable insights")
            
            insights = {}
            
            # ABC Analysis
            insights['abc_analysis'] = self.perform_abc_analysis(historical_data)
            
            # Reorder Points
            insights['reorder_points'] = self.calculate_reorder_points(forecast_data)
            
            # Inventory Optimization
            insights['optimization'] = self.optimize_inventory(historical_data, forecast_data)
            
            # Business Recommendations
            insights['recommendations'] = self.generate_recommendations(
                historical_data,
                forecast_data,
                insights
            )
            
            # Summary
            insights['optimization_summary'] = self.create_optimization_summary(insights)
            
            # Store insights history
            self.insights_history.append({
                'timestamp': datetime.now().isoformat(),
                'insights': insights
            })
            
            logger.info("Insights generated successfully")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise
    
    def perform_abc_analysis(self, data):
        """
        Perform ABC Analysis to categorize products by importance
        
        Args:
            data: Historical sales data
            
        Returns:
            dict: ABC analysis results
        """
        try:
            # Aggregate sales by product
            if 'product_id' in data.columns:
                product_sales = data.groupby('product_id').agg({
                    'sales': 'sum' if 'sales' in data.columns else 'count',
                    'price': 'first' if 'price' in data.columns else lambda x: 50
                }).reset_index()
                
                product_sales['revenue'] = product_sales['sales'] * product_sales['price']
                
                # Sort by revenue
                product_sales = product_sales.sort_values('revenue', ascending=False)
                
                # Calculate cumulative percentage
                product_sales['cumulative_revenue'] = product_sales['revenue'].cumsum()
                product_sales['total_revenue'] = product_sales['revenue'].sum()
                product_sales['cumulative_pct'] = (
                    product_sales['cumulative_revenue'] / product_sales['total_revenue'] * 100
                )
                
                # Assign ABC categories
                product_sales['category'] = 'C'
                product_sales.loc[product_sales['cumulative_pct'] <= 80, 'category'] = 'A'
                product_sales.loc[
                    (product_sales['cumulative_pct'] > 80) & 
                    (product_sales['cumulative_pct'] <= 95), 
                    'category'
                ] = 'B'
                
                # Calculate category statistics
                category_stats = product_sales.groupby('category').agg({
                    'product_id': 'count',
                    'revenue': 'sum'
                }).rename(columns={'product_id': 'product_count'})
                
                category_stats['revenue_pct'] = (
                    category_stats['revenue'] / product_sales['revenue'].sum() * 100
                )
                
                return {
                    'product_classification': product_sales.to_dict('records'),
                    'category_summary': category_stats.to_dict(),
                    'recommendations': {
                        'A': 'High priority items - maintain tight inventory control, frequent monitoring',
                        'B': 'Medium priority items - moderate inventory levels, periodic review',
                        'C': 'Low priority items - bulk ordering, less frequent monitoring'
                    }
                }
            
            else:
                # No product data, return default
                return {
                    'product_classification': [],
                    'category_summary': {},
                    'recommendations': {}
                }
            
        except Exception as e:
            logger.error(f"Error in ABC analysis: {str(e)}")
            return {}
    
    def calculate_reorder_points(self, forecast_data):
        """
        Calculate optimal reorder points for each product
        
        Args:
            forecast_data: Forecast predictions
            
        Returns:
            dict: Reorder point calculations
        """
        try:
            # Calculate daily demand statistics
            daily_demand = forecast_data['predicted_demand']
            
            # Calculate safety stock (using standard deviation)
            demand_std = daily_demand.std()
            lead_time = 7  # days
            service_level = 1.65  # 95% service level
            
            safety_stock = demand_std * np.sqrt(lead_time) * service_level
            
            # Calculate lead time demand
            lead_time_demand = daily_demand.head(lead_time).mean() * lead_time
            
            # Reorder point
            reorder_point = lead_time_demand + safety_stock
            
            # Economic Order Quantity (EOQ)
            annual_demand = daily_demand.sum() * 12
            holding_cost_rate = 0.2
            ordering_cost = 50
            unit_cost = 50
            
            holding_cost = unit_cost * holding_cost_rate
            eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
            
            # Order frequency
            order_frequency = annual_demand / eoq if eoq > 0 else 0
            
            return {
                'reorder_point': float(reorder_point),
                'safety_stock': float(safety_stock),
                'lead_time_demand': float(lead_time_demand),
                'economic_order_quantity': float(eoq),
                'order_frequency_days': float(365 / order_frequency) if order_frequency > 0 else 0,
                'annual_cost': float(annual_demand * unit_cost),
                'holding_cost_annual': float(eoq / 2 * holding_cost),
                'ordering_cost_annual': float(order_frequency * ordering_cost),
                'total_annual_cost': float(
                    (eoq / 2 * holding_cost) + (order_frequency * ordering_cost)
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating reorder points: {str(e)}")
            return {}
    
    def optimize_inventory(self, historical_data, forecast_data):
        """
        Generate inventory optimization recommendations
        
        Args:
            historical_data: Historical sales data
            forecast_data: Forecast predictions
            
        Returns:
            dict: Optimization recommendations
        """
        try:
            # Analyze demand patterns
            forecast_summary = {
                'total_forecast': float(forecast_data['predicted_demand'].sum()),
                'average_daily': float(forecast_data['predicted_demand'].mean()),
                'peak_demand': float(forecast_data['predicted_demand'].max()),
                'min_demand': float(forecast_data['predicted_demand'].min()),
                'demand_volatility': float(forecast_data['predicted_demand'].std())
            }
            
            # Identify trends
            first_week = forecast_data['predicted_demand'].head(7).mean()
            last_week = forecast_data['predicted_demand'].tail(7).mean()
            trend = (last_week - first_week) / first_week * 100
            
            # Seasonal patterns
            monthly_demand = forecast_data.groupby(
                forecast_data['date'].dt.month
            )['predicted_demand'].mean()
            
            # Optimization recommendations
            if forecast_summary['demand_volatility'] > 50:
                volatility_recommendation = "High volatility detected - increase safety stock by 20%"
            elif forecast_summary['demand_volatility'] > 30:
                volatility_recommendation = "Moderate volatility - maintain standard safety stock"
            else:
                volatility_recommendation = "Low volatility - can reduce safety stock by 10%"
            
            if trend > 10:
                trend_recommendation = "Upward trend - increase inventory levels by 15%"
            elif trend < -10:
                trend_recommendation = "Downward trend - reduce inventory levels by 15%"
            else:
                trend_recommendation = "Stable trend - maintain current inventory levels"
            
            return {
                'forecast_summary': forecast_summary,
                'demand_trend': float(trend),
                'trend_direction': 'increasing' if trend > 5 else 'decreasing' if trend < -5 else 'stable',
                'volatility_level': 'high' if forecast_summary['demand_volatility'] > 50 else 'medium' if forecast_summary['demand_volatility'] > 30 else 'low',
                'recommendations': {
                    'volatility': volatility_recommendation,
                    'trend': trend_recommendation,
                    'general': "Monitor forecast accuracy weekly and adjust inventory levels accordingly"
                },
                'monthly_pattern': monthly_demand.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error in inventory optimization: {str(e)}")
            return {}
    
    def generate_recommendations(self, historical_data, forecast_data, insights):
        """
        Generate actionable business recommendations
        
        Args:
            historical_data: Historical sales data
            forecast_data: Forecast predictions
            insights: Generated insights
            
        Returns:
            list: Actionable recommendations
        """
        try:
            recommendations = []
            
            # Reorder point recommendation
            reorder_point = insights.get('reorder_points', {}).get('reorder_point', 0)
            if reorder_point > 0:
                recommendations.append({
                    'priority': 'high',
                    'category': 'inventory',
                    'title': 'Set Reorder Point',
                    'description': f'Configure reorder alert at {reorder_point:.0f} units to prevent stockouts',
                    'action': 'Update inventory management system with new reorder point',
                    'expected_impact': 'Reduce stockouts by 95%'
                })
            
            # Safety stock recommendation
            safety_stock = insights.get('reorder_points', {}).get('safety_stock', 0)
            if safety_stock > 0:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'inventory',
                    'title': 'Maintain Safety Stock',
                    'description': f'Keep {safety_stock:.0f} units as safety stock to handle demand variability',
                    'action': 'Allocate warehouse space for safety stock',
                    'expected_impact': 'Handle unexpected demand spikes'
                })
            
            # ABC Analysis recommendation
            abc_analysis = insights.get('abc_analysis', {})
            if abc_analysis:
                recommendations.append({
                    'priority': 'high',
                    'category': 'classification',
                    'title': 'Implement ABC Analysis',
                    'description': 'Prioritize management attention based on product importance',
                    'action': 'Review A-category items weekly, B-category bi-weekly, C-category monthly',
                    'expected_impact': 'Optimize inventory management resources'
                })
            
            # EOQ recommendation
            eoq = insights.get('reorder_points', {}).get('economic_order_quantity', 0)
            if eoq > 0:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'ordering',
                    'title': 'Optimize Order Quantity',
                    'description': f'Use economic order quantity of {eoq:.0f} units to minimize costs',
                    'action': 'Update ordering policies with calculated EOQ',
                    'expected_impact': 'Reduce total inventory costs by 15-20%'
                })
            
            # Trend-based recommendation
            optimization = insights.get('optimization', {})
            if optimization.get('trend_direction') == 'increasing':
                recommendations.append({
                    'priority': 'high',
                    'category': 'planning',
                    'title': 'Prepare for Increased Demand',
                    'description': f'Demand is trending upward by {optimization.get("demand_trend", 0):.1f}%',
                    'action': 'Increase inventory levels and secure additional supplier capacity',
                    'expected_impact': 'Meet growing demand without stockouts'
                })
            
            # Volatility recommendation
            if optimization.get('volatility_level') == 'high':
                recommendations.append({
                    'priority': 'high',
                    'category': 'risk',
                    'title': 'Manage High Volatility',
                    'description': 'Demand volatility is high - implement demand buffering strategies',
                    'action': 'Increase safety stock and improve forecast accuracy with more data',
                    'expected_impact': 'Reduce stockout risk during demand spikes'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def create_optimization_summary(self, insights):
        """
        Create a summary of optimization insights
        
        Args:
            insights: All generated insights
            
        Returns:
            dict: Optimization summary
        """
        try:
            summary = {
                'total_recommendations': len(insights.get('recommendations', [])),
                'high_priority': len([r for r in insights.get('recommendations', []) if r.get('priority') == 'high']),
                'medium_priority': len([r for r in insights.get('recommendations', []) if r.get('priority') == 'medium']),
                'low_priority': len([r for r in insights.get('recommendations', []) if r.get('priority') == 'low']),
                'categories': {
                    'inventory': len([r for r in insights.get('recommendations', []) if r.get('category') == 'inventory']),
                    'ordering': len([r for r in insights.get('recommendations', []) if r.get('category') == 'ordering']),
                    'planning': len([r for r in insights.get('recommendations', []) if r.get('category') == 'planning']),
                    'risk': len([r for r in insights.get('recommendations', []) if r.get('category') == 'risk'])
                },
                'key_metrics': {
                    'reorder_point': insights.get('reorder_points', {}).get('reorder_point', 0),
                    'safety_stock': insights.get('reorder_points', {}).get('safety_stock', 0),
                    'economic_order_quantity': insights.get('reorder_points', {}).get('economic_order_quantity', 0),
                    'demand_trend': insights.get('optimization', {}).get('demand_trend', 0)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating optimization summary: {str(e)}")
            return {}
    
    def generate_report(self, processed_data, trained_models, report_type='forecast'):
        """
        Generate a comprehensive report
        
        Args:
            processed_data: All processed data
            trained_models: Trained models
            report_type: Type of report ('forecast', 'evaluation', 'optimization')
            
        Returns:
            str: Path to generated report file
        """
        try:
            import os
            
            # Create reports directory
            os.makedirs('../reports', exist_ok=True)
            
            # Generate report content
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f'../reports/{report_type}_report_{timestamp}.txt'
            
            with open(report_filename, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write(f"INVENTORY DEMAND FORECASTING REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Report Type: {report_type.upper()}\n")
                f.write("=" * 80 + "\n\n")
                
                # Data summary
                f.write("DATA SUMMARY\n")
                f.write("-" * 40 + "\n")
                if 'raw' in processed_data:
                    f.write(f"Historical Records: {len(processed_data['raw'])}\n")
                if 'forecast' in processed_data:
                    forecast = processed_data['forecast']['predictions']
                    f.write(f"Forecast Horizon: {len(forecast)} days\n")
                    f.write(f"Total Forecasted Demand: {forecast['predicted_demand'].sum():.0f}\n")
                    f.write(f"Average Daily Demand: {forecast['predicted_demand'].mean():.0f}\n")
                    f.write(f"Peak Demand: {forecast['predicted_demand'].max():.0f}\n")
                f.write("\n")
                
                # Model information
                f.write("MODELS TRAINED\n")
                f.write("-" * 40 + "\n")
                for model_name in trained_models.keys():
                    f.write(f"- {model_name}\n")
                f.write("\n")
                
                # Key recommendations
                f.write("KEY RECOMMENDATIONS\n")
                f.write("-" * 40 + "\n")
                f.write("1. Implement the calculated reorder points to prevent stockouts\n")
                f.write("2. Maintain appropriate safety stock levels\n")
                f.write("3. Monitor forecasts weekly and adjust as needed\n")
                f.write("4. Use ABC analysis to prioritize inventory management\n")
                f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"Report generated: {report_filename}")
            return report_filename
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise