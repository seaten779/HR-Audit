// Cedar-OS Streaming Service
// Real-time streaming service that replaces WebSocket functionality

import { 
  CedarStream, 
  CedarStreamConfig, 
  CedarStreamStatus, 
  CedarStreamEvent,
  CedarEvent, 
  CedarEventHandler,
  CedarStreamMetrics,
  CedarStreamError
} from '../types/cedar-stream';

export class CedarStreamService implements CedarStream {
  private config: CedarStreamConfig;
  private status: CedarStreamStatus = 'disconnected';
  private eventSource: EventSource | null = null;
  private eventHandlers = new Map<CedarStreamEvent, Function[]>();
  private channelHandlers = new Map<string, CedarEventHandler[]>();
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private heartbeatTimer: NodeJS.Timeout | null = null;
  private metrics: CedarStreamMetrics = {
    messagesReceived: 0,
    messagesProcessed: 0,
    errorsCount: 0,
    lastMessageTime: '',
    connectionUptime: 0,
    averageLatency: 0
  };
  private connectionStartTime = 0;
  private latencyHistory: number[] = [];

  constructor(config: CedarStreamConfig) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 30000,
      debug: false,
      ...config
    };
  }

  async connect(): Promise<void> {
    if (this.status === 'connected' || this.status === 'connecting') {
      return;
    }

    this.setStatus('connecting');
    this.connectionStartTime = Date.now();

    try {
      // Cedar-OS uses Server-Sent Events (SSE) for streaming
      // This provides a more robust and standardized streaming solution
      const url = new URL('/cedar/stream', this.config.endpoint);
      
      // Add channels as query parameters
      if (this.config.channels.length > 0) {
        url.searchParams.set('channels', this.config.channels.join(','));
      }

      this.eventSource = new EventSource(url.toString());

      this.eventSource.onopen = () => {
        this.log('Cedar-OS stream connected successfully');
        this.setStatus('connected');
        this.reconnectAttempts = 0;
        this.startHeartbeat();
        this.emit('connect');
      };

      this.eventSource.onmessage = (event) => {
        this.handleMessage(event);
      };

      this.eventSource.onerror = (error) => {
        this.log('Cedar-OS stream error:', error);
        this.handleError(error);
      };

      // Handle specific Cedar-OS event types
      this.eventSource.addEventListener('cedar-event', (event) => {
        this.handleCedarEvent(event as MessageEvent);
      });

      this.eventSource.addEventListener('cedar-heartbeat', (event) => {
        this.handleHeartbeat(event as MessageEvent);
      });

    } catch (error) {
      this.log('Failed to connect Cedar-OS stream:', error);
      this.handleError(error);
      throw error;
    }
  }

  disconnect(): void {
    this.log('Disconnecting Cedar-OS stream');
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.setStatus('disconnected');
    this.emit('disconnect');
  }

  subscribe(channel: string, handler: CedarEventHandler): void {
    if (!this.channelHandlers.has(channel)) {
      this.channelHandlers.set(channel, []);
    }
    this.channelHandlers.get(channel)?.push(handler);
    this.log(`Subscribed to channel: ${channel}`);
  }

  unsubscribe(channel: string, handler?: CedarEventHandler): void {
    if (!this.channelHandlers.has(channel)) {
      return;
    }

    if (handler) {
      const handlers = this.channelHandlers.get(channel) || [];
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    } else {
      this.channelHandlers.delete(channel);
    }
    
    this.log(`Unsubscribed from channel: ${channel}`);
  }

  async send(channel: string, data: any): Promise<void> {
    // Cedar-OS streaming is primarily for receiving data
    // For sending data, we use traditional HTTP requests
    const response = await fetch(`${this.config.endpoint}/cedar/send`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ channel, data }),
    });

    if (!response.ok) {
      throw new Error(`Failed to send data to channel ${channel}: ${response.statusText}`);
    }
  }

  getStatus(): CedarStreamStatus {
    return this.status;
  }

  getMetrics(): CedarStreamMetrics {
    const uptime = this.status === 'connected' 
      ? Date.now() - this.connectionStartTime 
      : 0;
    
    return {
      ...this.metrics,
      connectionUptime: uptime,
      averageLatency: this.calculateAverageLatency()
    };
  }

  on(event: CedarStreamEvent, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)?.push(handler);
  }

  off(event: CedarStreamEvent, handler: Function): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const startTime = Date.now();
      const data = JSON.parse(event.data);
      
      this.metrics.messagesReceived++;
      this.metrics.lastMessageTime = new Date().toISOString();

      // Process Cedar-OS event
      if (this.isCedarEvent(data)) {
        this.processCedarEvent(data);
      } else {
        // Legacy format support
        this.processLegacyEvent(data, event);
      }

      this.metrics.messagesProcessed++;
      this.recordLatency(Date.now() - startTime);
      
    } catch (error) {
      this.log('Error processing message:', error);
      this.metrics.errorsCount++;
    }
  }

  private handleCedarEvent(event: MessageEvent): void {
    try {
      const cedarEvent: CedarEvent = JSON.parse(event.data);
      this.processCedarEvent(cedarEvent);
    } catch (error) {
      this.log('Error processing Cedar event:', error);
    }
  }

  private handleHeartbeat(event: MessageEvent): void {
    try {
      const heartbeat = JSON.parse(event.data);
      this.log('Heartbeat received:', heartbeat);
      
      // Update connection health
      if (heartbeat.timestamp) {
        const latency = Date.now() - new Date(heartbeat.timestamp).getTime();
        this.recordLatency(latency);
      }
    } catch (error) {
      this.log('Error processing heartbeat:', error);
    }
  }

  private processCedarEvent(event: CedarEvent): void {
    const handlers = this.channelHandlers.get(event.channel) || [];
    handlers.forEach(handler => {
      try {
        handler(event);
      } catch (error) {
        this.log(`Error in channel handler for ${event.channel}:`, error);
      }
    });
  }

  private processLegacyEvent(data: any, event: MessageEvent): void {
    // Convert legacy WebSocket format to Cedar-OS format
    let cedarEvent: CedarEvent;

    if (data.type === 'transaction') {
      cedarEvent = {
        type: data.type,
        channel: 'transactions',
        data: data.data,
        timestamp: data.timestamp || new Date().toISOString(),
        source: 'legacy-websocket'
      };
    } else if (data.type === 'notification_popup') {
      cedarEvent = {
        type: data.type,
        channel: 'notifications', 
        data: data.data,
        timestamp: data.timestamp || new Date().toISOString(),
        source: 'legacy-websocket'
      };
    } else {
      // Generic event
      cedarEvent = {
        type: data.type || 'unknown',
        channel: 'system',
        data: data,
        timestamp: new Date().toISOString(),
        source: 'legacy-websocket'
      };
    }

    this.processCedarEvent(cedarEvent);
  }

  private isCedarEvent(data: any): data is CedarEvent {
    return data && 
           typeof data.type === 'string' && 
           typeof data.channel === 'string' && 
           data.data !== undefined &&
           typeof data.timestamp === 'string';
  }

  private handleError(error: any): void {
    this.metrics.errorsCount++;
    this.setStatus('error');
    
    const streamError: CedarStreamError = {
      code: error.code || 'STREAM_ERROR',
      message: error.message || 'Unknown stream error',
      timestamp: new Date().toISOString(),
      context: { error },
      recoverable: true
    };

    this.emit('error', streamError);
    
    // Attempt reconnection if enabled
    if (this.reconnectAttempts < (this.config.maxReconnectAttempts || 5)) {
      this.scheduleReconnect();
    } else {
      this.log('Max reconnect attempts reached. Giving up.');
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    this.setStatus('reconnecting');
    this.reconnectAttempts++;
    
    const delay = this.config.reconnectInterval || 3000;
    this.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect().catch(() => {
        // Error handling is done in connect method
      });
    }, delay);

    this.emit('reconnect', { attempt: this.reconnectAttempts, delay });
  }

  private startHeartbeat(): void {
    if (this.heartbeatTimer) {
      return;
    }

    const interval = this.config.heartbeatInterval || 30000;
    this.heartbeatTimer = setInterval(() => {
      this.sendHeartbeat();
    }, interval);
  }

  private async sendHeartbeat(): void {
    try {
      await this.send('system', {
        type: 'heartbeat',
        timestamp: new Date().toISOString(),
        client_id: this.generateClientId()
      });
    } catch (error) {
      this.log('Failed to send heartbeat:', error);
    }
  }

  private setStatus(status: CedarStreamStatus): void {
    if (this.status !== status) {
      const oldStatus = this.status;
      this.status = status;
      this.log(`Status changed: ${oldStatus} -> ${status}`);
      this.emit('status_change', { from: oldStatus, to: status });
    }
  }

  private emit(event: CedarStreamEvent, data?: any): void {
    const handlers = this.eventHandlers.get(event) || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        this.log(`Error in event handler for ${event}:`, error);
      }
    });
  }

  private recordLatency(latency: number): void {
    this.latencyHistory.push(latency);
    
    // Keep only last 100 measurements
    if (this.latencyHistory.length > 100) {
      this.latencyHistory.shift();
    }
  }

  private calculateAverageLatency(): number {
    if (this.latencyHistory.length === 0) {
      return 0;
    }
    
    const sum = this.latencyHistory.reduce((a, b) => a + b, 0);
    return sum / this.latencyHistory.length;
  }

  private generateClientId(): string {
    return `cedar-client-${Date.now()}-${Math.random().toString(36).substring(7)}`;
  }

  private log(...args: any[]): void {
    if (this.config.debug) {
      console.log('[Cedar-OS Stream]', ...args);
    }
  }
}

// Factory function for creating Cedar-OS stream instances
export function createCedarStream(config: CedarStreamConfig): CedarStream {
  return new CedarStreamService(config);
}

// Default configurations for different environments
export const defaultCedarConfigs = {
  development: {
    endpoint: process.env.NEXT_PUBLIC_CEDAR_ENDPOINT || 'http://localhost:8000',
    channels: ['transactions', 'notifications', 'system'],
    reconnectInterval: 2000,
    maxReconnectAttempts: 10,
    heartbeatInterval: 15000,
    debug: true
  },
  staging: {
    endpoint: process.env.NEXT_PUBLIC_CEDAR_ENDPOINT || 'https://staging-api.financepulse.com',
    channels: ['transactions', 'notifications', 'system'],
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000,
    debug: false
  },
  production: {
    endpoint: process.env.NEXT_PUBLIC_CEDAR_ENDPOINT || 'https://api.financepulse.com',
    channels: ['transactions', 'notifications', 'system'],
    reconnectInterval: 5000,
    maxReconnectAttempts: 3,
    heartbeatInterval: 30000,
    debug: false
  }
};

// Get config based on environment
export function getCedarConfig(): CedarStreamConfig {
  const env = process.env.NODE_ENV || 'development';
  return defaultCedarConfigs[env as keyof typeof defaultCedarConfigs] || defaultCedarConfigs.development;
}