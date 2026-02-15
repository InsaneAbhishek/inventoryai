"""
Module 9: Notifications & Alerts Module
Send alerts for low inventory conditions
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
# Email imports - using mock implementation for demo
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class Notifications:
    """Generate and send inventory alerts and notifications"""
    
    def __init__(self):
        self.alert_history = []
        self.alert_thresholds = {
            'low_stock': 100,
            'critical_stock': 50,
            'overstock': 500
        }
    
    def configure_alerts(self, config):
        """
        Configure alert settings
        
        Args:
            config: Dictionary with alert configuration
            
        Returns:
            dict: Configuration confirmation
        """
        try:
            self.alert_thresholds = {
                'low_stock': config.get('low_stock_threshold', 100),
                'critical_stock': config.get('critical_stock_threshold', 50),
                'overstock': config.get('overstock_threshold', 500)
            }
            
            self.email_config = {
                'enabled': config.get('email_enabled', False),
                'address': config.get('email_address', ''),
                'smtp_server': config.get('smtp_server', 'smtp.gmail.com'),
                'smtp_port': config.get('smtp_port', 587)
            }
            
            self.sms_config = {
                'enabled': config.get('sms_enabled', False),
                'phone_number': config.get('phone_number', '')
            }
            
            logger.info(f"Alerts configured with thresholds: {self.alert_thresholds}")
            
            return {
                'success': True,
                'thresholds': self.alert_thresholds,
                'email_enabled': self.email_config['enabled'],
                'sms_enabled': self.sms_config['enabled']
            }
            
        except Exception as e:
            logger.error(f"Error configuring alerts: {str(e)}")
            raise
    
    def check_and_send_alerts(self, forecast_data, current_inventory=None):
        """
        Check forecast against thresholds and send alerts
        
        Args:
            forecast_data: DataFrame with forecast predictions
            current_inventory: Current inventory levels (optional)
            
        Returns:
            dict: Alert results
        """
        try:
            logger.info("Checking forecast for alert conditions")
            
            alerts = []
            low_stock_items = []
            
            # Check each forecasted day
            for idx, row in forecast_data.iterrows():
                predicted_demand = row['predicted_demand']
                date = row['date']
                
                # Check against thresholds
                if predicted_demand < self.alert_thresholds['critical_stock']:
                    alert_type = 'critical'
                    message = f"CRITICAL: Predicted demand on {date.strftime('%Y-%m-%d')} is critically low: {predicted_demand:.0f}"
                    alerts.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'type': 'critical',
                        'demand': float(predicted_demand),
                        'message': message
                    })
                    low_stock_items.append(row.to_dict())
                
                elif predicted_demand < self.alert_thresholds['low_stock']:
                    alert_type = 'low'
                    message = f"WARNING: Predicted demand on {date.strftime('%Y-%m-%d')} is below threshold: {predicted_demand:.0f}"
                    alerts.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'type': 'low',
                        'demand': float(predicted_demand),
                        'message': message
                    })
                    low_stock_items.append(row.to_dict())
            
            # Send alerts if any were generated
            alerts_sent = 0
            if alerts:
                # Send email alert if configured
                if self.email_config.get('enabled'):
                    self._send_email_alert(alerts)
                    alerts_sent += 1
                
                # Send SMS alert if configured
                if self.sms_config.get('enabled'):
                    self._send_sms_alert(alerts)
                    alerts_sent += 1
            
            # Store alert history
            self.alert_history.append({
                'timestamp': datetime.now().isoformat(),
                'alerts_count': len(alerts),
                'alerts_sent': alerts_sent,
                'alerts': alerts
            })
            
            logger.info(f"Generated {len(alerts)} alerts, sent {alerts_sent}")
            
            return {
                'alerts_generated': len(alerts),
                'alerts_sent': alerts_sent,
                'low_stock_items': low_stock_items,
                'critical_alerts': len([a for a in alerts if a['type'] == 'critical']),
                'low_alerts': len([a for a in alerts if a['type'] == 'low'])
            }
            
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            raise
    
    def _send_email_alert(self, alerts):
        """Send email notification (mock implementation)"""
        try:
            if not self.email_config.get('enabled') or not self.email_config.get('address'):
                logger.info("Email alerts not configured")
                return
            
            # In production, implement actual email sending
            logger.info(f"Email alert would be sent to {self.email_config['address']} with {len(alerts)} alerts")
            
            # Mock email content
            subject = f"Inventory Alert - {len(alerts)} Issues Detected"
            body = self._format_alert_message(alerts)
            
            # For demonstration, we just log
            logger.info(f"Email Subject: {subject}")
            logger.info(f"Email Body: {body[:200]}...")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
    
    def _send_sms_alert(self, alerts):
        """Send SMS notification (mock implementation)"""
        try:
            if not self.sms_config.get('enabled') or not self.sms_config.get('phone_number'):
                logger.info("SMS alerts not configured")
                return
            
            # In production, use Twilio or similar service
            logger.info(f"SMS alert would be sent to {self.sms_config['phone_number']}")
            
            # Mock SMS content
            critical_count = len([a for a in alerts if a['type'] == 'critical'])
            message = f"Inventory Alert: {critical_count} critical, {len(alerts) - critical_count} low stock items detected."
            
            logger.info(f"SMS Message: {message}")
            
        except Exception as e:
            logger.error(f"Error sending SMS alert: {str(e)}")
    
    def _format_alert_message(self, alerts):
        """Format alerts into a readable message"""
        message = "Inventory Demand Forecasting Alert\n"
        message += "=" * 50 + "\n\n"
        
        # Group by alert type
        critical_alerts = [a for a in alerts if a['type'] == 'critical']
        low_alerts = [a for a in alerts if a['type'] == 'low']
        
        if critical_alerts:
            message += "CRITICAL ALERTS:\n"
            for alert in critical_alerts:
                message += f"  - {alert['date']}: Demand = {alert['demand']:.0f}\n"
            message += "\n"
        
        if low_alerts:
            message += "LOW STOCK ALERTS:\n"
            for alert in low_alerts[:5]:  # Limit to first 5
                message += f"  - {alert['date']}: Demand = {alert['demand']:.0f}\n"
            if len(low_alerts) > 5:
                message += f"  ... and {len(low_alerts) - 5} more\n"
        
        message += "\n" + "=" * 50
        message += "\nPlease review inventory levels and plan accordingly."
        
        return message
    
    def get_alert_history(self, days=30):
        """
        Get alert history for specified period
        
        Args:
            days: Number of days of history to retrieve
            
        Returns:
            list: Alert history
        """
        try:
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            
            recent_history = [
                alert for alert in self.alert_history
                if pd.Timestamp(alert['timestamp']) >= cutoff_date
            ]
            
            return recent_history
            
        except Exception as e:
            logger.error(f"Error getting alert history: {str(e)}")
            return []
    
    def generate_reorder_recommendations(self, forecast_data, lead_time_days=7):
        """
        Generate reorder point recommendations based on forecasts
        
        Args:
            forecast_data: DataFrame with forecast predictions
            lead_time_days: Lead time for orders in days
            
        Returns:
            dict: Reorder recommendations
        """
        try:
            # Calculate demand during lead time
            lead_time_demand = forecast_data['predicted_demand'].head(lead_time_days).sum()
            
            # Add safety stock (20% of lead time demand)
            safety_stock = lead_time_demand * 0.2
            
            # Calculate reorder point
            reorder_point = lead_time_demand + safety_stock
            
            # Calculate economic order quantity (EOQ) - simplified
            annual_demand = forecast_data['predicted_demand'].sum() * 12  # Extrapolate
            holding_cost = 0.2  # 20% of unit value
            ordering_cost = 50  # Fixed cost per order
            
            eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
            
            recommendation = {
                'reorder_point': float(reorder_point),
                'safety_stock': float(safety_stock),
                'lead_time_demand': float(lead_time_demand),
                'economic_order_quantity': float(eoq),
                'recommendation': f"Reorder when inventory falls below {reorder_point:.0f} units",
                'order_quantity': f"Optimal order quantity: {eoq:.0f} units"
            }
            
            logger.info("Reorder recommendations generated")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating reorder recommendations: {str(e)}")
            raise