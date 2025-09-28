#!/usr/bin/env python3
"""
FinancePulse Voice Service
Integrated Twilio voice calling for fraud detection and customer communication
Combines the hackgtcedar voice system with FinancePulse fraud detection
"""

import os
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

# Core dependencies
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Twilio
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# HTTP requests
import requests

# FinancePulse imports
from app.core.config import settings
from app.models import Transaction, AnomalyResult, RiskLevel
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)


class CallType(Enum):
    FRAUD_ALERT = "fraud_alert"
    SECURITY_VERIFICATION = "security_verification"
    ACCOUNT_NOTIFICATION = "account_notification"
    CUSTOMER_SERVICE = "customer_service"


class CallStatus(Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"


class FinancePulseVoiceService:
    """Integrated voice service for FinancePulse fraud detection calls"""
    
    def __init__(self):
        # Twilio configuration from FinancePulse settings
        self.twilio_client = None
        self.is_configured = False
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.conversation_history: Dict[str, list] = {}
        
        # Use settings from hackgtcedar if needed or FinancePulse settings
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None) 
        self.twilio_phone_number = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
        self.webhook_base_url = getattr(settings, 'PUBLIC_BASE_URL', 'http://localhost:8000')
        
        # Demo mode when credentials not available
        self.demo_mode = not all([
            self.twilio_account_sid, 
            self.twilio_auth_token, 
            self.twilio_phone_number
        ])
        
    async def initialize(self) -> bool:
        """Initialize the FinancePulse voice service"""
        try:
            if self.demo_mode:
                logger.info("🎭 Twilio credentials not configured - running in DEMO MODE")
                logger.info("📞 Voice calls will be simulated with detailed logging")
                self.is_configured = True
                return True
            
            # Initialize real Twilio client
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Test connection
            try:
                account = self.twilio_client.api.account.fetch()
                logger.info(f"✅ Twilio connected: {account.friendly_name}")
                self.is_configured = True
                return True
            except Exception as test_error:
                logger.error(f"Twilio connection test failed: {test_error}")
                logger.info("🎭 Falling back to DEMO MODE")
                self.demo_mode = True
                self.is_configured = True
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize voice service: {e}")
            logger.info("🎭 Falling back to DEMO MODE")  
            self.demo_mode = True
            self.is_configured = True
            return True
    
    async def make_fraud_alert_call(
        self,
        phone_number: str,
        customer_name: str,
        transaction: Transaction,
        anomaly_result: AnomalyResult
    ) -> Dict[str, Any]:
        """Make a fraud alert call to customer about suspicious transaction"""
        
        if not self.is_configured:
            return {"success": False, "error": "Voice service not configured"}
        
        try:
            # Generate AI-powered fraud alert script using OpenAI
            call_script = await self._generate_fraud_alert_script(
                customer_name, transaction, anomaly_result
            )
            
            # Make the call (real or simulated)
            call_result = await self._make_call(
                phone_number=phone_number,
                script=call_script,
                call_type=CallType.FRAUD_ALERT,
                customer_name=customer_name,
                transaction_id=transaction.id,
                risk_level=anomaly_result.risk_level.value
            )
            
            # Log the call
            await self._log_call_record(
                phone_number=phone_number,
                customer_name=customer_name,
                call_type=CallType.FRAUD_ALERT.value,
                transaction_id=transaction.id,
                risk_level=anomaly_result.risk_level.value,
                success=call_result.get('success', False),
                call_sid=call_result.get('call_sid'),
                script_preview=call_script[:100] + "..." if len(call_script) > 100 else call_script
            )
            
            return call_result
            
        except Exception as e:
            logger.error(f"Error making fraud alert call: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to make fraud alert call: {e}'
            }
    
    async def make_verification_call(
        self,
        phone_number: str,
        customer_name: str,
        verification_message: str
    ) -> Dict[str, Any]:
        """Make a verification call for account security"""
        
        try:
            script = await self._generate_verification_script(customer_name, verification_message)
            
            return await self._make_call(
                phone_number=phone_number,
                script=script,
                call_type=CallType.SECURITY_VERIFICATION,
                customer_name=customer_name
            )
            
        except Exception as e:
            logger.error(f"Error making verification call: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _make_call(
        self,
        phone_number: str,
        script: str,
        call_type: CallType,
        customer_name: str,
        transaction_id: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal method to make calls (real or simulated)"""
        
        if self.demo_mode:
            return await self._simulate_call(
                phone_number, script, call_type, customer_name, transaction_id, risk_level
            )
        else:
            return await self._make_real_twilio_call(
                phone_number, script, call_type, customer_name, transaction_id
            )
    
    async def _simulate_call(
        self,
        phone_number: str,
        script: str,
        call_type: CallType,
        customer_name: str,
        transaction_id: Optional[str] = None,
        risk_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simulate a call with detailed logging"""
        
        import random
        
        call_id = f"demo_call_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Simulate call success/failure
        success_rate = 0.85  # 85% success rate in demo
        success = random.random() < success_rate
        
        # Simulate call duration
        call_duration = random.randint(30, 120) if success else 0
        
        logger.info("🎭" + "="*60)
        logger.info(f"📞 SIMULATED FRAUD ALERT CALL - Call ID: {call_id}")
        logger.info(f"📱 To: {self._mask_phone_number(phone_number)} ({customer_name})")
        logger.info(f"🚨 Type: {call_type.value.upper()}")
        logger.info(f"⚠️  Risk Level: {risk_level or 'N/A'}")
        logger.info(f"✅ Status: {'COMPLETED' if success else 'FAILED'}")
        logger.info(f"⏱️  Duration: {call_duration} seconds" if success else "⏱️  Duration: Call not answered")
        logger.info(f"📝 Script Length: {len(script)} characters")
        logger.info("🎬 FRAUD ALERT SCRIPT:")
        logger.info(f"   \"{script}\"")
        logger.info("🎭" + "="*60)
        
        return {
            'success': success,
            'call_id': call_id,
            'call_sid': f"demo_{call_id}",
            'status': 'completed' if success else 'failed',
            'phone_number': self._mask_phone_number(phone_number),
            'customer_name': customer_name,
            'call_type': call_type.value,
            'transaction_id': transaction_id,
            'risk_level': risk_level,
            'duration_seconds': call_duration,
            'script_length': len(script),
            'initiated_at': datetime.utcnow().isoformat(),
            'completed_at': datetime.utcnow().isoformat() if success else None,
            'message': f'Demo fraud alert call {"completed successfully" if success else "failed"} to {customer_name}',
            'provider': 'financepulse_demo_simulation'
        }
    
    async def _make_real_twilio_call(
        self,
        phone_number: str,
        script: str,
        call_type: CallType,
        customer_name: str,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make a real Twilio call"""
        
        try:
            # Create webhook URL for this call
            webhook_url = f"{self.webhook_base_url}/api/v1/voice/webhook"
            
            call = self.twilio_client.calls.create(
                to=phone_number,
                from_=self.twilio_phone_number,
                twiml=f'<Response><Say voice="alice">{script}</Say></Response>',
                timeout=30,
                record=True
            )
            
            call_sid = call.sid
            
            # Store call info
            self.active_calls[call_sid] = {
                'call_sid': call_sid,
                'phone_number': phone_number,
                'customer_name': customer_name,
                'call_type': call_type.value,
                'transaction_id': transaction_id,
                'script': script,
                'status': 'initiated',
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"📞 REAL TWILIO CALL initiated to {self._mask_phone_number(phone_number)}")
            logger.info(f"📱 Call SID: {call.sid}")
            
            return {
                'success': True,
                'call_sid': call.sid,
                'status': 'initiated',
                'phone_number': self._mask_phone_number(phone_number),
                'customer_name': customer_name,
                'call_type': call_type.value,
                'message': f'Real fraud alert call initiated to {customer_name}',
                'provider': 'twilio'
            }
            
        except Exception as e:
            logger.error(f"Error making real Twilio call: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to make real call: {e}'
            }
    
    async def _generate_fraud_alert_script(
        self,
        customer_name: str,
        transaction: Transaction,
        anomaly_result: AnomalyResult
    ) -> str:
        """Generate AI-powered fraud alert script using OpenAI"""
        
        try:
            # Create detailed prompt for OpenAI
            risk_level = anomaly_result.risk_level.value.upper()
            amount = f"${transaction.amount:.2f}"
            merchant = transaction.merchant_name
            timestamp = transaction.timestamp.strftime("%B %d at %I:%M %p")
            
            prompt = f"""
Generate a professional, calm fraud alert phone call script for a customer.

DETAILS:
- Customer: {customer_name}
- Transaction: {amount} at {merchant}
- Time: {timestamp}
- Risk Level: {risk_level}
- Confidence: {anomaly_result.confidence_score * 100:.0f}%

REQUIREMENTS:
- Professional but friendly tone
- Under 45 seconds when spoken (about 150 words)
- Identify as "FinancePulse Security"
- Don't reveal sensitive details over phone
- Clear call to action
- Reassuring but urgent based on risk level

SCRIPT TONE for {risk_level} risk:
{"URGENT and IMMEDIATE action required" if risk_level == "CRITICAL" 
else "Prompt verification needed" if risk_level == "HIGH"
else "Please verify when convenient" if risk_level == "MEDIUM" 
else "Notification for your awareness"}

Generate ONLY the spoken script, no stage directions.
"""
            
            # Use OpenAI to generate script (includes fallback)
            script = await openai_service.generate_custom_content(prompt, max_tokens=200)
            
            # Ensure script isn't too long
            if len(script) > 600:  # ~45 seconds of speech
                script = script[:550] + "... Please call us back at your earliest convenience. Thank you."
            
            return script.strip()
            
        except Exception as e:
            logger.error(f"Error generating fraud script: {e}")
            # Ultimate fallback
            urgency = {
                "CRITICAL": "immediately",
                "HIGH": "as soon as possible", 
                "MEDIUM": "at your convenience",
                "LOW": "when convenient"
            }.get(anomaly_result.risk_level.value.upper(), "promptly")
            
            return f"""Hello {customer_name}, this is FinancePulse Security calling about a transaction on your account. 
We detected a {amount} transaction at {merchant} that appears unusual based on your spending patterns. 
Your account is secure and we've flagged this transaction for your protection. 
Please call us back {urgency} at 1-800-FINANCE or check your FinancePulse app to verify this transaction. 
Thank you for choosing FinancePulse where your security is our priority."""
    
    async def _generate_verification_script(
        self,
        customer_name: str,
        message: str
    ) -> str:
        """Generate verification call script"""
        
        return f"""Hello {customer_name}, this is FinancePulse Security. 
{message}
Please check your FinancePulse app or call us back if you have any questions. 
Your account security is our top priority. Thank you."""
    
    async def _log_call_record(self, **call_details):
        """Log call record for tracking and analytics"""
        call_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'financepulse_voice',
            **call_details
        }
        
        # In production, this would go to a database
        logger.info(f"📋 Call Record: {json.dumps(call_record, indent=2)}")
    
    def _mask_phone_number(self, phone_number: str) -> str:
        """Mask phone number for privacy"""
        if len(phone_number) < 4:
            return "***"
        return phone_number[:-4] + "****"
    
    def get_call_status(self, call_sid: str) -> Optional[Dict[str, Any]]:
        """Get call status by SID"""
        return self.active_calls.get(call_sid)
    
    def get_active_calls(self) -> Dict[str, Dict[str, Any]]:
        """Get all active calls"""
        return self.active_calls
    
    def get_call_stats(self) -> Dict[str, Any]:
        """Get call statistics"""
        # This would be enhanced with real database queries
        return {
            'total_active_calls': len(self.active_calls),
            'service_status': 'active' if self.is_configured else 'inactive',
            'demo_mode': self.demo_mode,
            'provider': 'twilio' if not self.demo_mode else 'demo_simulation'
        }


# Global service instance
financepulse_voice_service = FinancePulseVoiceService()