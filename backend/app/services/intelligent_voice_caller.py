#!/usr/bin/env python3
"""
Intelligent Voice Calling System for FinancePulse
Uses hybrid LLM models and real customer data for personalized fraud alerts
"""

import os
import json
import logging
import asyncio
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

# Twilio integration
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# FinancePulse services
from app.core.config import settings
from app.services.advanced_fraud_detector import advanced_fraud_detector, TransactionAnalysis, FraudRiskLevel
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)

class IntelligentVoiceCaller:
    """Advanced voice calling system with AI-generated personalized scripts"""
    
    def __init__(self):
        # Twilio configuration
        self.twilio_client = None
        self.is_configured = False
        self.demo_mode = True
        
        # Voice calling statistics
        self.calls_made = 0
        self.successful_calls = 0
        self.call_history: List[Dict] = []
        
        # Initialize Twilio if configured
        self._initialize_twilio()
    
    def _initialize_twilio(self):
        """Initialize Twilio client if credentials are available"""
        try:
            twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
            twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
            twilio_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
            
            if all([twilio_sid, twilio_token, twilio_phone]):
                self.twilio_client = Client(twilio_sid, twilio_token)
                self.twilio_phone_number = twilio_phone
                self.demo_mode = False
                logger.info("✅ Twilio initialized for live calls")
            else:
                logger.info("🎭 Twilio credentials not found - running in demo mode")
        except Exception as e:
            logger.error(f"Twilio initialization failed: {e} - using demo mode")
    
    async def generate_personalized_fraud_script(self, analysis: TransactionAnalysis) -> str:
        """Generate personalized fraud alert script using hybrid LLM approach"""
        
        customer = analysis.customer
        
        # Prepare context for LLM
        context = {
            "customer_name": customer.name,
            "customer_age": customer.age,
            "usual_location": customer.usual_location,
            "avg_monthly_spending": customer.avg_monthly_purchases,
            "transaction_amount": analysis.transaction_amount,
            "merchant": analysis.merchant_name,
            "location": analysis.location,
            "risk_level": analysis.risk_level.value,
            "risk_score": analysis.overall_risk_score,
            "urgency": analysis.call_urgency,
            "fraud_flags": [{
                "category": flag.category.value,
                "description": flag.description,
                "severity": flag.severity
            } for flag in analysis.fraud_flags]
        }
        
        # Create specialized prompt for different risk levels
        prompt = self._create_fraud_script_prompt(context)
        
        try:
            # Use OpenAI/hybrid model to generate script
            script = await openai_service.generate_custom_content(prompt)
            
            # Post-process script
            script = self._post_process_script(script, analysis)
            
            return script
            
        except Exception as e:
            logger.error(f"LLM script generation failed: {e}")
            # Fallback to template-based script
            return self._generate_fallback_script(analysis)
    
    def _create_fraud_script_prompt(self, context: Dict) -> str:
        """Create specialized prompt for fraud alert script generation"""
        
        urgency_tone = {
            "IMMEDIATE": "urgent and requires immediate action",
            "URGENT": "important and needs prompt attention", 
            "STANDARD": "concerning and should be verified"
        }.get(context["urgency"], "noteworthy")
        
        # Determine age-appropriate language
        age_consideration = ""
        if context["customer_age"] >= 65:
            age_consideration = "Use clear, respectful language appropriate for a senior customer. Explain technical terms simply."
        elif context["customer_age"] <= 30:
            age_consideration = "Use modern, direct language. Customer is likely tech-savvy."
        
        # Extract primary fraud concerns
        main_concerns = [flag["description"] for flag in context["fraud_flags"][:2]]  # Top 2 concerns
        
        prompt = f"""
Generate a professional fraud alert phone call script for a bank customer.

CUSTOMER DETAILS:
- Name: {context["customer_name"]}
- Age: {context["customer_age"]}
- Usual location: {context["usual_location"]}
- Typical monthly spending: ${context["avg_monthly_spending"]:.2f}

SUSPICIOUS TRANSACTION:
- Amount: ${context["transaction_amount"]:.2f}
- Merchant: {context["merchant"]}
- Location: {context["location"] or "Unknown location"}
- Risk Level: {context["risk_level"].upper()}
- This transaction is {urgency_tone}

MAIN FRAUD INDICATORS:
{chr(10).join(f"- {concern}" for concern in main_concerns)}

SCRIPT REQUIREMENTS:
- Identify as "FinancePulse Fraud Prevention Team"
- Professional, calm, and reassuring tone
- Explain WHY the transaction was flagged (without revealing sensitive algorithms)
- Clear next steps for the customer
- Under 45 seconds when spoken (≈150 words)
- No technical jargon
{age_consideration}

IMPORTANT: This is a {context["risk_level"]} risk situation requiring {context["urgency"].lower()} response.

Generate ONLY the spoken script, no stage directions or formatting:
"""
        
        return prompt
    
    def _post_process_script(self, script: str, analysis: TransactionAnalysis) -> str:
        """Post-process generated script for quality and compliance"""
        
        # Remove any unwanted formatting
        script = script.strip()
        script = script.replace("**", "")
        script = script.replace("*", "")
        
        # Ensure script isn't too long (45 seconds ≈ 150 words)
        words = script.split()
        if len(words) > 160:
            # Truncate and add proper ending
            script = " ".join(words[:140]) + " Please contact us immediately at 1-800-FRAUD-HELP or check your FinancePulse app. Thank you."
        
        # Ensure proper greeting and closing
        if not script.lower().startswith("hello"):
            script = f"Hello {analysis.customer.name}, " + script
        
        if "thank you" not in script.lower():
            script += " Thank you for your attention to account security."
        
        return script
    
    def _generate_fallback_script(self, analysis: TransactionAnalysis) -> str:
        """Generate fallback script when LLM fails"""
        
        customer = analysis.customer
        urgency_map = {
            "IMMEDIATE": "requires your immediate attention",
            "URGENT": "needs your prompt response",
            "STANDARD": "should be verified"
        }
        
        urgency_text = urgency_map.get(analysis.call_urgency, "requires verification")
        
        # Create explanation based on top fraud flags
        if analysis.fraud_flags:
            primary_reason = analysis.fraud_flags[0].description
        else:
            primary_reason = "unusual transaction pattern detected"
        
        script = f"""Hello {customer.name}, this is the FinancePulse Fraud Prevention Team. We detected a ${analysis.transaction_amount:.2f} transaction at {analysis.merchant_name} that {urgency_text}. This was flagged because {primary_reason.lower()}. Your account is secure, but we need you to verify this transaction. Please call us at 1-800-FRAUD-HELP or check your FinancePulse app immediately. Thank you for helping us protect your account."""
        
        return script.strip()
    
    async def make_intelligent_fraud_call(self, customer_name: str, phone_number: str = None) -> Dict[str, Any]:
        """Make an intelligent fraud alert call using real customer data"""
        
        # Get flagged transactions for this customer
        flagged_transactions = advanced_fraud_detector.get_flagged_transactions()
        customer_transactions = [t for t in flagged_transactions if t["customer_name"] == customer_name]
        
        if not customer_transactions:
            return {
                "success": False,
                "error": f"No flagged transactions found for {customer_name}",
                "message": "Customer has no suspicious transactions requiring calls"
            }
        
        # Analyze the most recent flagged transaction
        latest_transaction = customer_transactions[-1]  # Get the last one
        analysis = advanced_fraud_detector.analyze_transaction(
            customer_name, 
            latest_transaction["transaction_detail"]
        )
        
        if not analysis or not analysis.should_call_customer:
            return {
                "success": False,
                "error": "Transaction does not meet criteria for customer call",
                "risk_level": analysis.risk_level.value if analysis else "unknown"
            }
        
        # Generate personalized script
        script = await self.generate_personalized_fraud_script(analysis)
        
        # Determine phone number (use demo if not provided)
        if not phone_number:
            phone_number = "+1555" + str(analysis.customer.customer_id).zfill(6)
        
        # Make the call (demo or real)
        call_result = await self._execute_call(
            phone_number=phone_number,
            script=script,
            analysis=analysis
        )
        
        # Log call details
        await self._log_intelligent_call(analysis, script, call_result)
        
        return call_result
    
    async def _execute_call(self, phone_number: str, script: str, analysis: TransactionAnalysis) -> Dict[str, Any]:
        """Execute the actual call (real or simulated)"""
        
        if self.demo_mode:
            return await self._simulate_intelligent_call(phone_number, script, analysis)
        else:
            return await self._make_real_intelligent_call(phone_number, script, analysis)
    
    async def _simulate_intelligent_call(self, phone_number: str, script: str, analysis: TransactionAnalysis) -> Dict[str, Any]:
        """Simulate intelligent fraud call with detailed logging"""
        
        call_id = f"intel_fraud_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Simulate call success based on risk level
        success_rates = {
            FraudRiskLevel.CRITICAL: 0.95,
            FraudRiskLevel.HIGH: 0.90,
            FraudRiskLevel.MEDIUM: 0.85,
            FraudRiskLevel.LOW: 0.80
        }
        
        success = random.random() < success_rates.get(analysis.risk_level, 0.85)
        duration = random.randint(45, 120) if success else 0
        
        # Enhanced logging with fraud analysis details
        logger.info("🎭" + "="*70)
        logger.info(f"🔍 INTELLIGENT FRAUD ALERT CALL - ID: {call_id}")
        logger.info(f"👤 Customer: {analysis.customer.name} (Age: {analysis.customer.age})")
        logger.info(f"📱 Phone: {self._mask_phone(phone_number)}")
        logger.info(f"📍 Customer Location: {analysis.customer.usual_location}")
        logger.info(f"💰 Transaction: ${analysis.transaction_amount:.2f} at {analysis.merchant_name}")
        logger.info(f"🚨 Risk Level: {analysis.risk_level.value.upper()} ({analysis.overall_risk_score*100:.1f}%)")
        logger.info(f"⚡ Urgency: {analysis.call_urgency}")
        logger.info(f"🎯 Fraud Indicators ({len(analysis.fraud_flags)}):")
        
        for i, flag in enumerate(analysis.fraud_flags, 1):
            logger.info(f"   {i}. {flag.category.value.title()}: {flag.description[:60]}...")
        
        logger.info(f"✅ Call Status: {'COMPLETED' if success else 'FAILED'}")
        logger.info(f"⏱️  Duration: {duration} seconds" if success else "⏱️  Duration: No answer/Failed")
        logger.info(f"📝 Script Length: {len(script)} characters ({len(script.split())} words)")
        logger.info("🎬 PERSONALIZED FRAUD SCRIPT:")
        logger.info(f"   \"{script}\"")
        logger.info("🎭" + "="*70)
        
        self.calls_made += 1
        if success:
            self.successful_calls += 1
        
        return {
            "success": success,
            "call_id": call_id,
            "call_sid": f"demo_intel_{call_id}",
            "status": "completed" if success else "failed",
            "customer_name": analysis.customer.name,
            "phone_number": self._mask_phone(phone_number),
            "transaction_amount": analysis.transaction_amount,
            "merchant": analysis.merchant_name,
            "risk_level": analysis.risk_level.value,
            "risk_score": analysis.overall_risk_score,
            "urgency": analysis.call_urgency,
            "fraud_indicators": len(analysis.fraud_flags),
            "script_words": len(script.split()),
            "duration_seconds": duration,
            "provider": "financepulse_intelligent_demo",
            "demo_mode": True,
            "timestamp": datetime.now().isoformat(),
            "message": f"Intelligent fraud call {'completed' if success else 'failed'} for {analysis.customer.name}"
        }
    
    async def _make_real_intelligent_call(self, phone_number: str, script: str, analysis: TransactionAnalysis) -> Dict[str, Any]:
        """Make real Twilio call with intelligent script"""
        
        try:
            # Create TwiML with intelligent script
            twiml = f'<Response><Say voice="alice" rate="medium">{script}</Say></Response>'
            
            call = self.twilio_client.calls.create(
                to=phone_number,
                from_=self.twilio_phone_number,
                twiml=twiml,
                timeout=30,
                record=True
            )
            
            self.calls_made += 1
            self.successful_calls += 1
            
            logger.info(f"📞 LIVE INTELLIGENT CALL: {call.sid} to {analysis.customer.name}")
            
            return {
                "success": True,
                "call_sid": call.sid,
                "status": "initiated",
                "customer_name": analysis.customer.name,
                "phone_number": self._mask_phone(phone_number),
                "risk_level": analysis.risk_level.value,
                "provider": "twilio_intelligent",
                "demo_mode": False,
                "message": f"Live intelligent fraud call initiated for {analysis.customer.name}"
            }
            
        except Exception as e:
            logger.error(f"Real call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to make live call: {e}"
            }
    
    async def _log_intelligent_call(self, analysis: TransactionAnalysis, script: str, call_result: Dict):
        """Log detailed call information for analytics"""
        
        call_log = {
            "timestamp": datetime.now().isoformat(),
            "service": "intelligent_voice_caller",
            "customer_id": analysis.customer.customer_id,
            "customer_name": analysis.customer.name,
            "customer_age": analysis.customer.age,
            "transaction_id": analysis.transaction_id,
            "transaction_amount": analysis.transaction_amount,
            "merchant": analysis.merchant_name,
            "risk_analysis": {
                "risk_level": analysis.risk_level.value,
                "risk_score": analysis.overall_risk_score,
                "urgency": analysis.call_urgency,
                "fraud_flags_count": len(analysis.fraud_flags),
                "fraud_categories": [flag.category.value for flag in analysis.fraud_flags]
            },
            "call_details": {
                "success": call_result.get("success", False),
                "call_id": call_result.get("call_id"),
                "duration": call_result.get("duration_seconds", 0),
                "script_length": len(script),
                "script_words": len(script.split()),
                "demo_mode": call_result.get("demo_mode", True)
            }
        }
        
        self.call_history.append(call_log)
        logger.info(f"📋 Intelligent Call Logged: {json.dumps(call_log, indent=2)}")
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for privacy"""
        if len(phone) < 4:
            return "***"
        return phone[:-4] + "****"
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """Get comprehensive call statistics"""
        return {
            "total_calls_made": self.calls_made,
            "successful_calls": self.successful_calls,
            "success_rate": (self.successful_calls / max(1, self.calls_made)) * 100,
            "demo_mode": self.demo_mode,
            "provider": "twilio" if not self.demo_mode else "intelligent_demo",
            "call_history_count": len(self.call_history),
            "service_status": "operational"
        }

# Global instance
intelligent_voice_caller = IntelligentVoiceCaller()