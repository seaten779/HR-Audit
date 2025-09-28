# 🌲 Cedar OS Direct Voice Integration

A direct, seamless integration between Twilio voice calls and your Cedar OS AI agent. When someone calls your Twilio number, they'll speak directly with your AI agent!

## ✨ Features

- **📞 Direct Voice Calls**: Your Cedar OS AI agent answers phone calls directly
- **🤖 Natural Conversations**: Callers speak naturally with your AI using Twilio's speech recognition
- **🔊 Built-in Text-to-Speech**: AI responses are spoken back using Twilio's voice synthesis
- **📱 Real-time Dashboard**: Monitor active calls and conversations as they happen
- **🔄 Live Updates**: WebSocket-powered real-time conversation tracking
- **📊 Conversation History**: Full transcript logging with confidence scores
- **🎨 Modern Interface**: Clean, responsive React dashboard
- **⚡ Zero Complex Setup**: No Google Cloud or external services needed

## 🏗️ How It Works

```
📞 Caller dials your Twilio number
        ↓
🎙️  Twilio converts speech to text
        ↓
🤖 Your Flask server sends text to Cedar OS AI
        ↓
🧠 Cedar OS AI generates intelligent response
        ↓
🔊 Twilio speaks the AI response back to caller
        ↓
📱 Dashboard shows conversation in real-time
```

**It's that simple!** No complex cloud services, no audio processing - just direct communication between your caller and your AI agent.

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+** 
- **Twilio Account** with phone number
- **Cedar OS** AI agent running
- **ngrok** (for webhook URLs during development)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd twilio-cedar-integration

# Run the automated setup script
python setup.py
```

### 2. Configure Environment

Edit the `.env` file with your actual credentials:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_actual_account_sid
TWILIO_AUTH_TOKEN=your_actual_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Google Cloud Configuration  
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT_ID=your_project_id

# Cedar OS Configuration
CEDAR_OS_API_ENDPOINT=http://your-cedar-os-instance:8080/api
CEDAR_OS_API_KEY=your_cedar_os_api_key

# Webhook URLs (update with your ngrok URL)
PUBLIC_BASE_URL=https://your-subdomain.ngrok.io
```

### 3. Start Services

**Terminal 1 - Backend Server:**
```bash
python call-ai.py
# Or use: ./start-server.sh
```

**Terminal 2 - Frontend Dashboard:**
```bash
npm start
# Or use: ./start-frontend.sh
```

**Terminal 3 - ngrok (for webhooks):**
```bash
ngrok http 5000
```

### 4. Update Webhook URL

After starting ngrok, update your `.env` file:
```env
PUBLIC_BASE_URL=https://your-ngrok-subdomain.ngrok.io
```

Then restart the backend server.

## 📱 Usage

1. **Open the dashboard**: http://localhost:3000
2. **Check system status**: Ensure all services show ✅
3. **Make a test call**: Enter a phone number and click "Start Call"
4. **Monitor conversations**: View real-time transcripts and AI responses
5. **Manage calls**: End calls, view history, and track analytics

## 🔧 API Endpoints

### Health Check
```
GET /health
```
Returns system status and configuration.

### Make Call
```
POST /make-call
Content-Type: application/json

{
  "to": "+1234567890",
  "from": "+0987654321" // optional
}
```

### End Call
```
POST /end-call
Content-Type: application/json

{
  "call_sid": "CAxxxxxxxxxxxxx"
}
```

### Get Active Calls
```
GET /get-active-calls
```

### Voice Webhooks (Twilio)
```
POST /voice-webhook
POST /process-recording
POST /transcription-callback
POST /recording-callback
```

## 🔌 WebSocket Events

### Client → Server
- `request_call_status`: Request status for a specific call

### Server → Client
- `call_initiated`: New call started
- `call_connected`: Call connected successfully  
- `conversation_update`: New transcript/response available
- `call_ended`: Call terminated
- `message_queued`: Message queued for call

## 🎛️ Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID | ✅ |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token | ✅ |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google service account JSON | ✅ |
| `GOOGLE_CLOUD_PROJECT_ID` | Google Cloud project ID | ✅ |
| `CEDAR_OS_API_ENDPOINT` | Cedar OS API base URL | ✅ |
| `CEDAR_OS_API_KEY` | Cedar OS API authentication key | ❓ |
| `PUBLIC_BASE_URL` | Public URL for webhooks | ✅ |
| `FLASK_HOST` | Flask server host | ❓ |
| `FLASK_PORT` | Flask server port | ❓ |
| `FLASK_DEBUG` | Enable debug mode | ❓ |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | ❓ |
| `GOOGLE_SPEECH_TO_TEXT_ENABLED` | Enable Google STT | ❓ |
| `GOOGLE_TEXT_TO_SPEECH_ENABLED` | Enable Google TTS | ❓ |

## 🔍 Troubleshooting

### Common Issues

**1. "Twilio client not initialized"**
- Check your `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
- Verify credentials in Twilio Console

**2. "Google Cloud clients not initialized"**
- Verify `GOOGLE_APPLICATION_CREDENTIALS` path
- Ensure the service account JSON file exists
- Check Google Cloud project permissions

**3. "Cedar OS interface error"**
- Verify `CEDAR_OS_API_ENDPOINT` is accessible
- Check Cedar OS instance is running
- Validate API key if required

**4. "Webhook URL not accessible"**
- Ensure ngrok is running: `ngrok http 5000`
- Update `PUBLIC_BASE_URL` with current ngrok URL
- Restart the backend server after updating

**5. "Call audio issues"**
- Check Twilio phone number configuration
- Verify webhook URLs are publicly accessible
- Review call logs in Twilio Console

### Debug Mode

Enable detailed logging:
```env
LOG_LEVEL=DEBUG
FLASK_DEBUG=true
```

### Logs

Check the log file:
```bash
tail -f twilio_cedar_integration.log
```

## 📊 Monitoring

### Health Endpoint
Monitor system status:
```bash
curl http://localhost:5000/health
```

### Dashboard Metrics
The web dashboard provides:
- Real-time system status
- Active call count
- Service configuration status
- Call history and analytics
- Conversation transcripts

## 🔒 Security Considerations

1. **API Keys**: Store all API keys securely, never commit to version control
2. **Webhooks**: Use HTTPS URLs for production webhooks
3. **CORS**: Configure appropriate CORS settings for production
4. **Rate Limiting**: Implement rate limiting for production deployments
5. **Authentication**: Add authentication for production dashboards

## 🚀 Production Deployment

### Environment Setup
- Use a production WSGI server (gunicorn, uWSGI)
- Configure reverse proxy (nginx, Apache)
- Set up SSL certificates
- Use production databases for call storage
- Implement proper logging and monitoring

### Example Production Config
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 call-ai:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the inline code documentation
- **Logs**: Review application logs for detailed error information

## 🔄 Version History

### v1.0.0
- ✅ Twilio voice call integration
- ✅ Cedar OS AI connection
- ✅ Google Cloud Speech services
- ✅ Real-time web dashboard
- ✅ WebSocket communication
- ✅ Call recording and transcription
- ✅ Modern React frontend

---

**Made with ❤️ for Cedar OS Integration**
