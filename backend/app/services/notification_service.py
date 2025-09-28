"""
Notification Orchestrator Service
Main service that coordinates email and phone notifications for anomaly detection
"""

import logging
import asyncio
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from app.core.config import settings
from app.models import (
    Transaction, AnomalyResult, RiskLevel, 
    CustomerContact, NotificationRecord, NotificationSettings,
    NotificationType, NotificationStatus
)
from app.services.openai_service import openai_service
from app.services.email_service import email_service
from app.services.phone_service import phone_service
from app.services.financepulse_voice_service import financepulse_voice_service

logger = logging.getLogger(__name__)


class NotificationOrchestrator:
    """Main notification orchestrator service"""
    
    def __init__(self):
        self.notification_history: List[NotificationRecord] = []
        self.customer_contacts: Dict[str, CustomerContact] = {}
        self.customer_settings: Dict[str, NotificationSettings] = {}
        self.notification_cooldowns: Dict[str, datetime] = {}
        self.daily_notification_counts: Dict[str, Dict[str, int]] = {}
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize notification orchestrator and all services"""
        try:
            logger.info("🔔 Initializing notification orchestrator...")
            
            # Initialize all services
            services_status = {}
            
            # Initialize OpenAI service
            services_status['openai'] = await openai_service.initialize()
            
            # Initialize email service
            services_status['email'] = await email_service.initialize()
            
            # Initialize phone service
            services_status['phone'] = await phone_service.initialize()
            
            # Initialize integrated voice service
            services_status['voice'] = await financepulse_voice_service.initialize()
            
            # Load mock customer data
            await self._load_mock_customer_data()
            
            self.is_initialized = True
            
            # Log service status
            for service, status in services_status.items():
                status_emoji = "✅" if status else "❌"
                logger.info(f"{status_emoji} {service.title()} service: {'Ready' if status else 'Failed'}")
            
            logger.info("✅ Notification orchestrator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize notification orchestrator: {e}")
            return False
    
    async def process_anomaly_notification(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult
    ) -> Dict[str, bool]:
        """
        Process anomaly and send appropriate notifications
        Returns dict with notification results
        """
        if not self.is_initialized:
            logger.warning("Notification orchestrator not initialized")
            return {"email": False, "phone": False}
        
        results = {"email": False, "phone": False}
        
        try:
            # Get customer contact information
            customer_contact = self.customer_contacts.get(transaction.customer_id)
            if not customer_contact:
                logger.warning(f"No contact information found for customer {transaction.customer_id}")
                return results
            
            # Get customer notification settings
            settings_key = transaction.customer_id
            customer_settings = self.customer_settings.get(
                settings_key,
                NotificationSettings(customer_id=transaction.customer_id)
            )
            
            # Check if notifications should be sent based on risk level
            should_email = self._should_send_email(anomaly_result, customer_contact, customer_settings)
            should_phone = self._should_send_phone(anomaly_result, customer_contact, customer_settings)
            
            # Check cooldown periods
            if self._is_in_cooldown(transaction.customer_id):
                logger.info(f"Customer {transaction.customer_id} is in notification cooldown")
                return results
            
            # Check daily limits
            if self._exceeds_daily_limit(transaction.customer_id, customer_settings):
                logger.info(f"Customer {transaction.customer_id} has exceeded daily notification limit")
                return results
            
            # Send notifications
            notification_tasks = []
            
            if should_email:
                notification_tasks.append(
                    self._send_email_notification(
                        transaction, anomaly_result, customer_contact
                    )
                )
            
            if should_phone:
                notification_tasks.append(
                    self._send_phone_notification(
                        transaction, anomaly_result, customer_contact
                    )
                )
            
            # Execute notifications concurrently
            if notification_tasks:
                notification_results = await asyncio.gather(*notification_tasks, return_exceptions=True)
                
                # Process results
                if should_email:
                    results["email"] = isinstance(notification_results[0], bool) and notification_results[0]
                if should_phone:
                    phone_index = 1 if should_email else 0
                    if phone_index < len(notification_results):
                        results["phone"] = isinstance(notification_results[phone_index], bool) and notification_results[phone_index]
                
                # Update cooldown and daily counts
                if any(results.values()):
                    self._update_cooldown(transaction.customer_id)
                    self._increment_daily_count(transaction.customer_id)
            
            # Log results
            sent_methods = [method for method, success in results.items() if success]
            if sent_methods:
                logger.info(f"📢 Sent {anomaly_result.risk_level.value} risk notifications via {', '.join(sent_methods)} to customer {transaction.customer_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing anomaly notification: {e}")
            return results
    
    async def _send_email_notification(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult, 
        customer_contact: CustomerContact
    ) -> bool:
        """Send email notification"""
        try:
            if not customer_contact.email:
                logger.warning(f"No email address for customer {customer_contact.customer_id}")
                return False
            
            success = await email_service.send_anomaly_notification(
                transaction=transaction,
                anomaly_result=anomaly_result,
                recipient_email=customer_contact.email,
                customer_name=customer_contact.name
            )
            
            # Log notification record
            await self._log_notification_record(
                customer_contact.customer_id,
                transaction.id,
                NotificationType.EMAIL,
                customer_contact.email,
                anomaly_result.risk_level,
                success
            )
            
            # Broadcast email notification to frontend if successful
            if success:
                await self._broadcast_notification_popup({
                    "type": "email_notification",
                    "message": f"🔔 Security Alert Email sent to {customer_contact.name}",
                    "customer_id": customer_contact.customer_id,
                    "customer_name": customer_contact.name,
                    "email": customer_contact.email,
                    "risk_level": anomaly_result.risk_level.value,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return False
    
    async def _send_phone_notification(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult, 
        customer_contact: CustomerContact
    ) -> bool:
        """Send phone notification using integrated voice service"""
        try:
            if not customer_contact.phone:
                logger.warning(f"No phone number for customer {customer_contact.customer_id}")
                return False
            
            # Use the new integrated voice service for fraud alert calls
            call_result = await financepulse_voice_service.make_fraud_alert_call(
                phone_number=customer_contact.phone,
                customer_name=customer_contact.name,
                transaction=transaction,
                anomaly_result=anomaly_result
            )
            
            success = call_result.get('success', False)
            
            # Log notification record
            await self._log_notification_record(
                customer_contact.customer_id,
                transaction.id,
                NotificationType.PHONE,
                customer_contact.phone,
                anomaly_result.risk_level,
                success
            )
            
            # Broadcast phone notification to frontend if successful
            if success:
                await self._broadcast_notification_popup({
                    "type": "voice_call_notification",
                    "message": f"📞 Fraud Alert Call made to {customer_contact.name}",
                    "customer_id": customer_contact.customer_id,
                    "customer_name": customer_contact.name,
                    "phone": customer_contact.phone,
                    "call_sid": call_result.get('call_sid', 'N/A'),
                    "call_provider": call_result.get('provider', 'unknown'),
                    "risk_level": anomaly_result.risk_level.value,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"📞 VOICE CALL SUCCESS: {call_result.get('message', 'Call completed')}")
            else:
                logger.error(f"📞 VOICE CALL FAILED: {call_result.get('error', 'Unknown error')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending voice notification: {e}")
            return False
    
    def _should_send_email(
        self, 
        anomaly_result: AnomalyResult, 
        customer_contact: CustomerContact,
        customer_settings: NotificationSettings
    ) -> bool:
        """Determine if email notification should be sent"""
        if not settings.ENABLE_EMAIL_NOTIFICATIONS:
            return False
        
        if not customer_contact.email_notifications_enabled:
            return False
        
        if not customer_settings.email_enabled:
            return False
        
        # Check risk level threshold
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        email_threshold_index = risk_levels.index(customer_settings.email_threshold)
        anomaly_risk_index = risk_levels.index(anomaly_result.risk_level)
        
        return anomaly_risk_index >= email_threshold_index
    
    def _should_send_phone(
        self, 
        anomaly_result: AnomalyResult, 
        customer_contact: CustomerContact,
        customer_settings: NotificationSettings
    ) -> bool:
        """Determine if phone notification should be sent"""
        if not settings.ENABLE_PHONE_NOTIFICATIONS:
            return False
        
        if not customer_contact.phone_notifications_enabled:
            return False
        
        if not customer_settings.phone_enabled:
            return False
        
        # Check quiet hours
        if self._is_quiet_hours(customer_settings):
            logger.info(f"Skipping phone notification due to quiet hours for customer {customer_contact.customer_id}")
            return False
        
        # Check risk level threshold
        risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        phone_threshold_index = risk_levels.index(customer_settings.phone_threshold)
        anomaly_risk_index = risk_levels.index(anomaly_result.risk_level)
        
        return anomaly_risk_index >= phone_threshold_index
    
    def _is_in_cooldown(self, customer_id: str) -> bool:
        """Check if customer is in notification cooldown period"""
        last_notification = self.notification_cooldowns.get(customer_id)
        if not last_notification:
            return False
        
        cooldown_period = timedelta(seconds=settings.NOTIFICATION_COOLDOWN)
        return datetime.utcnow() < last_notification + cooldown_period
    
    def _exceeds_daily_limit(self, customer_id: str, customer_settings: NotificationSettings) -> bool:
        """Check if daily notification limit is exceeded"""
        today = datetime.utcnow().date().isoformat()
        daily_counts = self.daily_notification_counts.get(customer_id, {})
        today_count = daily_counts.get(today, 0)
        
        return today_count >= customer_settings.max_daily_notifications
    
    def _is_quiet_hours(self, customer_settings: NotificationSettings) -> bool:
        """Check if current time is within quiet hours"""
        if not customer_settings.quiet_hours_start or not customer_settings.quiet_hours_end:
            return False
        
        current_hour = datetime.utcnow().hour
        start_hour = customer_settings.quiet_hours_start
        end_hour = customer_settings.quiet_hours_end
        
        if start_hour <= end_hour:
            return start_hour <= current_hour <= end_hour
        else:
            # Quiet hours span midnight
            return current_hour >= start_hour or current_hour <= end_hour
    
    def _update_cooldown(self, customer_id: str):
        """Update notification cooldown for customer"""
        self.notification_cooldowns[customer_id] = datetime.utcnow()
    
    def _increment_daily_count(self, customer_id: str):
        """Increment daily notification count for customer"""
        today = datetime.utcnow().date().isoformat()
        
        if customer_id not in self.daily_notification_counts:
            self.daily_notification_counts[customer_id] = {}
        
        daily_counts = self.daily_notification_counts[customer_id]
        daily_counts[today] = daily_counts.get(today, 0) + 1
    
    async def _log_notification_record(
        self,
        customer_id: str,
        transaction_id: str,
        notification_type: NotificationType,
        recipient: str,
        risk_level: RiskLevel,
        success: bool
    ):
        """Log notification delivery record"""
        try:
            record = NotificationRecord(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                transaction_id=transaction_id,
                notification_type=notification_type,
                status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
                content="Anomaly notification",
                recipient=recipient,
                risk_level=risk_level,
                sent_at=datetime.utcnow() if success else None,
                error_message=None if success else "Failed to send notification"
            )
            
            self.notification_history.append(record)
            
            # Keep only last 1000 records to prevent memory bloat
            if len(self.notification_history) > 1000:
                self.notification_history = self.notification_history[-1000:]
                
        except Exception as e:
            logger.error(f"Error logging notification record: {e}")
    
    async def _load_mock_customer_data(self):
        """Load mock customer contact information and settings"""
        try:
            # Real Gmail addresses for testing
            real_emails = [
                "harisamser27@gmail.com",
                "basyalprashant6@gmail.com", 
                "hellheaven23389@gmail.com",
                "basyalprashant27@gmail.com",
                "aljdoiuhao@gmail.com"
            ]
            
            # Create customer contacts with real Gmail addresses
            mock_customers = []
            for i in range(1, 21):
                # Cycle through the real email addresses
                email_index = (i - 1) % len(real_emails)
                customer_data = {
                    "customer_id": f"customer_{i:03d}",
                    "name": f"Customer {i:03d}",
                    "email": real_emails[email_index],
                    "phone": f"+1-555-{100 + i:04d}",
                    "email_notifications_enabled": True,
                    "phone_notifications_enabled": i % 3 != 0,  # 2/3 of customers enable phone
                    "notification_threshold": RiskLevel.MEDIUM if i % 2 == 0 else RiskLevel.HIGH
                }
                mock_customers.append(customer_data)
            
            # Store customer contacts
            for customer_data in mock_customers:
                customer_id = customer_data["customer_id"]
                contact = CustomerContact(**customer_data)
                self.customer_contacts[customer_id] = contact
                
                # Create default settings
                settings = NotificationSettings(
                    customer_id=customer_id,
                    email_threshold=RiskLevel.LOW,  # Send emails for low risk and above
                    phone_threshold=RiskLevel.HIGH,
                    quiet_hours_start=22,  # 10 PM
                    quiet_hours_end=8      # 8 AM
                )
                self.customer_settings[customer_id] = settings
            
            logger.info(f"📋 Loaded {len(mock_customers)} mock customer profiles")
            
        except Exception as e:
            logger.error(f"Error loading mock customer data: {e}")
    
    # Public API methods
    
    def get_notification_history(self, customer_id: Optional[str] = None, limit: int = 50) -> List[NotificationRecord]:
        """Get notification history"""
        history = self.notification_history
        
        if customer_id:
            history = [record for record in history if record.customer_id == customer_id]
        
        return history[-limit:] if limit else history
    
    def get_customer_contact(self, customer_id: str) -> Optional[CustomerContact]:
        """Get customer contact information"""
        return self.customer_contacts.get(customer_id)
    
    def update_customer_contact(self, customer_id: str, contact_data: dict) -> bool:
        """Update customer contact information"""
        try:
            if customer_id in self.customer_contacts:
                current_contact = self.customer_contacts[customer_id]
                updated_data = current_contact.model_dump()
                updated_data.update(contact_data)
                updated_data['updated_at'] = datetime.utcnow()
                
                self.customer_contacts[customer_id] = CustomerContact(**updated_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating customer contact: {e}")
            return False
    
    def get_customer_settings(self, customer_id: str) -> Optional[NotificationSettings]:
        """Get customer notification settings"""
        return self.customer_settings.get(customer_id)
    
    def update_customer_settings(self, customer_id: str, settings_data: dict) -> bool:
        """Update customer notification settings"""
        try:
            if customer_id in self.customer_settings:
                current_settings = self.customer_settings[customer_id]
                updated_data = current_settings.model_dump()
                updated_data.update(settings_data)
                updated_data['updated_at'] = datetime.utcnow()
                
                self.customer_settings[customer_id] = NotificationSettings(**updated_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating customer settings: {e}")
            return False
    
    async def _broadcast_notification_popup(self, notification_data: dict):
        """Broadcast notification popup to WebSocket clients"""
        try:
            # Import here to avoid circular imports
            from main import websocket_manager
            
            message = {
                "type": "notification_popup",
                "data": notification_data
            }
            
            await websocket_manager.broadcast(message)
            logger.info(f"📱 Notification popup broadcasted: {notification_data['message']}")
            
        except Exception as e:
            logger.error(f"Error broadcasting notification popup: {e}")


# Global service instance
notification_orchestrator = NotificationOrchestrator()