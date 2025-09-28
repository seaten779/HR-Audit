# 🛡️ FinancePulse Intelligent Voice Calling System

## Overview
This consolidated script brings all FinancePulse voice calling functionality into a single file for easy testing and demonstration. When customers call, they simply say their name and the system automatically explains their flagged transaction with full details.

## 🚀 How to Run
```bash
cd D:\f2\financepulse\hackgtcedar
python call-ai-simple.py
```

The server will start on http://localhost:5000

## 📞 How It Works
1. **Customer calls** your Twilio number
2. **System greets them**: "Hello! This is FinancePulse Fraud Prevention. Please tell me your first name..."
3. **Customer says their name**: "John", "I'm Sarah", or "My name is Mike"
4. **System automatically looks up** their flagged transaction
5. **System explains in detail** why it was flagged, including:
   - Transaction amount and merchant
   - Location and time
   - Why it's suspicious (5 specific reasons)
   - Their normal spending patterns for comparison
   - Next steps to take

## 👥 Test Customers Available

### John Smith - CRITICAL Risk
- **Transaction**: $1,250.00 at Electronics Superstore
- **Location**: Las Vegas, NV at 2:30 AM
- **Why Flagged**: Amount 400% higher than normal, outside usual hours, 280 miles from home
- **Phone**: +15551234567

### Sarah Johnson - HIGH Risk  
- **Transaction**: $850.00 ATM Withdrawal
- **Location**: Mexico City, Mexico at 11:45 PM
- **Why Flagged**: Foreign country, exceeds daily limit, no travel notification
- **Phone**: +15559876543

### Michael Chen - CRITICAL Risk
- **Transaction**: $2,500.00 at Online Gaming Store
- **Location**: Unknown (Online) at 3:15 AM  
- **Why Flagged**: Largest purchase ever, high-risk category, unusual IP location
- **Phone**: +15555678901

## 🔧 Setup Instructions

### 1. Start the Voice System
```bash
python call-ai-simple.py
```

### 2. Set up ngrok (for webhooks)
```bash
ngrok http 5000
```

### 3. Update Twilio Webhook
- Go to your Twilio Console
- Update voice webhook URL to: `https://your-ngrok-url.ngrok.io/voice`

### 4. Test the System
- Call your Twilio number: **+16403568689**
- When prompted, say: "John", "Sarah", or "Mike" 
- Listen to the detailed fraud explanation

## 🌐 Web Interface
Visit http://localhost:5000 to see:
- System status
- List of all flagged customers
- Test endpoints for each customer
- Setup instructions

## 🔗 API Endpoints
- `/health` - System status and customer list
- `/customers` - View all flagged customers
- `/test-fraud/john` - Test John's fraud alert
- `/test-fraud/sarah` - Test Sarah's fraud alert  
- `/test-fraud/mike` - Test Mike's fraud alert
- `/voice` - Twilio voice webhook (POST)
- `/gather` - Speech processing (POST)

## 💡 Key Features
- **Smart Name Detection**: Recognizes "John", "I am Sarah", "My name is Mike"
- **Detailed Fraud Explanations**: 5 specific reasons why each transaction was flagged
- **Pattern Comparison**: Shows normal vs. suspicious behavior
- **Risk Levels**: CRITICAL, HIGH, MEDIUM, LOW
- **Live Twilio Integration**: Makes real calls when credentials are provided
- **Demo Mode**: Works without Twilio for testing

## 🔒 Environment Variables (Optional for Live Calls)
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token  
TWILIO_PHONE_NUMBER=+16403568689
```

Without these, the system runs in demo mode and logs calls to console.

## 📋 Example Call Flow
1. **System**: "Hello! This is FinancePulse Fraud Prevention. Please tell me your first name..."
2. **Customer**: "John"
3. **System**: "Hello John Smith, this is FinancePulse Fraud Prevention. We detected suspicious activity... $1,250.00 at Electronics Superstore in Las Vegas, NV at 2:30 AM... flagged because transaction amount is 400% higher than your average purchase..."

## 🎯 Perfect for Demonstrations
- Simple to run: just one Python file
- Instant customer lookup by name
- Realistic fraud scenarios with detailed explanations
- Professional voice responses
- Easy to customize customer data

The system is now ready to use! Just run the script and start making test calls.