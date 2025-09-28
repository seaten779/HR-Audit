import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './App.css';

// Socket.IO connection
const socket = io('http://localhost:5000');

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [activeCalls, setActiveCalls] = useState({});
  const [callHistory, setCallHistory] = useState([]);
  const [currentCall, setCurrentCall] = useState(null);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({});
  const [error, setError] = useState('');
  const conversationEndRef = useRef(null);

  useEffect(() => {
    // Socket connection handlers
    socket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to Cedar OS Voice Integration Server');
    });

    socket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from server');
    });

    socket.on('call_initiated', (data) => {
      console.log('Call initiated:', data);
      setCurrentCall(data);
      setActiveCalls(prev => ({
        ...prev,
        [data.call_sid]: { ...data, status: 'initiated' }
      }));
    });

    socket.on('call_connected', (data) => {
      console.log('Call connected:', data);
      setActiveCalls(prev => ({
        ...prev,
        [data.call_sid]: { ...prev[data.call_sid], ...data, status: 'connected' }
      }));
    });

    socket.on('conversation_update', (data) => {
      console.log('Conversation update:', data);
      setConversationHistory(prev => [...prev, {
        id: Date.now(),
        timestamp: data.timestamp,
        type: 'conversation',
        user_input: data.user_input,
        ai_response: data.ai_response,
        call_sid: data.call_sid,
        confidence: data.confidence
      }]);
      
      // Update current call with latest interaction
      setCurrentCall(prev => prev ? { ...prev, last_interaction: data } : null);
    });

    socket.on('call_ended', (data) => {
      console.log('Call ended:', data);
      setCallHistory(prev => [...prev, {
        ...activeCalls[data.call_sid],
        ended_at: new Date().toISOString(),
        reason: data.reason
      }]);
      
      setActiveCalls(prev => {
        const { [data.call_sid]: ended, ...remaining } = prev;
        return remaining;
      });
      
      if (currentCall && currentCall.call_sid === data.call_sid) {
        setCurrentCall(null);
      }
    });

    socket.on('message_queued', (data) => {
      console.log('Message queued:', data);
    });

    // Cleanup on unmount
    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('call_initiated');
      socket.off('call_connected');
      socket.off('conversation_update');
      socket.off('call_ended');
      socket.off('message_queued');
    };
  }, [activeCalls, currentCall]);

  useEffect(() => {
    // Scroll to bottom of conversation
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversationHistory]);

  useEffect(() => {
    // Fetch system status on mount
    fetchSystemStatus();
    
    // Refresh status every 30 seconds
    const statusInterval = setInterval(fetchSystemStatus, 30000);
    return () => clearInterval(statusInterval);
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('/health');
      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
      }
    } catch (err) {
      console.error('Error fetching system status:', err);
    }
  };

  const initiateCall = async () => {
    if (!phoneNumber.trim()) {
      setError('Please enter a phone number');
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const response = await fetch('/make-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ to: phoneNumber }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log('Call initiated successfully:', result);
        // Socket will handle the call_initiated event
      } else {
        setError(result.error || 'Failed to initiate call');
      }
    } catch (err) {
      console.error('Error initiating call:', err);
      setError('Network error - please try again');
    } finally {
      setIsLoading(false);
    }
  };

  const endCall = async (callSid) => {
    try {
      const response = await fetch('/end-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ call_sid: callSid }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log('Call ended successfully');
        // Socket will handle the call_ended event
      } else {
        setError(result.error || 'Failed to end call');
      }
    } catch (err) {
      console.error('Error ending call:', err);
      setError('Network error - please try again');
    }
  };

  const sendMessageToCall = async (callSid, message) => {
    try {
      const response = await fetch('/send-message-to-call', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ call_sid: callSid, message }),
      });
      
      const result = await response.json();
      
      if (!result.success) {
        setError(result.error || 'Failed to send message');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Network error - please try again');
    }
  };

  const formatPhoneNumber = (value) => {
    const phoneNumber = value.replace(/[^\d]/g, '');
    const phoneNumberLength = phoneNumber.length;
    
    if (phoneNumberLength < 4) return phoneNumber;
    if (phoneNumberLength < 7) {
      return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3)}`;
    }
    return `(${phoneNumber.slice(0, 3)}) ${phoneNumber.slice(3, 6)}-${phoneNumber.slice(6, 10)}`;
  };

  const handlePhoneNumberChange = (e) => {
    const formattedNumber = formatPhoneNumber(e.target.value);
    setPhoneNumber(formattedNumber);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return '#4CAF50';
      case 'initiated': return '#FF9800';
      case 'ringing': return '#2196F3';
      default: return '#757575';
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🌲 Cedar OS Voice Integration</h1>
        <div className="connection-status">
          <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </span>
        </div>
      </header>

      <div className="main-container">
        {/* System Status Panel */}
        <div className="status-panel">
          <h3>System Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Twilio:</span>
              <span className={`status-value ${systemStatus.twilio_configured ? 'enabled' : 'disabled'}`}>
                {systemStatus.twilio_configured ? '✅' : '❌'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Cedar OS AI:</span>
              <span className={`status-value ${systemStatus.cedar_os_configured ? 'enabled' : 'disabled'}`}>
                {systemStatus.cedar_os_configured ? '✅' : '❌'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Integration:</span>
              <span className="status-value enabled">
                Direct Voice
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Active Calls:</span>
              <span className="status-value">
                {systemStatus.active_calls_count || Object.keys(activeCalls).length}
              </span>
            </div>
          </div>
        </div>

        {/* Call Initiation Panel */}
        <div className="call-panel">
          <h3>Initiate Voice Call</h3>
          <div className="call-form">
            <div className="input-group">
              <label htmlFor="phone">Phone Number:</label>
              <input
                id="phone"
                type="tel"
                value={phoneNumber}
                onChange={handlePhoneNumberChange}
                placeholder="(555) 123-4567"
                maxLength={14}
                disabled={isLoading}
              />
            </div>
            <button 
              onClick={initiateCall}
              disabled={isLoading || !phoneNumber.trim()}
              className="call-button"
            >
              {isLoading ? '📞 Calling...' : '📞 Start Call'}
            </button>
          </div>
          {error && <div className="error-message">{error}</div>}
        </div>

        {/* Active Calls Panel */}
        {Object.keys(activeCalls).length > 0 && (
          <div className="active-calls-panel">
            <h3>Active Calls ({Object.keys(activeCalls).length})</h3>
            <div className="calls-list">
              {Object.values(activeCalls).map((call) => (
                <div key={call.call_sid} className="call-item">
                  <div className="call-info">
                    <div className="call-number">{call.to_number || call.caller}</div>
                    <div 
                      className="call-status"
                      style={{ color: getStatusColor(call.status) }}
                    >
                      {call.status}
                    </div>
                    <div className="call-duration">
                      {call.created_at ? new Date(call.created_at).toLocaleTimeString() : ''}
                    </div>
                  </div>
                  <div className="call-actions">
                    <button 
                      onClick={() => setCurrentCall(call)}
                      className="view-button"
                    >
                      👁️ View
                    </button>
                    <button 
                      onClick={() => endCall(call.call_sid)}
                      className="end-button"
                    >
                      📞 End
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Conversation Panel */}
        {currentCall && (
          <div className="conversation-panel">
            <div className="conversation-header">
              <h3>Conversation - {currentCall.to_number || currentCall.caller}</h3>
              <button 
                onClick={() => setCurrentCall(null)}
                className="close-button"
              >
                ✕
              </button>
            </div>
            <div className="conversation-history">
              {conversationHistory
                .filter(item => item.call_sid === currentCall.call_sid)
                .map((item) => (
                  <div key={item.id} className="conversation-item">
                    <div className="timestamp">
                      {new Date(item.timestamp).toLocaleTimeString()}
                      {item.confidence && (
                        <span className="confidence-score"> (confidence: {(parseFloat(item.confidence) * 100).toFixed(0)}%)</span>
                      )}
                    </div>
                    <div className="user-input">
                      <strong>User:</strong> {item.user_input}
                    </div>
                    <div className="ai-response">
                      <strong>Cedar OS AI:</strong> {item.ai_response}
                    </div>
                  </div>
                ))}
              <div ref={conversationEndRef} />
            </div>
            {conversationHistory.filter(item => item.call_sid === currentCall.call_sid).length === 0 && (
              <div className="no-conversation">
                Waiting for conversation to begin...
              </div>
            )}
          </div>
        )}

        {/* Call History Panel */}
        {callHistory.length > 0 && (
          <div className="history-panel">
            <h3>Call History ({callHistory.length})</h3>
            <div className="history-list">
              {callHistory.slice(-10).reverse().map((call, index) => (
                <div key={index} className="history-item">
                  <div className="history-info">
                    <div className="history-number">{call.to_number || call.caller}</div>
                    <div className="history-time">
                      {call.created_at ? new Date(call.created_at).toLocaleString() : ''}
                    </div>
                    <div className="history-reason">{call.reason || 'completed'}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <footer className="app-footer">
        <p>🌲 Cedar OS Direct Voice Integration • Powered by Twilio</p>
        {systemStatus.cedar_os_endpoint && (
          <p>Cedar OS: {systemStatus.cedar_os_endpoint}</p>
        )}
        {systemStatus.integration_type && (
          <p>Mode: {systemStatus.integration_type}</p>
        )}
      </footer>
    </div>
  );
}

export default App;
