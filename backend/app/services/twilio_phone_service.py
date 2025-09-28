"""
Enhanced Phone Call Service with Twilio Integration
Real phone calls with AI-generated scripts for fraud alerts
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

try:
    from twilio.rest import Client as TwilioClient
    from twilio.twiml import VoiceResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Twilio not available, phone service will use simulation mode")

from app.core.config import settings
from app.models import Transaction, AnomalyResult, RiskLevel
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class CallStatus(Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered" 
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"


class CallType(Enum):
    FRAUD_ALERT = "fraud_alert"
    SECURITY_NOTIFICATION = "security_notification"
    VERIFICATION_REQUEST = "verification_request"
    ACCOUNT_FREEZE = "account_freeze"
    TEST_CALL = "test_call"


class EnhancedTwilioPhoneService:
    """Enhanced phone service using Twilio for real calls with AI-generated scripts"""
    
    def __init__(self):
        self.client = None
        self.is_configured = False
        self.call_log: List[Dict[str, Any]] = []
        self.webhook_base_url = getattr(settings, 'TWILIO_WEBHOOK_BASE_URL', 'https://your-ngrok-url.ngrok.io')
        
        # Demo mode settings (for hackathon when Twilio credentials aren't available)
        self.demo_mode = not all([
            getattr(settings, 'TWILIO_ACCOUNT_SID', None),
            getattr(settings, 'TWILIO_AUTH_TOKEN', None),
            getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        ])
        
    async def initialize(self) -> bool:
        """Initialize Twilio phone service"""
        try:
            if not getattr(settings, 'ENABLE_PHONE_NOTIFICATIONS', True):
                logger.info("Phone notifications disabled in configuration")
                return False
            
            if self.demo_mode:
                logger.info("🎭 Twilio credentials not configured - running in DEMO MODE")
                logger.info("📞 Phone calls will be simulated with detailed logging")
                self.is_configured = True
                return True
                
            if not TWILIO_AVAILABLE:
                logger.error("Twilio package not available")
                return False
                
            # Initialize Twilio client with real credentials
            self.client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID, 
                settings.TWILIO_AUTH_TOKEN
            )
            
            # Test the connection
            try:
                account = self.client.api.account.fetch()
                logger.info(f"✅ Twilio connected successfully to account: {account.friendly_name}")
                self.is_configured = True
                return True
                
            except Exception as test_error:
                logger.error(f"Twilio connection test failed: {test_error}")
                logger.info("🎭 Falling back to DEMO MODE")
                self.demo_mode = True
                self.is_configured = True
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize Twilio phone service: {e}")
            logger.info("🎭 Falling back to DEMO MODE")
            self.demo_mode = True
            self.is_configured = True
            return True
    
    async def make_fraud_alert_call(
        self,
        phone_number: str,
        customer_name: str,
        transaction: Transaction,
        anomaly_result: AnomalyResult,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a fraud alert call to customer"""
        
        try:
            # Generate AI-powered call script
            call_script = await self._generate_fraud_script(
                customer_name, transaction, anomaly_result, custom_message
            )
            
            call_result = await self._make_call(
                phone_number=phone_number,
                script=call_script,
                call_type=CallType.FRAUD_ALERT,
                customer_name=customer_name,
                transaction_id=transaction.id,
                risk_level=anomaly_result.risk_level
            )
            
            # Log the call details
            self._log_call(
                phone_number=phone_number,
                customer_name=customer_name,
                call_type=CallType.FRAUD_ALERT,
                transaction_id=transaction.id,
                risk_level=anomaly_result.risk_level,
                success=call_result.get('success', False),
                call_sid=call_result.get('call_sid'),
                status=call_result.get('status'),
                script_preview=call_script[:100] + "..." if len(call_script) > 100 else call_script
            )
            
            return call_result
            
        except Exception as e:
            logger.error(f"Error making fraud alert call: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': CallStatus.FAILED.value,
                'message': f'Failed to initiate fraud alert call: {e}'
            }
    
    async def make_verification_call(
        self,
        phone_number: str,
        customer_name: str,
        verification_code: str,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a verification call with code"""
        
        script = await self._generate_verification_script(customer_name, verification_code)
        
        return await self._make_call(
            phone_number=phone_number,
            script=script,
            call_type=CallType.VERIFICATION_REQUEST,
            customer_name=customer_name,
            transaction_id=transaction_id
        )
    
    async def make_security_notification_call(
        self,
        phone_number: str,
        customer_name: str,
        notification_message: str,
        urgent: bool = False
    ) -> Dict[str, Any]:
        """Make a general security notification call"""
        
        script = await self._generate_security_script(customer_name, notification_message, urgent)
        
        return await self._make_call(
            phone_number=phone_number,
            script=script,
            call_type=CallType.SECURITY_NOTIFICATION,
            customer_name=customer_name
        )
    
    async def make_test_call(
        self,
        phone_number: str,
        customer_name: str = "Customer"
    ) -> Dict[str, Any]:
        """Make a test call to verify phone service is working"""
        
        script = f"Hello {customer_name}, this is a test call from FinancePulse to verify your phone notification settings are working correctly. Your fraud protection system is active and monitoring your account. Thank you for choosing FinancePulse. Goodbye."
        
        return await self._make_call(
            phone_number=phone_number,
            script=script,
            call_type=CallType.TEST_CALL,
            customer_name=customer_name
        )
    
    async def _make_call(
        self,
        phone_number: str,
        script: str,
        call_type: CallType,
        customer_name: str,
        transaction_id: Optional[str] = None,
        risk_level: Optional[RiskLevel] = None
    ) -> Dict[str, Any]:
        """Internal method to make the actual phone call"""
        
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Phone service not configured',
                'status': CallStatus.FAILED.value,
                'message': 'Phone service is not properly initialized'
            }
        
        call_id = f"call_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{phone_number[-4:]}"
        
        try:
            if self.demo_mode:
                return await self._simulate_call(
                    phone_number, script, call_type, customer_name, call_id
                )
            else:
                return await self._make_real_twilio_call(
                    phone_number, script, call_type, customer_name, call_id
                )
                
        except Exception as e:
            logger.error(f"Error in _make_call: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': CallStatus.FAILED.value,
                'call_id': call_id,
                'message': f'Call failed: {e}'
            }
    
    async def _make_real_twilio_call(
        self,
        phone_number: str,
        script: str,
        call_type: CallType,
        customer_name: str,
        call_id: str
    ) -> Dict[str, Any]:
        """Make actual Twilio call"""
        
        try:
            # Create TwiML for the call
            twiml = VoiceResponse()
            twiml.say(script, voice='alice', language='en-US')
            
            # Make the call
            call = self.client.calls.create(
                twiml=str(twiml),
                to=phone_number,
                from_=settings.TWILIO_PHONE_NUMBER,
                status_callback=f"{self.webhook_base_url}/api/v1/twilio/status",
                status_callback_event=['initiated', 'answered', 'completed'],
                status_callback_method='POST'
            )
            
            logger.info(f"📞 REAL TWILIO CALL initiated: {call.sid} to {self._mask_phone_number(phone_number)}")
            logger.info(f"🎯 Call Type: {call_type.value}")
            logger.info(f"📱 Script Preview: {script[:150]}...")
            
            return {
                'success': True,
                'call_id': call_id,
                'call_sid': call.sid,
                'status': CallStatus.INITIATED.value,
                'phone_number': self._mask_phone_number(phone_number),
                'customer_name': customer_name,
                'call_type': call_type.value,
                'script_length': len(script),
                'initiated_at': datetime.utcnow().isoformat(),
                'message': f'Call initiated successfully to {self._mask_phone_number(phone_number)}',
                'provider': 'twilio_real'
            }
            
        except Exception as e:
            logger.error(f"Twilio call failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'call_id': call_id,
                'status': CallStatus.FAILED.value,
                'message': f'Twilio call failed: {e}',
                'provider': 'twilio_real'
            }
    
    async def _simulate_call(
        self,
        phone_number: str,
        script: str,
        call_type: CallType,
        customer_name: str,
        call_id: str
    ) -> Dict[str, Any]:
        """Simulate a phone call for demo purposes"""
        
        try:
            # Simulate call processing time
            await asyncio.sleep(0.5)
            
            # Simulate various call outcomes
            import random
            outcomes = [
                (CallStatus.COMPLETED, 0.85),  # 85% success rate
                (CallStatus.NO_ANSWER, 0.10),  # 10% no answer
                (CallStatus.BUSY, 0.05)        # 5% busy
            ]
            
            rand_val = random.random()
            cumulative = 0
            status = CallStatus.COMPLETED
            
            for outcome_status, probability in outcomes:
                cumulative += probability
                if rand_val <= cumulative:
                    status = outcome_status
                    break
            
            success = status == CallStatus.COMPLETED
            
            # Generate realistic call duration (30-90 seconds)
            call_duration = random.randint(30, 90) if success else 0
            
            logger.info("🎭" + "="*60)
            logger.info(f"📞 SIMULATED CALL - Call ID: {call_id}")
            logger.info(f"📱 To: {self._mask_phone_number(phone_number)} ({customer_name})")
            logger.info(f"🎯 Type: {call_type.value.upper()}")
            logger.info(f"✅ Status: {status.value.upper()}")
            logger.info(f"⏱️  Duration: {call_duration} seconds" if success else "⏱️  Duration: Call not answered")
            logger.info(f"📝 Script Length: {len(script)} characters")
            logger.info("🎬 SCRIPT PREVIEW:")
            logger.info(f"   \"{script[:200]}{'...' if len(script) > 200 else ''}\"")
            logger.info("🎭" + "="*60)
            
            return {
                'success': success,
                'call_id': call_id,
                'call_sid': f"demo_{call_id}",
                'status': status.value,
                'phone_number': self._mask_phone_number(phone_number),
                'customer_name': customer_name,
                'call_type': call_type.value,
                'duration_seconds': call_duration,
                'script_length': len(script),
                'initiated_at': datetime.utcnow().isoformat(),
                'completed_at': datetime.utcnow().isoformat() if success else None,
                'message': f'Demo call {"completed successfully" if success else f"failed: {status.value}"} to {self._mask_phone_number(phone_number)}',
                'provider': 'demo_simulation',
                'script_preview': script[:100] + "..." if len(script) > 100 else script
            }
            
        except Exception as e:
            logger.error(f"Error in call simulation: {e}")
            return {
                'success': False,
                'error': str(e),
                'call_id': call_id,
                'status': CallStatus.FAILED.value,
                'message': f'Demo call simulation failed: {e}',
                'provider': 'demo_simulation'
            }
    
    async def _generate_fraud_script(
        self,
        customer_name: str,
        transaction: Transaction,
        anomaly_result: AnomalyResult,
        custom_message: Optional[str] = None
    ) -> str:
        """Generate AI-powered fraud alert script"""
        
        try:
            if custom_message:
                # Use custom message if provided
                base_script = f"Hello {customer_name}, this is FinancePulse Security calling about your account. {custom_message}"
            else:
                # Generate script based on transaction details
                risk_urgency = {
                    RiskLevel.CRITICAL: "immediately",
                    RiskLevel.HIGH: "urgently", 
                    RiskLevel.MEDIUM: "promptly",
                    RiskLevel.LOW: "when convenient"
                }
                
                urgency = risk_urgency.get(anomaly_result.risk_level, "promptly")
                
                # Use OpenAI to generate a natural, professional script
                prompt = f"""
                Generate a professional, calm, and reassuring phone call script for a fraud alert.
                
                Customer: {customer_name}
                Transaction: ${transaction.amount:.2f} at {transaction.merchant_name}
                Location: {transaction.location.get('city', 'Unknown')}, {transaction.location.get('state', '')}
                Risk Level: {anomaly_result.risk_level.value}
                Confidence: {anomaly_result.confidence_score * 100:.0f}%
                
                Requirements:
                - Keep under 45 seconds when spoken
                - Professional but friendly tone
                - Clear call to action
                - Mention this is FinancePulse Security
                - Don't reveal sensitive details over phone
                - Ask them to call back or check their app
                - Reassure them their account is monitored
                
                Format as spoken dialogue, not bullet points.
                """
                
                try:
                    ai_script = await openai_service.generate_custom_content(prompt)
                    base_script = ai_script.strip()
                except Exception as openai_error:
                    logger.warning(f"OpenAI script generation failed: {openai_error}")
                    # Fallback to template script
                    base_script = f"""
                    Hello {customer_name}, this is FinancePulse Security calling about your account. 
                    We've detected a transaction for ${transaction.amount:.2f} at {transaction.merchant_name} 
                    that appears unusual based on your spending patterns. 
                    
                    Your account is secure and we've temporarily flagged this transaction for your protection. 
                    Please call us back at 1-800-FINANCE or check your FinancePulse app to verify this transaction. 
                    
                    Thank you for choosing FinancePulse where your security is our priority. Goodbye.
                    """.strip()
            
            # Clean up the script
            script = base_script.replace('\n', ' ').replace('  ', ' ').strip()
            
            # Ensure script isn't too long (max ~50 seconds at normal speech rate)
            if len(script) > 800:  # Roughly 50 seconds of speech
                script = script[:750] + "... Please contact us for more details. Thank you."
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating fraud script: {e}")
            # Ultimate fallback script
            return f"Hello {customer_name}, this is FinancePulse Security. We've detected unusual activity on your account. Please call us back immediately to verify your recent transactions. Thank you."
    
    async def _generate_verification_script(
        self,
        customer_name: str,
        verification_code: str
    ) -> str:
        """Generate verification call script"""
        
        return f"""
        Hello {customer_name}, this is FinancePulse calling with a security verification code. 
        Your verification code is: {verification_code}. I'll repeat that: {verification_code}. 
        Please enter this code in your app or website to complete your security verification. 
        This code will expire in 10 minutes. Thank you for using FinancePulse.
        """.strip().replace('\n', ' ').replace('  ', ' ')
    
    async def _generate_security_script(
        self,
        customer_name: str,
        message: str,
        urgent: bool = False
    ) -> str:
        """Generate general security notification script"""
        
        urgency_prefix = "Urgent security notification: " if urgent else ""
        
        return f"""
        Hello {customer_name}, this is FinancePulse Security. {urgency_prefix}{message} 
        Please check your FinancePulse app or call us back if you have any questions. 
        Your account security is our top priority. Thank you.
        """.strip().replace('\n', ' ').replace('  ', ' ')
    
    def _log_call(self, **call_details):
        """Log call details for tracking"""
        call_record = {
            'timestamp': datetime.utcnow().isoformat(),
            **call_details
        }
        self.call_log.append(call_record)
        
        # Keep only last 1000 calls to prevent memory issues
        if len(self.call_log) > 1000:
            self.call_log = self.call_log[-1000:]
    
    def _mask_phone_number(self, phone_number: str) -> str:
        """Mask phone number for privacy in logs"""
        if len(phone_number) < 4:
            return "***"
        return phone_number[:-4] + "****"
    
    def get_call_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent call history"""
        return self.call_log[-limit:] if self.call_log else []
    
    def get_call_stats(self) -> Dict[str, Any]:
        """Get call statistics"""
        if not self.call_log:
            return {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'success_rate': 0.0,
                'call_types': {}
            }
        
        successful = len([c for c in self.call_log if c.get('success', False)])
        total = len(self.call_log)
        
        call_types = {}
        for call in self.call_log:
            call_type = call.get('call_type', 'unknown')
            call_types[call_type] = call_types.get(call_type, 0) + 1
        
        return {
            'total_calls': total,
            'successful_calls': successful,
            'failed_calls': total - successful,
            'success_rate': round(successful / total, 3) if total > 0 else 0.0,
            'call_types': call_types,
            'demo_mode': self.demo_mode,
            'provider': 'twilio' if not self.demo_mode else 'demo_simulation'
        }


# Global service instance
enhanced_phone_service = EnhancedTwilioPhoneService()