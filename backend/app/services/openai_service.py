"""
OpenAI Integration Service
Handles AI content generation for email and phone notifications using OpenAI GPT models
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple
from datetime import datetime

from openai import AsyncOpenAI

from app.core.config import settings
from app.models import Transaction, AnomalyResult, RiskLevel

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI service for generating notification content"""
    
    def __init__(self):
        self.client = None
        self.is_initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the OpenAI service"""
        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not configured, using fallback content generation")
                return False
                
            # Initialize the OpenAI client
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=30.0
            )
            
            # Test the client with a simple request
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": "Test connection. Respond with 'OK'."}],
                    max_tokens=10,
                    temperature=0.1
                )
                
                if response and response.choices and response.choices[0].message.content:
                    self.is_initialized = True
                    logger.info("✅ OpenAI service initialized successfully")
                    return True
                else:
                    logger.error("Failed to get test response from OpenAI")
                    return False
                    
            except Exception as test_error:
                logger.error(f"OpenAI test request failed: {test_error}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI service: {e}")
            return False
    
    async def generate_email_content(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult,
        customer_name: str = "Customer"
    ) -> Tuple[str, str]:
        """
        Generate email subject and body for anomaly notification
        Returns tuple of (subject, body)
        """
        if not self.is_initialized:
            return self._fallback_email_content(transaction, anomaly_result, customer_name)
        
        try:
            # Create prompt for email generation
            prompt = self._build_email_prompt(transaction, anomaly_result, customer_name)
            
            # Generate content using OpenAI
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional banking security AI that generates formal, clear, and actionable fraud alert emails. Always maintain banking industry communication standards."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.3,
                top_p=0.9
            )
            
            if response and response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                return self._parse_email_response(content)
            else:
                logger.warning("Empty or invalid response from OpenAI, using fallback")
                return self._fallback_email_content(transaction, anomaly_result, customer_name)
                
        except Exception as e:
            logger.error(f"Error generating email content with OpenAI: {e}")
            return self._fallback_email_content(transaction, anomaly_result, customer_name)
    
    async def generate_phone_script(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult,
        customer_name: str = "Customer"
    ) -> str:
        """Generate phone call script for anomaly notification"""
        if not self.is_initialized:
            return self._fallback_phone_script(transaction, anomaly_result, customer_name)
        
        try:
            # Create prompt for phone script generation
            prompt = self._build_phone_script_prompt(transaction, anomaly_result, customer_name)
            
            # Generate content using OpenAI
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI that generates professional, concise phone call scripts for banking security alerts. Scripts should be natural when spoken aloud and under 60 seconds."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=400,
                temperature=0.2
            )
            
            if response and response.choices and response.choices[0].message.content:
                script = response.choices[0].message.content.strip()
                # Clean up the script for better speech synthesis
                script = script.replace('\n\n', ' ').replace('\n', ' ')
                return script
            else:
                logger.warning("Empty or invalid response from OpenAI, using fallback")
                return self._fallback_phone_script(transaction, anomaly_result, customer_name)
                
        except Exception as e:
            logger.error(f"Error generating phone script with OpenAI: {e}")
            return self._fallback_phone_script(transaction, anomaly_result, customer_name)
    
    async def generate_custom_content(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate custom content using OpenAI with a given prompt"""
        if not self.is_initialized:
            return "OpenAI service not available. Using fallback analysis."
            
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial security AI assistant that provides clear, professional analysis and explanations about financial transactions and fraud detection."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            if response and response.choices and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                logger.warning("Empty or invalid response from OpenAI for custom content")
                return "Unable to generate AI analysis at this time. Please try again later."
                
        except Exception as e:
            logger.error(f"Error generating custom content with OpenAI: {e}")
            return "Unable to generate AI analysis at this time. Please try again later."
    
    def _build_email_prompt(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult,
        customer_name: str
    ) -> str:
        """Build personalized prompt for email content generation"""
        risk_level = anomaly_result.risk_level.value.upper()
        amount = f"${transaction.amount:.2f}"
        merchant = transaction.merchant_name
        timestamp = transaction.timestamp.strftime("%B %d, %Y at %I:%M %p")
        confidence = f"{anomaly_result.confidence_score * 100:.1f}%"
        
        # Format anomaly types in a user-friendly way
        anomaly_descriptions = {
            "unusual_amount": f"an unusually large transaction amount ({amount})",
            "unusual_time": f"a transaction made at an unusual time ({transaction.timestamp.strftime('%I:%M %p')})",
            "unusual_location": "a transaction from an unexpected location",
            "unusual_merchant": f"a transaction with an uncommon merchant type ({merchant})",
            "velocity_spike": "multiple rapid transactions in a short time period",
            "amount_pattern": "a suspiciously round transaction amount that may indicate fraud",
            "geographic_outlier": "a transaction from a location far from your usual spending areas"
        }
        
        detected_anomalies = []
        for anomaly_type in anomaly_result.anomaly_types:
            description = anomaly_descriptions.get(anomaly_type.value, f"unusual {anomaly_type.value.replace('_', ' ')}")
            detected_anomalies.append(description)
        
        anomaly_explanation = ", ".join(detected_anomalies) if detected_anomalies else "suspicious transaction patterns"
        
        # Determine urgency and action based on risk level
        if risk_level == "CRITICAL":
            urgency = "URGENT ACTION REQUIRED"
            action_tone = "immediate"
            security_advice = "Your card has been temporarily suspended for your protection. Please contact us immediately."
        elif risk_level == "HIGH":
            urgency = "Immediate Attention Needed"
            action_tone = "prompt"
            security_advice = "Please verify this transaction immediately and review your recent account activity."
        elif risk_level == "MEDIUM":
            urgency = "Security Alert"
            action_tone = "timely"
            security_advice = "Please review this transaction and contact us if you did not authorize it."
        else:
            urgency = "Transaction Notice"
            action_tone = "your earliest convenience"
            security_advice = "This transaction has been flagged for your awareness. Please review when convenient."
        
        # Build location context if available
        location_context = ""
        if hasattr(transaction, 'location') and transaction.location:
            city = transaction.location.get('city', 'Unknown')
            state = transaction.location.get('state', 'Unknown')
            if state in ['JP', 'UK', 'AE', 'RU', 'TH', 'CN', 'DE', 'FR']:
                location_context = f" from {city}, {state} (international location)"
            else:
                location_context = f" in {city}, {state}"
        
        prompt = f"""
Write a highly personalized, professional security alert email for a {risk_level.lower()} risk financial transaction.

=== CUSTOMER INFORMATION ===
Customer Name: {customer_name}
Transaction ID: {transaction.id}

=== TRANSACTION DETAILS ===
- Amount: {amount}
- Merchant: {merchant}
- Date & Time: {timestamp}
- Location: {location_context if location_context else 'Standard location'}
- Category: {transaction.merchant_category.value.replace('_', ' ').title()}

=== SECURITY ANALYSIS ===
- Risk Level: {risk_level}
- AI Confidence: {confidence}
- Detected Issues: {anomaly_explanation}
- Context: Transaction occurred{location_context}

=== EMAIL REQUIREMENTS ===
1. **Subject Line**: Professional banking subject (NO EMOJIS) mentioning the specific transaction concern
2. **Personal Greeting**: Formal business greeting addressing {customer_name} personally
3. **Transaction Summary**: Present transaction details in organized, formal business format
4. **Security Analysis**: Explain why transaction triggered security system using professional language
5. **Action Required**: {urgency} - Provide clear, numbered action steps
6. **Contact Information**: Multiple professional contact methods for immediate assistance
7. **Professional Banking Footer**: Standard financial institution closing
8. **Formatting**: Use **bold** for critical information (amounts, dates, merchant names)
9. **NO EMOJIS**: Maintain strict professional banking communication standards

=== TONE GUIDELINES ===
- **STRICTLY PROFESSIONAL**: Banking industry standard communication
- **NO EMOJIS OR CASUAL LANGUAGE**: Formal business correspondence only
- **CLEAR AND DIRECT**: Structured information presentation with proper formatting
- **SECURITY-FOCUSED**: Emphasize protective measures and fraud prevention
- **ACTIONABLE**: Specific steps with clear instructions and contact information
- **APPROPRIATELY URGENT**: Risk level {risk_level.lower()} requires {action_tone} response tone
- **CUSTOMER-CENTRIC**: Protective and helpful while maintaining professional boundaries

{security_advice}

Format your response as:
SUBJECT: [Your personalized subject line]

BODY:
[Your complete personalized email body]

Make this email feel like it was written specifically for {customer_name} about this exact transaction at {merchant} for {amount}.
"""
        return prompt
    
    def _build_phone_script_prompt(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult,
        customer_name: str
    ) -> str:
        """Build prompt for phone script generation"""
        risk_level = anomaly_result.risk_level.value.upper()
        amount = f"${transaction.amount:.2f}"
        merchant = transaction.merchant_name
        timestamp = transaction.timestamp.strftime("%Y-%m-%d at %I:%M %p")
        
        prompt = f"""
Generate a brief, professional phone call script for an automated security alert call about a {risk_level.lower()} risk financial transaction.

Customer: {customer_name}
Transaction: {amount} at {merchant} on {timestamp}
Risk Level: {risk_level}

Requirements:
1. Keep the script under 60 seconds when spoken (approximately 150-180 words)
2. Start with a clear identification of the caller as FinancePulse Security
3. Explain the purpose of the call concisely
4. Provide key transaction details
5. Give clear next steps for both authorized and unauthorized transactions
6. End with a professional closing
7. Use natural, conversational language that sounds good when spoken
8. Include a callback number for customer assistance
9. Be appropriately urgent for {risk_level.lower()} risk level

The script should sound natural and professional when converted to speech. Use simple, clear language appropriate for a security notification call.
"""
        return prompt
    
    def _parse_email_response(self, content: str) -> Tuple[str, str]:
        """Parse OpenAI response to extract subject and body"""
        try:
            # Split content into subject and body
            lines = content.strip().split('\n')
            subject = ""
            body = ""
            body_started = False
            
            for line in lines:
                line = line.strip()
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("BODY:"):
                    body_started = True
                elif body_started:
                    body += line + "\n"
                elif not subject and ":" in line and not body_started:
                    # Might be a subject line without "SUBJECT:" prefix
                    subject = line
            
            # Clean up body
            body = body.strip()
            
            # If no clear separation, try to identify subject as first line
            if not subject and not body:
                lines = content.strip().split('\n', 1)
                subject = lines[0] if lines else "Security Alert: Transaction Anomaly Detected"
                body = lines[1] if len(lines) > 1 else content
            
            return subject or "Security Alert: Transaction Anomaly Detected", body or content
            
        except Exception as e:
            logger.error(f"Error parsing email response: {e}")
            return "Security Alert: Transaction Anomaly Detected", content
    
    def _fallback_email_content(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult,
        customer_name: str
    ) -> Tuple[str, str]:
        """Enhanced fallback email content when OpenAI is not available"""
        risk_level = anomaly_result.risk_level.value.upper()
        amount = f"${transaction.amount:.2f}"
        merchant = transaction.merchant_name
        timestamp = transaction.timestamp.strftime("%B %d, %Y at %I:%M %p")
        
        # Create personalized subject based on transaction details
        if anomaly_result.risk_level.value == "critical":
            subject = f"CRITICAL: Unusual {amount} transaction at {merchant} - {customer_name}"
        elif anomaly_result.risk_level.value == "high":
            subject = f"HIGH RISK: {amount} transaction requires verification - {customer_name}"
        elif anomaly_result.risk_level.value == "medium":
            subject = f"Security Alert: {amount} transaction at {merchant} - {customer_name}"
        else:
            subject = f"Transaction Notice: {amount} at {merchant} - {customer_name}"
        
        # Get context about the anomaly
        anomaly_descriptions = []
        for anomaly_type in anomaly_result.anomaly_types:
            if anomaly_type.value == "unusual_amount":
                anomaly_descriptions.append(f"The transaction amount ({amount}) is significantly higher than your typical spending")
            elif anomaly_type.value == "unusual_time":
                hour = transaction.timestamp.hour
                time_desc = "very early morning" if hour < 6 else "late night" if hour > 22 else "unusual"
                anomaly_descriptions.append(f"This transaction occurred during {time_desc} hours ({transaction.timestamp.strftime('%I:%M %p')})")
            elif anomaly_type.value == "unusual_location":
                anomaly_descriptions.append("This transaction was made from a location that differs from your usual spending areas")
            elif anomaly_type.value == "unusual_merchant":
                anomaly_descriptions.append(f"The merchant type ({merchant}) is different from your typical purchases")
            else:
                anomaly_descriptions.append(f"Unusual {anomaly_type.value.replace('_', ' ')} detected")
        
        anomaly_explanation = ". ".join(anomaly_descriptions) if anomaly_descriptions else "Our AI system has flagged this transaction as potentially suspicious"
        
        # Determine urgency level
        if risk_level == "CRITICAL":
            urgency_message = "URGENT: Your account may be compromised. Please take immediate action."
            action_urgency = "immediately"
        elif risk_level == "HIGH":
            urgency_message = "This transaction requires your immediate attention and verification."
            action_urgency = "as soon as possible"
        elif risk_level == "MEDIUM":
            urgency_message = "Please review this transaction to ensure it was authorized by you."
            action_urgency = "at your earliest convenience"
        else:
            urgency_message = "We're notifying you of this transaction for your awareness."
            action_urgency = "when convenient"
        
        body = f"""Dear {customer_name},

{urgency_message}

Our advanced fraud detection system has identified suspicious activity on your FinancePulse account:

━━━ TRANSACTION DETAILS ━━━
• Amount: {amount}
• Merchant: {merchant}
• Date & Time: {timestamp}
• Transaction ID: {transaction.id}
• Risk Level: {risk_level}

━━━ WHY THIS WAS FLAGGED ━━━
{anomaly_explanation}.

Our AI confidence level for this detection is {anomaly_result.confidence_score * 100:.1f}%.

━━━ IMMEDIATE ACTIONS REQUIRED ━━━
Please take the following steps {action_urgency}:

1. VERIFY: Did you make this transaction?
   • If YES: No further action needed
   • If NO: Continue to step 2 immediately

2. SECURE: If unauthorized, protect your account:
   • Call our 24/7 Security Hotline: 1-800-FINANCE
   • Consider temporarily freezing your card
   • Change your online banking password

3. MONITOR: Check your recent transactions for other unauthorized activity

Thank you for banking with FinancePulse. Your security is our top priority.

Best regards,
FinancePulse Security Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This is an automated security notification.
For immediate assistance, call 1-800-FINANCE or visit our website."""
        
        return subject, body
    
    def _fallback_phone_script(
        self, 
        transaction: Transaction, 
        anomaly_result: AnomalyResult,
        customer_name: str
    ) -> str:
        """Fallback phone script when OpenAI is not available"""
        amount = f"${transaction.amount:.2f}"
        merchant = transaction.merchant_name
        risk_level = anomaly_result.risk_level.value.lower()
        
        return f"""Hello {customer_name}, this is an automated security alert from FinancePulse. 

We've detected {risk_level} risk suspicious activity on your account. A transaction of {amount} at {merchant} has been flagged by our fraud detection system.

If you authorized this transaction, no action is needed. However, if this transaction was not made by you, please call us immediately at 1-800-FINANCE to secure your account.

For your security, we recommend reviewing your recent account activity. Thank you for banking with FinancePulse. Goodbye."""


# Global service instance
openai_service = OpenAIService()