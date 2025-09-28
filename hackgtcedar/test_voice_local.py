#!/usr/bin/env python3
"""
Test the voice integration locally without needing ngrok
"""
import requests
import json

# Test the /health endpoint
print("Testing server health...")
try:
    health_response = requests.get("http://localhost:5000/health")
    print(f"Health check: {health_response.status_code}")
    print(f"Response: {health_response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

print("\n" + "="*50)

# Test the /voice endpoint (simulating Twilio webhook)
print("Testing voice webhook...")
try:
    voice_data = {
        'CallSid': 'test-call-123',
        'From': '+12102517978',
        'CallStatus': 'in-progress'
    }
    
    voice_response = requests.post("http://localhost:5000/voice", data=voice_data)
    print(f"Voice webhook: {voice_response.status_code}")
    print(f"TwiML Response:")
    print(voice_response.text)
except Exception as e:
    print(f"Voice webhook test failed: {e}")

print("\n" + "="*50)

# Test the /gather endpoint (simulating speech recognition)
print("Testing speech processing with API trigger...")
try:
    gather_data = {
        'CallSid': 'test-call-123',
        'SpeechResult': 'run api test',
        'Confidence': '0.95'
    }
    
    gather_response = requests.post("http://localhost:5000/gather", data=gather_data)
    print(f"Speech processing: {gather_response.status_code}")
    print(f"TwiML Response:")
    print(gather_response.text)
except Exception as e:
    print(f"Speech processing test failed: {e}")