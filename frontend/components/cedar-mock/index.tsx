import React, { useState, useEffect } from 'react';

// Mock CedarChat component
export function CedarChat({ 
  agent, 
  initialMessages = [], 
  onMessageSent, 
  onMessageReceived, 
  className = "", 
  placeholder = "Type a message...",
  showTypingIndicator = false 
}: {
  agent: any;
  initialMessages?: any[];
  onMessageSent?: (message: any) => void;
  onMessageReceived?: (message: any) => void;
  className?: string;
  placeholder?: string;
  showTypingIndicator?: boolean;
}) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    onMessageSent?.(userMessage);
    setInput('');
    setIsProcessing(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: `ai_${Date.now()}`,
        type: 'assistant',
        content: `I understand you're asking about: "${input}". As FinancePulse AI, I'm analyzing your request and will provide insights based on the current transaction data and anomaly patterns.`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiResponse]);
      onMessageReceived?.(aiResponse);
      setIsProcessing(false);
    }, 1500);
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.type === 'system'
                  ? 'bg-orange-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className="text-xs opacity-75 mt-1">
                {new Date(message.timestamp).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {(isProcessing || showTypingIndicator) && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-900 p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={placeholder}
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isProcessing}
          />
          <button
            onClick={handleSendMessage}
            disabled={isProcessing || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

// Mock CedarState component
export function CedarState({ state }: { state: any }) {
  // This is just a provider component that would normally manage global state
  // For now, we'll just store it in a context or global variable
  useEffect(() => {
    // Store global state for the application
    (window as any).__cedarState = state;
  }, [state]);

  return null;
}

// Mock CedarSpell type
export interface CedarSpell {
  id: string;
  name: string;
  description: string;
  category: string;
  parameters: Record<string, any>;
  executable: boolean;
}