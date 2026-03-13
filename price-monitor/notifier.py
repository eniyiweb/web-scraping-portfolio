"""
Notification module
Send price alerts via email and webhooks
"""
import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


class PriceNotifier:
    """Send notifications when prices change"""
    
    def __init__(self):
        self.email_enabled = all([
            os.getenv('EMAIL_SMTP'),
            os.getenv('EMAIL_USER'),
            os.getenv('EMAIL_PASS')
        ])
        self.webhook_url = os.getenv('WEBHOOK_URL')
    
    def send_price_alert(self, product):
        """Send alert when price drops"""
        message = self._format_message(product)
        
        # Send email notification
        if self.email_enabled:
            self._send_email(product, message)
        
        # Send webhook notification
        if self.webhook_url:
            self._send_webhook(product, message)
        
        # Always print to console
        print(f"\n🚨 PRICE ALERT:\n{message}\n")
    
    def _format_message(self, product) -> str:
        """Format alert message"""
        old_price = product.previous_price
        new_price = product.current_price
        change_pct = product.price_change_percent()
        
        return f"""
🎉 PRICE DROP ALERT!

Product: {product.name}
Old Price: ${old_price:.2f}
New Price: ${new_price:.2f}
Change: {change_pct:.1f}%

Check it out: {product.url}
"""
    
    def _send_email(self, product, message: str):
        """Send email notification"""
        try:
            smtp_server = os.getenv('EMAIL_SMTP')
            smtp_port = int(os.getenv('EMAIL_PORT', '587'))
            sender_email = os.getenv('EMAIL_USER')
            sender_password = os.getenv('EMAIL_PASS')
            recipient = os.getenv('ALERT_EMAIL', sender_email)
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = f"🎉 Price Drop: {product.name}"
            
            msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"   📧 Email sent to {recipient}")
            
        except Exception as e:
            print(f"   ⚠️ Email failed: {e}")
    
    def _send_webhook(self, product, message: str):
        """Send webhook notification (e.g., Slack, Discord)"""
        try:
            payload = {
                'text': message,
                'product': {
                    'name': product.name,
                    'price': product.current_price,
                    'url': product.url
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            print(f"   🔗 Webhook sent")
            
        except Exception as e:
            print(f"   ⚠️ Webhook failed: {e}")
