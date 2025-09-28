#!/usr/bin/env python3
"""
HR Audit Intelligent Voice Calling System with Capital One API Integration
Integrates both intelligent fraud detection calling and Capital One API functionality
"""

import os
import logging
import sys
import subprocess
import asyncio
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, render_template_string
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from twilio import twiml
import json
from datetime import datetime
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging without emojis
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'simple-twilio-test')

# Capital One API Configuration
API_KEY = os.environ.get('API_KEY')

# HR Audit Voice Calling Configuration
class FinancePulseVoiceCaller:
    """Intelligent voice calling system for fraud alerts"""
    
    def __init__(self):
        # Configuration
        self.demo_mode = True
        self.twilio_client = None
        self.calls_made = 0
        self.successful_calls = 0
        self.call_history = []
        
        # Initialize Twilio if credentials are available
        self._initialize_twilio()
    
    def _initialize_twilio(self):
        """Initialize Twilio client from environment variables"""
        try:
            twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
            twilio_token = os.getenv('TWILIO_AUTH_TOKEN') 
            twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
            
            if all([twilio_sid, twilio_token, twilio_phone]):
                self.twilio_client = Client(twilio_sid, twilio_token)
                self.twilio_phone_number = twilio_phone
                self.demo_mode = False
                logger.info("Twilio initialized for live calls")
                print(f"Live calling enabled with number: {twilio_phone}")
            else:
                logger.info("Twilio credentials not found - running in demo mode")
                print("Demo mode: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER for live calls")
        except Exception as e:
            logger.error(f"Twilio initialization failed: {e}")
            print(f"Twilio setup failed: {e}")
    
    def generate_fraud_alert_script(self, customer_name: str, transaction_amount: float, 
                                  merchant: str, risk_level: str = "HIGH", 
                                  location: str = "Unknown") -> str:
        """Generate a personalized fraud alert script"""
        
        urgency_map = {
            "CRITICAL": "requires your immediate attention",
            "HIGH": "needs your prompt response", 
            "MEDIUM": "should be verified",
            "LOW": "requires verification"
        }
        
        urgency_text = urgency_map.get(risk_level.upper(), "requires verification")
        
        # Create personalized script
        script = f"""Hello {customer_name}, this is the HR Audit Security Team.
We detected a ${transaction_amount:.2f} transaction at {merchant} that {urgency_text}. 
This was flagged because the transaction pattern is unusual for your account. 
Your account is secure, but we need you to verify this transaction immediately. 
Please call us at 1-800-FRAUD-HELP or check your FinancePulse app. 
Thank you for helping us protect your account."""
        
        return script.strip()
    
    async def make_fraud_alert_call(self, customer_name: str, phone_number: str,
                                  transaction_amount: float = 250.00, 
                                  merchant: str = "Unknown Merchant",
                                  risk_level: str = "HIGH") -> Dict[str, Any]:
        """Make an intelligent fraud alert call"""
        
        # Generate personalized script
        script = self.generate_fraud_alert_script(
            customer_name, transaction_amount, merchant, risk_level
        )
        
        if self.demo_mode:
            return await self._simulate_call(customer_name, phone_number, script, 
                                           transaction_amount, merchant, risk_level)
        else:
            return await self._make_live_call(customer_name, phone_number, script,
                                            transaction_amount, merchant, risk_level)
    
    async def _simulate_call(self, customer_name: str, phone_number: str, script: str,
                           transaction_amount: float, merchant: str, risk_level: str) -> Dict[str, Any]:
        """Simulate a fraud alert call with detailed logging"""
        
        call_id = f"fraud_call_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Simulate call success based on risk level
        success_rates = {"CRITICAL": 0.95, "HIGH": 0.90, "MEDIUM": 0.85, "LOW": 0.80}
        success = random.random() < success_rates.get(risk_level, 0.85)
        duration = random.randint(45, 120) if success else 0
        
        # Enhanced logging
        print("==" + "="*70)
        print(f"INTELLIGENT FRAUD ALERT CALL - ID: {call_id}")
        print(f"Customer: {customer_name}")
        print(f"Phone: {self._mask_phone(phone_number)}")
        print(f"Transaction: ${transaction_amount:.2f} at {merchant}")
        print(f"Risk Level: {risk_level}")
        print(f"Call Status: {'COMPLETED' if success else 'FAILED'}")
        print(f"Duration: {duration} seconds" if success else "Duration: No answer/Failed")
        print(f"Script Length: {len(script)} characters ({len(script.split())} words)")
        print("PERSONALIZED FRAUD SCRIPT:")
        print(f'   "{script}"')
        print("==" + "="*70)
        
        self.calls_made += 1
        if success:
            self.successful_calls += 1
        
        call_result = {
            "success": success,
            "call_id": call_id,
            "call_sid": f"demo_{call_id}",
            "status": "completed" if success else "failed",
            "customer_name": customer_name,
            "phone_number": self._mask_phone(phone_number),
            "transaction_amount": transaction_amount,
            "merchant": merchant,
            "risk_level": risk_level,
            "script_words": len(script.split()),
            "duration_seconds": duration,
            "demo_mode": True,
            "timestamp": datetime.now().isoformat()
        }
        
        self.call_history.append(call_result)
        return call_result
    
    async def _make_live_call(self, customer_name: str, phone_number: str, script: str,
                            transaction_amount: float, merchant: str, risk_level: str) -> Dict[str, Any]:
        """Make a real Twilio call"""
        
        try:
            # Create TwiML with the script
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
            
            print(f"LIVE FRAUD CALL INITIATED: {call.sid}")
            print(f"Customer: {customer_name}")
            print(f"Phone: {self._mask_phone(phone_number)}")
            print(f"Transaction: ${transaction_amount:.2f} at {merchant}")
            print(f"Risk Level: {risk_level}")
            
            call_result = {
                "success": True,
                "call_sid": call.sid,
                "status": "initiated", 
                "customer_name": customer_name,
                "phone_number": self._mask_phone(phone_number),
                "transaction_amount": transaction_amount,
                "merchant": merchant,
                "risk_level": risk_level,
                "demo_mode": False,
                "timestamp": datetime.now().isoformat()
            }
            
            self.call_history.append(call_result)
            return call_result
            
        except Exception as e:
            logger.error(f"Live call failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to make live call: {e}"
            }
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for privacy"""
        if len(phone) < 4:
            return "***"
        return phone[:-4] + "****"
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """Get call statistics"""
        return {
            "total_calls_made": self.calls_made,
            "successful_calls": self.successful_calls,
            "success_rate": (self.successful_calls / max(1, self.calls_made)) * 100,
            "demo_mode": self.demo_mode,
            "provider": "twilio" if not self.demo_mode else "demo",
            "call_history_count": len(self.call_history)
        }
    
    def list_recent_calls(self, limit: int = 5) -> List[Dict]:
        """List recent calls"""
        return self.call_history[-limit:] if self.call_history else []

# Initialize the voice caller
voice_caller = FinancePulseVoiceCaller()

# Simple Customer Transaction Database
CUSTOMER_TRANSACTIONS = {
    "john": {
        "name": "John Smith",
        "phone": "+15551234567",
        "flagged_transaction": {
            "amount": 1250.00,
            "merchant": "Electronics Superstore",
            "location": "Las Vegas, NV",
            "time": "2:30 AM",
            "date": "September 28, 2024",
            "risk_level": "CRITICAL",
            "reasons": [
                "Transaction amount is 400% higher than your average purchase",
                "Purchase made at 2:30 AM, outside your normal hours (9 AM - 8 PM)",
                "Location is 280 miles from your home in Austin, TX",
                "First time purchasing from this merchant",
                "High-risk merchant category for fraud"
            ]
        },
        "normal_spending": {
            "avg_amount": 85.50,
            "usual_location": "Austin, TX",
            "usual_hours": "9 AM - 8 PM",
            "common_merchants": ["HEB Grocery", "Shell Gas Station", "Starbucks"]
        }
    },
    "sarah": {
        "name": "Sarah Johnson",
        "phone": "+15559876543",
        "flagged_transaction": {
            "amount": 850.00,
            "merchant": "ATM Withdrawal",
            "location": "Mexico City, Mexico",
            "time": "11:45 PM",
            "date": "September 28, 2024",
            "risk_level": "HIGH",
            "reasons": [
                "ATM withdrawal in foreign country (Mexico)",
                "Amount exceeds your daily withdrawal limit",
                "Transaction made at 11:45 PM",
                "No travel notification on file",
                "ATM located in high-fraud area"
            ]
        },
        "normal_spending": {
            "avg_amount": 125.00,
            "usual_location": "Denver, CO",
            "usual_hours": "8 AM - 9 PM",
            "common_merchants": ["King Soopers", "Target", "Amazon"]
        }
    },
    "mike": {
        "name": "Michael Chen",
        "phone": "+15555678901",
        "flagged_transaction": {
            "amount": 2500.00,
            "merchant": "Online Gaming Store",
            "location": "Unknown (Online)",
            "time": "3:15 AM",
            "date": "September 28, 2024",
            "risk_level": "CRITICAL",
            "reasons": [
                "Largest single purchase in your account history",
                "Online gaming purchases flagged as high-risk category",
                "Transaction made at 3:15 AM",
                "Multiple failed authentication attempts before purchase",
                "IP address shows unusual geographic location"
            ]
        },
        "normal_spending": {
            "avg_amount": 95.75,
            "usual_location": "Seattle, WA",
            "usual_hours": "7 AM - 10 PM",
            "common_merchants": ["Whole Foods", "Amazon", "Uber"]
        }
    }
}

def generate_fraud_explanation(customer_name):
    """Generate detailed fraud explanation for a customer"""
    customer_key = customer_name.lower().strip()
    
    if customer_key not in CUSTOMER_TRANSACTIONS:
        return f"I'm sorry, I don't have any flagged transactions for {customer_name}. Your account appears to be secure."
    
    customer_data = CUSTOMER_TRANSACTIONS[customer_key]
    transaction = customer_data["flagged_transaction"]
    normal = customer_data["normal_spending"]
    
    explanation = f"""Hello {customer_data['name']}, this is FinancePulse Fraud Prevention. 

We detected suspicious activity on your account and need to verify a transaction immediately.

Here are the details:
- Amount: ${transaction['amount']:,.2f} at {transaction['merchant']}
- Location: {transaction['location']}
- Time: {transaction['time']} on {transaction['date']}
- Risk Level: {transaction['risk_level']}

This transaction was flagged because:
{chr(10).join(f'  • {reason}' for reason in transaction['reasons'])}

For comparison, your normal spending pattern is:
  • Average purchase: ${normal['avg_amount']:,.2f}
  • Usual location: {normal['usual_location']}
  • Typical hours: {normal['usual_hours']}
  • Common merchants: {', '.join(normal['common_merchants'])}

If you did NOT make this transaction, please call us immediately at 1-800-FRAUD-HELP or text STOP to freeze your card.

If you DID make this transaction, please call us to verify and remove the fraud flag.

Your account security is our top priority. Thank you."""
    
    return explanation

# Capital One API Functions
def run_capital_one_api():
    """Execute the Capital One API script and return results"""
    try:
        logger.info("Running Capital One API script...")
        
        # Create a new customer
        new_customer = {
            "first_name": "John",
            "last_name": "Doe",
            "address": {
                "street_number": "123",
                "street_name": "Main St",
                "city": "Austin",
                "state": "TX",
                "zip": "78701"
            }
        }
        
        customer_url = f"http://api.nessieisreal.com/customers?key={API_KEY}"
        customer_res = requests.post(customer_url, json=new_customer)
        
        if customer_res.status_code != 201:
            return "Sorry, I encountered an error creating a customer account with the API."
        
        customer_data = customer_res.json()
        customer_id = None
        
        # Extract customer ID
        if isinstance(customer_data, dict):
            if "objectCreated" in customer_data and "_id" in customer_data["objectCreated"]:
                customer_id = customer_data["objectCreated"]["_id"]
            elif "_id" in customer_data:
                customer_id = customer_data["_id"]
        
        if not customer_id:
            return "Sorry, I couldn't create a customer account properly."
        
        # Create an account
        new_account = {
            "type": "Credit Card",
            "nickname": "Test Checking",
            "balance": 5000,
            "rewards": 100
        }
        
        account_url = f"http://api.nessieisreal.com/customers/{customer_id}/accounts?key={API_KEY}"
        account_res = requests.post(account_url, json=new_account)
        
        if account_res.status_code != 201:
            return "Sorry, I encountered an error creating an account."
        
        account_data = account_res.json()
        account_id = None
        
        # Extract account ID
        if isinstance(account_data, dict):
            if "objectCreated" in account_data and "_id" in account_data["objectCreated"]:
                account_id = account_data["objectCreated"]["_id"]
            elif "_id" in account_data:
                account_id = account_data["_id"]
        
        if not account_id:
            return "Sorry, I couldn't create an account properly."
        
        # Create a purchase
        new_purchase_data = {
            "merchant_id": "57cf75cea73e494d8675ec49",
            "medium": "balance",
            "purchase_date": "2024-09-27",
            "amount": 25.99,
            "description": "Sample purchase transaction"
        }
        
        purchase_url = f"http://api.nessieisreal.com/accounts/{account_id}/purchases?key={API_KEY}"
        purchase_res = requests.post(purchase_url, json=new_purchase_data)
        
        if purchase_res.status_code == 201:
            return f"Great! I successfully created a customer account, credit card account with $5000 balance, and processed a sample transaction of $25.99. The Capital One API integration is working perfectly!"
        else:
            return f"I created the customer and account successfully, but had a small issue with the transaction. The main API functionality is working!"
            
    except Exception as e:
        logger.error(f"Error running Capital One API: {e}")
        return "Sorry, I encountered an error while running the Capital One API integration."

# AI Conversation Scripts and Responses
AI_SCRIPTS = {
    # Banking/Capital One Script
    "banking": {
        "greeting": "Hello! I'm your Capital One API assistant. I can help you test the banking API integration. What would you like me to do?",
        "responses": {
            "api": "I'll run the Capital One API script right now!",
            "test": "Let me test the API integration for you!",
            "demo": "I'll demonstrate the Capital One API functionality!",
            "capital one": "Running the Capital One API integration now!",
            "banking": "Let me execute the banking API script!",
            "create account": "I'll create a test account using the API!"
        }
    },
    # FinancePulse Fraud Detection Script
    "financepulse": {
        "greeting": "Hello! I'm your FinancePulse Fraud Prevention AI assistant. I can help you test our intelligent voice calling system for fraud alerts. What would you like me to do?",
        "responses": {
            "fraud": "I'll demonstrate our fraud alert calling system!",
            "call": "Let me make a test fraud alert call!",
            "alert": "I'll trigger a fraud alert call for you!",
            "test call": "Running a test fraud detection call now!",
            "financepulse": "Let me show you the FinancePulse fraud calling system!",
            "security": "I'll run a security alert call demonstration!",
            "demo call": "Making a demo fraud alert call!"
        }
    },
    # Customer Service Script
    "customer_service": {
        "greeting": "Thank you for calling our customer service line. I'm your AI assistant. How can I help you today?",
        "responses": {
            "billing": "I'd be happy to help you with your billing inquiry. Can you please provide your account number?",
            "technical": "I can help you with technical support. What device or service are you having trouble with?",
            "cancel": "I understand you'd like to cancel your service. Let me connect you with a specialist who can help with that.",
            "complaint": "I'm sorry to hear about your experience. I want to make sure we resolve this for you. Can you tell me more about what happened?"
        }
    }
}

# Simple fallback responses
SIMPLE_RESPONSES = {
    "hello": "Hello! I'm your Capital One API assistant. Say 'run API' or 'test API' to execute the Capital One integration!",
    "how are you": "I'm doing great! Thanks for asking. I'm ready to run the Capital One API for you!",
    "weather": "I don't have real-time weather data, but I can run the Capital One API integration for you!",
    "time": f"The current time is {datetime.now().strftime('%I:%M %p')}. Would you like me to run the API test?",
    "thank you": "You're very welcome! Would you like me to run the Capital One API integration?",
    "goodbye": "Thank you for calling! Have a wonderful day!",
    "default": "I heard you say something. Try saying 'run API', 'test API', or 'demo' to execute the Capital One integration!"
}

# Current active script (change this to switch conversation modes)
ACTIVE_SCRIPT = "banking"  # Options: "banking", "customer_service", or None for simple responses

def get_ai_response(user_text, is_first_call=False):
    """Generate AI response based on user input and active script"""
    user_text_lower = user_text.lower()
    
    # If this is the first call, use a simple fraud prevention greeting
    if is_first_call:
        return "Hello! This is FinancePulse Fraud Prevention. Please tell me your first name so I can look up any flagged transactions on your account."
    
    # Check for customer names first
    customer_names = ["john", "sarah", "mike", "michael"]
    for name in customer_names:
        if name in user_text_lower:
            logger.info(f"Customer name '{name}' detected in: '{user_text}'")
            return generate_fraud_explanation(name)
    
    # Check for "I am" or "my name is" patterns
    if "i am" in user_text_lower or "my name is" in user_text_lower:
        # Try to extract the name
        words = user_text_lower.split()
        for i, word in enumerate(words):
            if word in ["am", "is"] and i + 1 < len(words):
                potential_name = words[i + 1].strip()
                if potential_name in CUSTOMER_TRANSACTIONS:
                    logger.info(f"Customer identified as: '{potential_name}'")
                    return generate_fraud_explanation(potential_name)
    
    # Check for Capital One API trigger words
    api_triggers = ["api", "test", "demo", "capital one", "banking", "create account", "run", "execute"]
    if any(trigger in user_text_lower for trigger in api_triggers):
        logger.info(f"API trigger detected in: '{user_text}'")
        return run_capital_one_api()
    
    # Check for fraud-related keywords
    fraud_keywords = ["fraud", "transaction", "flagged", "suspicious", "alert"]
    if any(keyword in user_text_lower for keyword in fraud_keywords):
        return "I can help you with fraud alerts. Please tell me your first name - John, Sarah, or Mike - and I'll look up your flagged transactions."
    
    # Fall back to simple responses
    for keyword, response in SIMPLE_RESPONSES.items():
        if keyword in user_text_lower:
            return response
    
    return "Please tell me your first name so I can check for any flagged transactions. We have alerts for John, Sarah, or Mike."

@app.route('/')
def index():
    """Simple web interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FinancePulse Voice Integration Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .status { padding: 20px; border-radius: 8px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .success { background: #d4edda; border: 1px solid #c3e6cb; }
            .info { background: #d1ecf1; border: 1px solid #bee5eb; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; }
            .customer { background: #e7f3ff; border: 1px solid #b3d7ff; margin: 10px 0; padding: 15px; }
            .critical { border-left: 5px solid #dc3545; }
            .high { border-left: 5px solid #fd7e14; }
            h1 { color: #2c3e50; text-align: center; }
            h3 { color: #34495e; margin-top: 0; }
            code { background: #f8f9fa; padding: 4px 8px; border-radius: 4px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ FinancePulse Voice Integration</h1>
            
            <div class="status success">
                <h3>✅ Server Status: RUNNING</h3>
                <p>FinancePulse Fraud Detection Voice System is active on port 5000</p>
            </div>
            
            <div class="grid">
                <div>
                    <div class="status info">
                        <h3>🚀 Test Your Integration:</h3>
                        <ol>
                            <li>Start ngrok: <code>ngrok http 5000</code></li>
                            <li>Update Twilio webhook URL to: <code>https://your-ngrok-url.ngrok.io/voice</code></li>
                            <li>Call your Twilio number</li>
                            <li>Say your name: <strong>"John"</strong>, <strong>"Sarah"</strong>, or <strong>"Mike"</strong></li>
                        </ol>
                    </div>
                    
                    <div class="status info">
                        <h3>🔗 Available Endpoints:</h3>
                        <ul>
                            <li><a href="/health">/health</a> - System status & customer list</li>
                            <li><a href="/customers">/customers</a> - View all flagged customers</li>
                            <li><a href="/test-fraud/john">/test-fraud/john</a> - Test John's fraud alert</li>
                            <li><a href="/test-fraud/sarah">/test-fraud/sarah</a> - Test Sarah's fraud alert</li>
                            <li><a href="/test-fraud/mike">/test-fraud/mike</a> - Test Mike's fraud alert</li>
                            <li>/voice - Voice webhook (POST)</li>
                            <li>/gather - Speech processing (POST)</li>
                        </ul>
                    </div>
                </div>
                
                <div>
                    <div class="status warning">
                        <h3>👥 Customers with Flagged Transactions:</h3>
                        
                        <div class="customer critical">
                            <strong>John Smith</strong> - CRITICAL Risk<br>
                            💰 $1,250.00 at Electronics Superstore<br>
                            📍 Las Vegas, NV at 2:30 AM<br>
                            <small>Say "John" to hear his fraud alert</small>
                        </div>
                        
                        <div class="customer high">
                            <strong>Sarah Johnson</strong> - HIGH Risk<br>
                            💰 $850.00 ATM Withdrawal<br>
                            📍 Mexico City, Mexico at 11:45 PM<br>
                            <small>Say "Sarah" to hear her fraud alert</small>
                        </div>
                        
                        <div class="customer critical">
                            <strong>Michael Chen</strong> - CRITICAL Risk<br>
                            💰 $2,500.00 at Online Gaming Store<br>
                            📍 Unknown (Online) at 3:15 AM<br>
                            <small>Say "Mike" to hear his fraud alert</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="status info">
                <h3>📞 How It Works:</h3>
                <ol>
                    <li><strong>Customer calls</strong> the Twilio number</li>
                    <li><strong>System greets them</strong> and asks for their name</li>
                    <li><strong>Customer says their name</strong> (e.g., "I'm John" or just "John")</li>
                    <li><strong>System looks up</strong> their flagged transaction</li>
                    <li><strong>System explains</strong> why the transaction was flagged with full details</li>
                    <li><strong>Customer can verify</strong> if the transaction was legitimate or not</li>
                </ol>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'FinancePulse Voice Integration',
        'timestamp': datetime.now().isoformat(),
        'endpoints': ['/voice', '/gather', '/health', '/test-fraud', '/customers'],
        'customers': list(CUSTOMER_TRANSACTIONS.keys())
    })

@app.route('/test-fraud/<customer_name>')
def test_fraud(customer_name):
    """Test fraud explanation for a customer"""
    explanation = generate_fraud_explanation(customer_name)
    return jsonify({
        'customer': customer_name,
        'explanation': explanation,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/customers')
def list_customers():
    """List all customers with flagged transactions"""
    customers = {}
    for key, data in CUSTOMER_TRANSACTIONS.items():
        customers[key] = {
            'name': data['name'],
            'phone': data['phone'],
            'risk_level': data['flagged_transaction']['risk_level'],
            'amount': data['flagged_transaction']['amount'],
            'merchant': data['flagged_transaction']['merchant']
        }
    return jsonify(customers)

@app.route('/voice', methods=['POST'])
def voice():
    """Handle incoming calls"""
    logger.info("Incoming call received")
    
    response = VoiceResponse()
    
    # Get greeting from active script or use default
    greeting = get_ai_response("", is_first_call=True)
    if not greeting or greeting == SIMPLE_RESPONSES["default"]:
        greeting = "Hello! Welcome to the AI voice assistant. Please say something and I'll respond."
    
    # Welcome message
    response.say(greeting, voice='alice')
    
    # Gather speech input
    gather = response.gather(
        input='speech',
        timeout=5,
        speech_timeout='auto',
        action='/gather',
        method='POST'
    )
    
    # If no input, say goodbye
    response.say(
        "I didn't hear anything. Thanks for calling! Goodbye.",
        voice='alice'
    )
    response.hangup()
    
    logger.info(f"Voice response: {str(response)}")
    return str(response)

@app.route('/gather', methods=['POST'])
def gather():
    """Process speech input and respond"""
    logger.info("Processing speech input")
    
    # Get the speech result from Twilio
    speech_result = request.form.get('SpeechResult', '')
    confidence = request.form.get('Confidence', '0')
    
    logger.info(f"Speech recognized: '{speech_result}' (confidence: {confidence})")
    
    response = VoiceResponse()
    
    if speech_result:
        # Get AI response
        ai_response = get_ai_response(speech_result)
        logger.info(f"AI response: {ai_response}")
        
        # Speak the AI response
        response.say(ai_response, voice='alice')
        
        # Ask if they want to continue
        response.pause(length=1)
        response.say("Would you like to ask me something else?", voice='alice')
        
        # Gather more input
        gather = response.gather(
            input='speech',
            timeout=5,
            speech_timeout='auto',
            action='/gather',
            method='POST'
        )
        
    else:
        response.say(
            "I didn't understand what you said. Please try again.",
            voice='alice'
        )
        
        # Try again
        gather = response.gather(
            input='speech',
            timeout=5,
            speech_timeout='auto',
            action='/gather',
            method='POST'
        )
    
    # Final goodbye if no more input
    response.say("Thanks for calling! Have a great day!", voice='alice')
    response.hangup()
    
    return str(response)

if __name__ == '__main__':
    # Get configuration
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Log startup info
    logger.info("Starting FinancePulse Intelligent Voice Integration Server...")
    logger.info("Configuration Summary:")
    logger.info(f"  Flask Host: {host}")
    logger.info(f"  Flask Port: {port}")
    logger.info(f"  Debug Mode: {debug}")
    logger.info(f"  Voice Caller Mode: {'Live' if not voice_caller.demo_mode else 'Demo'}")
    logger.info(f"  Customers with Flagged Transactions: {len(CUSTOMER_TRANSACTIONS)}")
    logger.info("")
    logger.info("FinancePulse Fraud Detection System:")
    logger.info("  1. Customer calls Twilio number")
    logger.info("  2. System asks for their name")
    logger.info("  3. Customer says name (John, Sarah, or Mike)")
    logger.info("  4. System explains their flagged transaction with details")
    logger.info("  5. Customer can verify if transaction was legitimate")
    logger.info("")
    logger.info("Available Test Customers:")
    for name, data in CUSTOMER_TRANSACTIONS.items():
        transaction = data['flagged_transaction']
        logger.info(f"  - {data['name']}: ${transaction['amount']:,.2f} at {transaction['merchant']} ({transaction['risk_level']})")
    logger.info("")
    logger.info("Setup Instructions:")
    logger.info("  1. Start ngrok: ngrok http 5000")
    logger.info("  2. Update Twilio webhook to: https://your-ngrok-url.ngrok.io/voice")
    logger.info("  3. Call your Twilio number")
    logger.info("  4. Say your name when prompted")
    logger.info("  5. Visit http://localhost:5000 for web interface")
    logger.info("")
    logger.info(f"Starting FinancePulse server on {host}:{port}")
    
    # Start the server
    app.run(host=host, port=port, debug=debug)