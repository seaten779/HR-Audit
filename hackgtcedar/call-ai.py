#!/usr/bin/env python3
"""
Twilio-Cedar OS Direct Voice Integration Server
Direct integration between Twilio voice calls and Cedar OS AI agent
"""

import os
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Core dependencies
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Twilio
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

# HTTP requests
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'twilio_cedar_integration.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app with SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Twilio configuration
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
twilio_client = Client(twilio_account_sid, twilio_auth_token) if twilio_account_sid and twilio_auth_token else None

# Cedar OS configuration
cedar_os_endpoint = os.getenv('CEDAR_OS_API_ENDPOINT', 'http://localhost:8080/api')
cedar_os_voice_endpoint = os.getenv('CEDAR_OS_VOICE_ENDPOINT', 'http://localhost:8080/api/voice')
cedar_os_api_key = os.getenv('CEDAR_OS_API_KEY')
cedar_os_ai_model = os.getenv('CEDAR_OS_AI_MODEL', 'gpt-4-turbo')

# Application state
active_calls: Dict[str, Dict[str, Any]] = {}
conversation_history: Dict[str, list] = {}

# Removed complex VoiceProcessor - using direct Twilio voice integration

class CedarOSInterface:
    """Direct interface for communicating with Cedar OS AI agent"""
    
    def __init__(self):
        self.session = requests.Session()
        if cedar_os_api_key:
            self.session.headers.update({'Authorization': f'Bearer {cedar_os_api_key}'})
    
    def get_ai_response(self, user_input: str, call_sid: str) -> str:
        """Get AI response from Cedar OS for voice input"""
        try:
            # Get conversation history for context
            history = conversation_history.get(call_sid, [])
            
            payload = {
                'message': user_input,
                'call_sid': call_sid,
                'conversation_history': history,
                'model': cedar_os_ai_model,
                'timestamp': datetime.utcnow().isoformat(),
                'voice_mode': True  # Indicate this is for voice response
            }
            
            response = self.session.post(
                f"{cedar_os_voice_endpoint}/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', 'I apologize, but I could not process your request.')
                
                # Update conversation history
                if call_sid not in conversation_history:
                    conversation_history[call_sid] = []
                
                conversation_history[call_sid].extend([
                    {'role': 'user', 'content': user_input, 'timestamp': datetime.utcnow().isoformat()},
                    {'role': 'assistant', 'content': ai_response, 'timestamp': datetime.utcnow().isoformat()}
                ])
                
                # Keep only last 20 messages to prevent memory issues
                if len(conversation_history[call_sid]) > 20:
                    conversation_history[call_sid] = conversation_history[call_sid][-20:]
                
                logger.info(f"Cedar OS AI response for call {call_sid}: {ai_response[:100]}...")
                return ai_response
            else:
                logger.error(f"Cedar OS API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Cedar OS interface error: {e}")
        
        return "I'm sorry, I'm having trouble connecting to my AI system right now. Please try again later."
    
    def get_greeting(self, call_sid: str, caller_number: str) -> str:
        """Get personalized greeting from Cedar OS"""
        try:
            payload = {
                'action': 'greeting',
                'call_sid': call_sid,
                'caller_number': caller_number,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            response = self.session.post(
                f"{cedar_os_voice_endpoint}/greeting",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('greeting', 'Hello! I\'m your Cedar OS AI assistant. How can I help you today?')
                
        except Exception as e:
            logger.error(f"Error getting Cedar OS greeting: {e}")
        
        return "Hello! I'm your Cedar OS AI assistant. How can I help you today?"

# Initialize Cedar OS interface
cedar_interface = CedarOSInterface()

def make_voice_call(to_number: str, from_number: str = None) -> Optional[str]:
    """Initiate a Twilio call that will connect to Cedar OS"""
    if not twilio_client:
        logger.error("Twilio client not initialized")
        return None
    
    from_number = from_number or twilio_phone_number
    webhook_base = os.getenv('PUBLIC_BASE_URL', 'http://localhost:5000')
    
    try:
        call = twilio_client.calls.create(
            to=to_number,
            from_=from_number,
            url=f"{webhook_base}/voice-webhook",
            method="POST",
            record=True,  # Enable call recording
            recording_status_callback=f"{webhook_base}/recording-callback"
        )
        
        logger.info(f"Call initiated! SID: {call.sid}")
        
        # Initialize call session
        active_calls[call.sid] = {
            'call_sid': call.sid,
            'to_number': to_number,
            'from_number': from_number,
            'status': 'initiated',
            'created_at': datetime.utcnow().isoformat(),
            'context': cedar_interface.get_voice_context(call.sid)
        }
        
        return call.sid
        
    except Exception as e:
        logger.error(f"Error making call: {e}")
        return None

# ========== API ENDPOINTS ==========

@app.route('/make-call', methods=['POST'])
def api_make_call():
    """API endpoint to initiate calls"""
    try:
        data = request.get_json() or {}
        to_number = data.get('to', "+12102517978")
        from_number = data.get('from', twilio_phone_number)
        
        if not to_number:
            return jsonify({"success": False, "error": "'to' number is required"}), 400
        
        call_sid = make_voice_call(to_number, from_number)
        
        if call_sid:
            # Emit to frontend via WebSocket
            socketio.emit('call_initiated', {
                'call_sid': call_sid,
                'to_number': to_number,
                'from_number': from_number
            })
            
            return jsonify({
                "success": True, 
                "call_sid": call_sid,
                "message": "Call initiated successfully"
            })
        else:
            return jsonify({"success": False, "error": "Failed to initiate call"}), 500
            
    except Exception as e:
        logger.error(f"Error in make_call endpoint: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/voice-webhook', methods=['POST'])
def voice_webhook():
    """Handle incoming Twilio voice webhook with direct Cedar OS integration"""
    response = VoiceResponse()
    call_sid = request.form.get('CallSid')
    caller_number = request.form.get('From')
    call_status = request.form.get('CallStatus')
    
    logger.info(f"Voice webhook - Call SID: {call_sid}, Status: {call_status}, From: {caller_number}")
    
    # Initialize call tracking
    if call_sid not in active_calls:
        active_calls[call_sid] = {
            'call_sid': call_sid,
            'caller': caller_number,
            'status': 'connected',
            'created_at': datetime.utcnow().isoformat()
        }
    
    # Get personalized greeting from Cedar OS
    greeting_text = cedar_interface.get_greeting(call_sid, caller_number)
    
    # Say the greeting
    response.say(greeting_text, voice='alice')
    
    # Use Gather to listen for speech input and redirect to process the response
    gather = response.gather(
        input='speech',
        timeout=5,
        speech_timeout='auto',
        action=f'/process-speech?CallSid={call_sid}',
        method='POST',
        language='en-US'
    )
    
    # If no speech detected, prompt again
    response.say("I didn't hear anything. Please speak your question or request.", voice='alice')
    response.redirect(f'/voice-webhook?CallSid={call_sid}')
    
    # Emit call connected event
    socketio.emit('call_connected', {
        'call_sid': call_sid,
        'caller': caller_number,
        'status': 'connected'
    })
    
    return str(response)

@app.route('/process-speech', methods=['POST'])
def process_speech():
    """Process speech input from Twilio and get Cedar OS AI response"""
    response = VoiceResponse()
    call_sid = request.args.get('CallSid') or request.form.get('CallSid')
    speech_result = request.form.get('SpeechResult')
    confidence = request.form.get('Confidence')
    
    logger.info(f"Speech processed for call {call_sid}: '{speech_result}' (confidence: {confidence})")
    
    if call_sid not in active_calls:
        response.say("I'm sorry, I can't find your call session. Please try again.", voice='alice')
        response.hangup()
        return str(response)
    
    try:
        if speech_result and speech_result.strip():
            # Get AI response from Cedar OS
            ai_response = cedar_interface.get_ai_response(speech_result, call_sid)
            
            # Update call info
            active_calls[call_sid]['last_input'] = speech_result
            active_calls[call_sid]['last_response'] = ai_response
            active_calls[call_sid]['last_updated'] = datetime.utcnow().isoformat()
            
            # Speak the AI response using Twilio's built-in TTS
            response.say(ai_response, voice='alice')
            
            # Emit conversation update to frontend
            socketio.emit('conversation_update', {
                'call_sid': call_sid,
                'user_input': speech_result,
                'ai_response': ai_response,
                'timestamp': datetime.utcnow().isoformat(),
                'confidence': confidence
            })
            
        else:
            response.say("I didn't understand what you said. Could you please repeat that?", voice='alice')
        
        # Continue the conversation by gathering more speech
        gather = response.gather(
            input='speech',
            timeout=5,
            speech_timeout='auto',
            action=f'/process-speech?CallSid={call_sid}',
            method='POST',
            language='en-US'
        )
        
        # If no more speech, offer to end or continue
        response.say("Is there anything else I can help you with? Say goodbye to end the call.", voice='alice')
        response.redirect(f'/process-speech?CallSid={call_sid}')
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        response.say("I'm sorry, I encountered an error. Let me try again.", voice='alice')
        response.redirect(f'/voice-webhook?CallSid={call_sid}')
    
    return str(response)

# Additional utility endpoints

@app.route('/serve-audio/<filename>')
def serve_audio(filename):
    """Serve temporary audio files"""
    try:
        audio_path = f"/tmp/{filename}"
        if os.path.exists(audio_path):
            return send_file(audio_path, mimetype='audio/wav')
        else:
            return "Audio file not found", 404
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        return "Error serving audio", 500

@app.route('/send-message-to-call', methods=['POST'])
def send_message_to_call():
    """Send a message from Cedar OS to the active call"""
    try:
        data = request.get_json()
        call_sid = data.get('call_sid')
        message = data.get('message')
        audio_url = data.get('audio_url')  # Optional: URL to audio file
        
        if call_sid not in active_calls:
            return jsonify({'error': 'Call not found'}), 404
        
        if not twilio_client:
            return jsonify({'error': 'Twilio client not initialized'}), 500
        
        # For this simplified version, we'll store the message to be played on next recording cycle
        active_calls[call_sid]['pending_message'] = message
        
        # Emit message to frontend
        socketio.emit('message_queued', {
            'call_sid': call_sid,
            'message': message
        })
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error sending message to call: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-active-calls')
def get_active_calls():
    """Get list of active calls for the frontend"""
    return jsonify({'active_calls': active_calls, 'count': len(active_calls)})

@app.route('/get-call-details/<call_sid>')
def get_call_details(call_sid):
    """Get detailed information about a specific call"""
    if call_sid in active_calls:
        return jsonify(active_calls[call_sid])
    else:
        return jsonify({'error': 'Call not found'}), 404

@app.route('/end-call', methods=['POST'])
def end_call():
    """End an active call"""
    try:
        data = request.get_json()
        call_sid = data.get('call_sid')
        
        if call_sid in active_calls:
            if twilio_client:
                try:
                    # End the call
                    call = twilio_client.calls(call_sid).update(status='completed')
                    logger.info(f"Call {call_sid} ended successfully")
                except Exception as e:
                    logger.error(f"Error ending call via Twilio: {e}")
            
            # Remove from active calls
            call_info = active_calls.pop(call_sid, {})
            
            # Emit call ended event
            socketio.emit('call_ended', {
                'call_sid': call_sid,
                'reason': 'user_ended'
            })
            
            return jsonify({'success': True, 'message': 'Call ended successfully'})
        else:
            return jsonify({'error': 'Call not found'}), 404
            
    except Exception as e:
        logger.error(f"Error in end_call endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'twilio_configured': twilio_client is not None,
        'cedar_os_configured': cedar_os_endpoint is not None,
        'cedar_os_endpoint': cedar_os_endpoint,
        'active_calls_count': len(active_calls),
        'conversation_sessions': len(conversation_history),
        'timestamp': datetime.utcnow().isoformat(),
        'integration_type': 'Direct Twilio-Cedar OS Voice Integration'
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected to WebSocket")
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected from WebSocket")

@socketio.on('request_call_status')
def handle_call_status_request(data):
    """Handle request for call status"""
    call_sid = data.get('call_sid')
    if call_sid and call_sid in active_calls:
        emit('call_status_update', {
            'call_sid': call_sid,
            'status': active_calls[call_sid]
        })
    else:
        emit('call_status_error', {'error': 'Call not found'})

# Serve the React frontend (if built)
@app.route('/')
def index():
    """Serve the main React application"""
    try:
        return render_template('index.html')
    except:
        return jsonify({
            'message': 'Twilio-Cedar OS Voice Integration API',
            'status': 'running',
            'endpoints': [
                '/make-call',
                '/voice-webhook', 
                '/get-active-calls',
                '/end-call',
                '/health'
            ]
        })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Main application runner
if __name__ == '__main__':
    logger.info("🌲 Starting Twilio-Cedar OS Direct Voice Integration Server...")
    
    # Validate configuration
    if not twilio_account_sid or not twilio_auth_token:
        logger.warning("❌ Twilio credentials not configured - call functionality will be disabled")
    
    if not cedar_os_endpoint:
        logger.warning("❌ Cedar OS endpoint not configured - AI responses will use fallback")
    
    # Configuration summary
    logger.info("📋 Configuration Summary:")
    logger.info(f"  🌐 Flask Host: {os.getenv('FLASK_HOST', '0.0.0.0')}")
    logger.info(f"  🔌 Flask Port: {os.getenv('FLASK_PORT', 5000)}")
    logger.info(f"  🐛 Debug Mode: {os.getenv('FLASK_DEBUG', 'true')}")
    logger.info(f"  🌍 Public Base URL: {os.getenv('PUBLIC_BASE_URL', 'http://localhost:5000')}")
    logger.info(f"  🤖 Cedar OS Endpoint: {cedar_os_endpoint}")
    logger.info(f"  📞 Twilio Configured: {'✅' if twilio_client is not None else '❌'}")
    logger.info(f"  🧠 Cedar OS Configured: {'✅' if cedar_os_endpoint else '❌'}")
    
    logger.info("📝 How it works:")
    logger.info("  1. User calls Twilio number")
    logger.info("  2. Twilio sends speech to our webhook")
    logger.info("  3. We send speech text to Cedar OS AI")
    logger.info("  4. Cedar OS responds with AI answer")
    logger.info("  5. Twilio speaks the AI response to caller")
    
    logger.info("🚀 Setup Instructions:")
    logger.info("  1. Configure .env file with Twilio and Cedar OS credentials")
    logger.info("  2. Start ngrok: ngrok http 5000")
    logger.info("  3. Update PUBLIC_BASE_URL in .env with ngrok URL")
    logger.info("  4. Ensure Cedar OS is running and accessible")
    logger.info("  5. Test with /health endpoint")
    logger.info("  6. Call your Twilio number to test!")
    
    # Start the application
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    try:
        logger.info(f"🌲 Starting server on {host}:{port}")
        socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        logger.info("👋 Server stopped by user")
    except Exception as e:
        logger.error(f"💥 Failed to start server: {e}")
        raise
