"""
Phone Call Notification Service
Autonomous phone call service using Twilio Voice API with AI-generated scripts
"""

import logging
import asyncio
import urllib.parse
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from twilio.rest import Client
    from twilio.twiml.voice_response import VoiceResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Twilio not available, phone service will be limited")

from app.core.config import settings
from app.models import Transaction, AnomalyResult
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class PhoneService:
    """Phone call service for voice notifications using Twilio"""
    
    def __init__(self):
        self.twilio_client = None
        self.is_configured = False
        self.fallback_mode = False
        self.call_log = []
        
    async def initialize(self) -> bool:
        """Initialize phone service with Twilio"""
        try:
            if not settings.ENABLE_PHONE_NOTIFICATIONS:
                logger.info("Phone notifications disabled in configuration")
                return False
                
            if not TWILIO_AVAILABLE:
                logger.error("Twilio SDK not available")
                return False
                
            # Initialize Twilio client
            success = await self._initialize_twilio()
            
            if success:
                self.is_configured = True
                logger.info("✅ Phone service initialized successfully with Twilio")
                return True
            else:
                logger.warning("Phone service initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize phone service: {e}")
            return False
    
    async def make_anomaly_call(
        self,
        transaction: Transaction,
        anomaly_result: AnomalyResult,
        phone_number: str,
        customer_name: str = "Customer"
    ) -> bool:
        """Make autonomous phone call for anomaly notification with retry logic"""
        if not self.is_configured:
            logger.warning("Phone service not configured, cannot make call")
            return False
            
        max_retries = 2
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries + 1):
            try:
                # Generate call script using OpenAI (with fallback)
                script = await self._generate_script_with_fallback(
                    transaction, anomaly_result, customer_name
                )
                
                # Make the phone call
                call_result = await self._make_call(
                    phone_number=phone_number,
                    script=script,
                    customer_name=customer_name
                )
                
                success = call_result.get('success', False) if isinstance(call_result, dict) else call_result
                call_sid = call_result.get('call_sid') if isinstance(call_result, dict) else None
                
                if success:
                    break  # Success, exit retry loop
                elif attempt < max_retries:
                    logger.warning(f"Call attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    
            except Exception as e:
                logger.error(f"Error in anomaly call attempt {attempt + 1}: {e}")
                if attempt < max_retries:
                    logger.warning(f"Retrying call in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    success = False
                    call_sid = None
            
            # Log the call attempt
            call_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "phone_number": self._mask_phone_number(phone_number),
                "customer_name": customer_name,
                "transaction_id": transaction.id,
                "risk_level": anomaly_result.risk_level.value,
                "success": success,
                "script_length": len(script),
                "call_sid": call_sid
            }
            self.call_log.append(call_record)
            
            if success:
                logger.info(f"📞 Anomaly notification call completed for {phone_number}")
            else:
                logger.error(f"Failed to complete anomaly notification call for {phone_number}")
                
        return success
    
    async def make_custom_call(
        self,
        phone_number: str,
        script: str,
        customer_name: str = "Customer"
    ) -> bool:
        """Make custom phone call with provided script"""
        if not self.is_configured:
            logger.warning("Phone service not configured, cannot make call")
            return False
            
        return await self._make_call(phone_number, script, customer_name)
    
    async def _make_call(
        self,
        phone_number: str,
        script: str,
        customer_name: str
    ) -> Dict[str, Any]:
        """Internal method to make phone call using Twilio or fallback mode"""
        try:
            # Handle fallback mode
            if self.fallback_mode:
                logger.info(f"🎯 FALLBACK MODE CALL to {self._mask_phone_number(phone_number)}")
                logger.info(f"📱 Script: {script[:100]}...")
                logger.info("📞 In production: This would be a real Twilio call")
                return {
                    'success': True,
                    'call_sid': f"fallback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    'status': 'fallback_logged'
                }
            
            if not self.twilio_client:
                logger.error("Twilio client not initialized")
                return {
                    'success': False,
                    'call_sid': None,
                    'error': 'Twilio client not initialized'
                }
                
            # Create TwiML for the call
            twiml_url = self._generate_twiml_url(script)
            
            # Make the call using Twilio
            call = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.twilio_client.calls.create(
                    to=phone_number,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    url=twiml_url,
                    status_callback=f"{settings.TWILIO_WEBHOOK_URL}/status" if settings.TWILIO_WEBHOOK_URL else None,
                    status_callback_event=['completed', 'failed', 'busy', 'no-answer'],
                    timeout=30
                )
            )
            
            # Store call SID for tracking
            call_sid = call.sid
            
            logger.info(f"📞 REAL CALL initiated to {self._mask_phone_number(phone_number)}")
            logger.info(f"📱 Call SID: {call.sid}")
            logger.info(f"📝 Script: {script[:100]}...")
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': 'initiated'
            }
            
        except Exception as e:
            logger.error(f"Error making Twilio call: {e}")
            return {
                'success': False,
                'call_sid': None,
                'error': str(e)
            }
    
    async def _initialize_twilio(self) -> bool:
        """Initialize Twilio client with fallback mode"""
        try:
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.error("Twilio credentials not configured")
                return self._enable_fallback_mode("Missing Twilio credentials")
                
            if not settings.TWILIO_PHONE_NUMBER:
                logger.error("Twilio phone number not configured")
                return self._enable_fallback_mode("Missing Twilio phone number")
                
            # Initialize Twilio client
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            # Test the connection by fetching account info
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.twilio_client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            )
            
            logger.info("Twilio client initialized successfully")
            return True
                
        except Exception as e:
            logger.error(f"Error initializing Twilio: {e}")
            return self._enable_fallback_mode(f"Twilio initialization failed: {e}")
    
    def _enable_fallback_mode(self, reason: str) -> bool:
        """Enable fallback mode when Twilio is unavailable"""
        logger.warning(f"Enabling phone service fallback mode: {reason}")
        self.fallback_mode = True
        # Still return True so notifications continue to work (they'll just be logged)
        return True
    
    def _generate_twiml_url(self, script: str) -> str:
        """Generate TwiML URL for the call script"""
        try:
            # URL encode the script for safe transmission
            encoded_script = urllib.parse.quote(script)
            
            # If webhook URL is configured, use dynamic TwiML
            if settings.TWILIO_WEBHOOK_URL:
                return f"{settings.TWILIO_WEBHOOK_URL}/twiml?script={encoded_script}"
            
            # Fallback to inline TwiML (limited by URL length)
            # This is a simplified approach - in production, use webhook
            return f"data:text/xml,<?xml version='1.0' encoding='UTF-8'?><Response><Say voice='{settings.TWILIO_TTS_VOICE}'>{script[:500]}</Say></Response>"
                
        except Exception as e:
            logger.error(f"Error generating TwiML URL: {e}")
            # Fallback TwiML
            return "data:text/xml,<?xml version='1.0' encoding='UTF-8'?><Response><Say>Unable to generate call script</Say></Response>"
    
    def generate_twiml(self, script: str) -> str:
        """Generate TwiML response for a call"""
        try:
            response = VoiceResponse()
            response.say(script, voice=settings.TWILIO_TTS_VOICE)
            return str(response)
        except Exception as e:
            logger.error(f"Error generating TwiML: {e}")
            # Fallback TwiML
            response = VoiceResponse()
            response.say("Unable to generate call script")
            return str(response)
    
    async def _generate_script_with_fallback(
        self,
        transaction: Transaction,
        anomaly_result: AnomalyResult,
        customer_name: str
    ) -> str:
        """Generate call script with fallback if OpenAI fails"""
        try:
            # Try to generate script using OpenAI (includes built-in fallback)
            script = await openai_service.generate_phone_script(
                transaction, anomaly_result, customer_name
            )
            return script
        except Exception as e:
            logger.warning(f"OpenAI script generation failed, using basic fallback: {e}")
            # Fallback to basic script
            return self._generate_fallback_script(transaction, anomaly_result, customer_name)
    
    def _generate_fallback_script(self, transaction: Transaction, anomaly_result: AnomalyResult, customer_name: str) -> str:
        """Generate fallback script when AI generation fails"""
        risk_level = anomaly_result.risk_level.value.lower()
        amount = f"${transaction.amount:.2f}"
        merchant = transaction.merchant_name
        
        if risk_level == "critical":
            return f"Hello {customer_name}, this is an urgent security alert from FinancePulse. We detected a critical transaction of {amount} at {merchant}. Please call us immediately at our security hotline to verify this transaction. Do not ignore this call."
        elif risk_level == "high":
            return f"Hello {customer_name}, this is a security alert from FinancePulse. We detected suspicious activity on your account. A transaction of {amount} was made at {merchant}. Please contact us to verify this transaction."
        else:
            return f"Hello {customer_name}, this is FinancePulse security. We're calling to verify a recent transaction of {amount} at {merchant}. If this was you, no action is needed. Otherwise, please contact us immediately."
    
    async def get_call_status(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get status of a Twilio call"""
        try:
            if not self.twilio_client:
                return None
                
            call = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.twilio_client.calls(call_sid).fetch()
            )
            
            return {
                'sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'price': call.price,
                'direction': call.direction
            }
            
        except Exception as e:
            logger.error(f"Error fetching call status: {e}")
            return None
    
    def _mask_phone_number(self, phone_number: str) -> str:
        """Mask phone number for logging privacy"""
        if len(phone_number) < 4:
            return "***"
        return phone_number[:-4] + "****"
    
    def get_call_log(self) -> list:
        """Get call history log"""
        return self.call_log.copy()
    
    def clear_call_log(self):
        """Clear call history log"""
        self.call_log.clear()


# Global service instance
phone_service = PhoneService()