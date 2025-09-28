"""
Twilio webhook handlers for FinancePulse
Handles TwiML generation and call status updates
"""

import logging
from fastapi import APIRouter, Request, Response, HTTPException, Form
from fastapi.responses import PlainTextResponse
from typing import Optional, Dict, Any
import urllib.parse

from app.services.phone_service import phone_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/twilio", tags=["twilio"])


@router.post("/twiml")
async def generate_twiml(request: Request, script: Optional[str] = None):
    """Generate TwiML for phone calls"""
    try:
        # Get script from query parameter or form data
        if not script:
            query_params = request.query_params
            script = query_params.get('script')
            
        if not script:
            # Try to get from form data
            form_data = await request.form()
            script = form_data.get('script')
            
        if not script:
            script = "Hello, this is a security alert from FinancePulse. Please contact us immediately."
            
        # URL decode the script
        script = urllib.parse.unquote(script)
        
        # Generate TwiML
        twiml = phone_service.generate_twiml(script)
        
        logger.info(f"Generated TwiML for call: {script[:50]}...")
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error generating TwiML: {e}")
        # Return basic TwiML as fallback
        fallback_twiml = '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Security alert from FinancePulse</Say></Response>'
        return Response(content=fallback_twiml, media_type="application/xml")


@router.post("/status")
async def handle_call_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    AccountSid: str = Form(...),
    To: str = Form(...),
    From: str = Form(...),
    CallDuration: Optional[str] = Form(None),
    RecordingUrl: Optional[str] = Form(None),
    RecordingSid: Optional[str] = Form(None)
):
    """Handle call status updates from Twilio"""
    try:
        logger.info(f"📞 Call status update - SID: {CallSid}, Status: {CallStatus}")
        
        # Log call details
        call_info = {
            "call_sid": CallSid,
            "status": CallStatus,
            "account_sid": AccountSid,
            "to": To,
            "from": From,
            "duration": CallDuration,
            "recording_url": RecordingUrl,
            "recording_sid": RecordingSid
        }
        
        # Update call log in phone service
        if hasattr(phone_service, 'call_log'):
            # Find and update the corresponding call record
            for call_record in phone_service.call_log:
                if call_record.get('call_sid') == CallSid:
                    call_record.update({
                        'final_status': CallStatus,
                        'duration': CallDuration,
                        'recording_url': RecordingUrl
                    })
                    break
        
        # Handle different call statuses
        if CallStatus == 'completed':
            logger.info(f"✅ Call {CallSid} completed successfully")
        elif CallStatus == 'failed':
            logger.error(f"❌ Call {CallSid} failed")
        elif CallStatus == 'busy':
            logger.warning(f"📞 Call {CallSid} - line was busy")
        elif CallStatus == 'no-answer':
            logger.warning(f"📞 Call {CallSid} - no answer")
        elif CallStatus == 'canceled':
            logger.info(f"🚫 Call {CallSid} was canceled")
            
        # TODO: Add custom logic here for handling different call outcomes
        # For example, retry logic for failed calls, logging to database, etc.
        
        return {"status": "received", "call_sid": CallSid}
        
    except Exception as e:
        logger.error(f"Error handling call status: {e}")
        raise HTTPException(status_code=500, detail="Error processing call status")


@router.post("/voice")
async def handle_incoming_call(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    CallStatus: str = Form(...)
):
    """Handle incoming calls (if needed for interactive responses)"""
    try:
        logger.info(f"📞 Incoming call - SID: {CallSid}, From: {From}")
        
        # For security notifications, we typically don't handle incoming calls
        # But this endpoint can be used for interactive responses
        
        # Generate TwiML to handle the incoming call
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say voice="Polly.Joanna">
                Thank you for calling FinancePulse Security. 
                If this is regarding a security alert, please press 1. 
                Otherwise, please visit our website or contact customer service.
            </Say>
            <Gather numDigits="1" action="/api/v1/twilio/gather" method="POST">
                <Say>Press 1 for security alerts, or any other key for general information.</Say>
            </Gather>
        </Response>'''
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        raise HTTPException(status_code=500, detail="Error processing incoming call")


@router.post("/gather")
async def handle_user_input(
    Digits: str = Form(...),
    CallSid: str = Form(...),
    From: str = Form(...)
):
    """Handle user input from phone keypad"""
    try:
        logger.info(f"📱 User input - Digits: {Digits}, Call: {CallSid}")
        
        if Digits == "1":
            # User pressed 1 for security alerts
            twiml = '''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="Polly.Joanna">
                    For security concerns, please call our dedicated security line 
                    or check your email for detailed information about any recent alerts.
                    Thank you for using FinancePulse.
                </Say>
            </Response>'''
        else:
            # General information
            twiml = '''<?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say voice="Polly.Joanna">
                    For general information, please visit our website or contact customer service.
                    Thank you for calling FinancePulse.
                </Say>
            </Response>'''
        
        return Response(content=twiml, media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling user input: {e}")
        raise HTTPException(status_code=500, detail="Error processing user input")


@router.get("/test")
async def test_webhook():
    """Test endpoint to verify webhook connectivity"""
    return {
        "status": "ok", 
        "message": "Twilio webhook endpoint is accessible",
        "configured": bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)
    }