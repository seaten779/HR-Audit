// Cedar-OS Streaming Types and Interfaces
// Replacing WebSocket with Cedar-OS streaming capabilities

export interface CedarStreamConfig {
  endpoint: string;
  channels: string[];
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  debug?: boolean;
}

export interface CedarStream {
  connect(): Promise<void>;
  disconnect(): void;
  subscribe(channel: string, handler: CedarEventHandler): void;
  unsubscribe(channel: string, handler?: CedarEventHandler): void;
  send(channel: string, data: any): Promise<void>;
  getStatus(): CedarStreamStatus;
  on(event: CedarStreamEvent, handler: Function): void;
  off(event: CedarStreamEvent, handler: Function): void;
}

export type CedarStreamStatus = 
  | 'connecting'
  | 'connected'
  | 'disconnected'
  | 'reconnecting'
  | 'error';

export type CedarStreamEvent = 
  | 'connect'
  | 'disconnect'
  | 'reconnect'
  | 'error'
  | 'status_change';

export interface CedarEvent<T = any> {
  type: string;
  channel: string;
  data: T;
  timestamp: string;
  id?: string;
  source?: string;
}

export type CedarEventHandler<T = any> = (event: CedarEvent<T>) => void;

// Specific event types for FinancePulse
export interface TransactionStreamEvent extends CedarEvent {
  type: 'transaction';
  channel: 'transactions';
  data: {
    transaction: {
      id: string;
      account_id: string;
      customer_id: string;
      amount: number;
      type: string;
      merchant_name: string;
      merchant_category: string;
      timestamp: string;
      description?: string;
    };
    anomaly: {
      is_anomaly: boolean;
      confidence_score: number;
      risk_level: "low" | "medium" | "high" | "critical";
      anomaly_types: string[];
      explanation?: string;
      recommendations?: string[];
    } | null;
  };
}

export interface NotificationStreamEvent extends CedarEvent {
  type: 'notification_popup';
  channel: 'notifications';
  data: {
    type: string;
    message: string;
    customer_id: string;
    customer_name: string;
    email?: string;
    phone?: string;
    risk_level: string;
    timestamp: string;
  };
}

export interface SystemStreamEvent extends CedarEvent {
  type: 'system_status';
  channel: 'system';
  data: {
    status: 'healthy' | 'warning' | 'error';
    component: string;
    message: string;
    timestamp: string;
  };
}

// Cedar-OS specific stream types
export type CedarStreamChannel = 
  | 'transactions'
  | 'notifications'
  | 'system'
  | 'alerts'
  | 'analytics';

export interface CedarStreamMetrics {
  messagesReceived: number;
  messagesProcessed: number;
  errorsCount: number;
  lastMessageTime: string;
  connectionUptime: number;
  averageLatency: number;
}

export interface CedarStreamError {
  code: string;
  message: string;
  timestamp: string;
  context?: Record<string, any>;
  recoverable: boolean;
}

// Configuration for different environments
export interface CedarStreamEnvironmentConfig {
  development: CedarStreamConfig;
  staging: CedarStreamConfig;
  production: CedarStreamConfig;
}