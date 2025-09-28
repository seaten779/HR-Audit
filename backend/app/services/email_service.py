"""
Email Notification Service
Handles SMTP email sending for anomaly notifications
"""

import logging
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.core.config import settings
from app.models import Transaction, AnomalyResult
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP email service for sending anomaly notifications"""
    
    def __init__(self):
        self.smtp_server = None
        self.is_configured = False
        
    async def initialize(self) -> bool:
        """Initialize email service and test connection"""
        try:
            if not settings.ENABLE_EMAIL_NOTIFICATIONS:
                logger.info("Email notifications disabled in configuration")
                return False
                
            if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
                logger.warning("SMTP credentials not configured, email service unavailable")
                return False
                
            # Test SMTP connection
            await self._test_smtp_connection()
            self.is_configured = True
            logger.info("✅ Email service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize email service: {e}")
            return False
    
    async def send_anomaly_notification(
        self,
        transaction: Transaction,
        anomaly_result: AnomalyResult,
        recipient_email: str,
        customer_name: str = "Customer"
    ) -> bool:
        """Send anomaly notification email"""
        if not self.is_configured:
            logger.warning("Email service not configured, cannot send notification")
            return False
            
        try:
            # Generate email content using OpenAI (with fallback)
            subject, body = await openai_service.generate_email_content(
                transaction, anomaly_result, customer_name
            )
            
            # Send the email
            success = await self._send_email(
                to_email=recipient_email,
                subject=subject,
                body=body,
                is_html=False
            )
            
            if success:
                logger.info(f"📧 ✅ ALERT EMAIL SENT to {recipient_email} | Customer: {customer_name} | Subject: {subject[:50]}...")
                # Log for frontend notification popup
                logger.info(f"FRONTEND_NOTIFICATION: Email sent to {customer_name} ({recipient_email})")
            else:
                logger.error(f"❌ Failed to send anomaly notification email to {recipient_email}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending anomaly notification email: {e}")
            return False
    
    async def send_custom_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send custom email"""
        if not self.is_configured:
            logger.warning("Email service not configured, cannot send email")
            return False
            
        return await self._send_email(to_email, subject, body, is_html, attachments)
    
    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Internal method to send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            
            # Add body
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    # This could be extended to handle file attachments
                    pass
            
            # Send email in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self._smtp_send, msg, to_email
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error in _send_email: {e}")
            return False
    
    def _smtp_send(self, msg: MIMEMultipart, to_email: str):
        """Synchronous SMTP send operation"""
        smtp = None
        try:
            # Create SMTP connection
            smtp = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            smtp.ehlo()
            
            # Start TLS encryption
            if settings.SMTP_PORT == 587:
                smtp.starttls()
                smtp.ehlo()
            
            # Login
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            # Send email
            smtp.send_message(msg, settings.EMAIL_FROM, [to_email])
            
        finally:
            if smtp:
                smtp.quit()
    
    async def _test_smtp_connection(self):
        """Test SMTP connection and authentication"""
        def test_connection():
            smtp = None
            try:
                smtp = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
                smtp.ehlo()
                
                if settings.SMTP_PORT == 587:
                    smtp.starttls()
                    smtp.ehlo()
                
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                return True
                
            except Exception as e:
                raise Exception(f"SMTP connection test failed: {e}")
            finally:
                if smtp:
                    smtp.quit()
        
        # Run test in executor
        await asyncio.get_event_loop().run_in_executor(None, test_connection)
    
    def get_email_template(self, template_type: str) -> Dict[str, str]:
        """Get predefined email templates"""
        templates = {
            "high_risk_anomaly": {
                "subject": "🚨 HIGH RISK Transaction Alert - Immediate Action Required",
                "body": """
Dear {customer_name},

URGENT: We've detected HIGH RISK suspicious activity on your account.

TRANSACTION DETAILS:
• Amount: {amount}
• Merchant: {merchant}  
• Date: {timestamp}
• Risk Score: {confidence}%

IMMEDIATE ACTIONS REQUIRED:
1. Call us immediately at 1-800-FINANCE
2. Do not use your card until we verify your identity
3. Check your account for other unauthorized transactions

If you authorized this transaction, please disregard this alert.

This is an automated security notification.

FinancePulse Security Team
""",
            },
            "medium_risk_anomaly": {
                "subject": "⚠️ Transaction Security Alert - Please Review",
                "body": """
Dear {customer_name},

We've detected unusual activity on your account that requires your attention.

TRANSACTION DETAILS:
• Amount: {amount}
• Merchant: {merchant}
• Date: {timestamp}

Please log into your account to review this transaction. If you did not authorize it, contact us at 1-800-FINANCE.

Your security is our priority.

FinancePulse Security Team
""",
            }
        }
        
        return templates.get(template_type, {})


# Global service instance
email_service = EmailService()