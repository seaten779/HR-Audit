// Core financial data types for FinancePulse Cedar-OS integration

export interface Transaction {
  id: string;
  customer_id: string;
  amount: number;
  merchant_name: string;
  merchant_category: string;
  timestamp: string;
  location: {
    city: string;
    state: string;
    country: string;
    lat?: number;
    lng?: number;
  };
  card_id: string;
  type: 'PURCHASE' | 'WITHDRAWAL' | 'TRANSFER' | 'REFUND';
  status: 'PENDING' | 'APPROVED' | 'DECLINED';
  description?: string;
}

export interface AnomalyResult {
  id: string;
  transaction_id: string;
  is_anomaly: boolean;
  confidence_score: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  anomaly_types: AnomalyType[];
  features: Record<string, number>;
  explanation?: string;
  recommended_actions?: string[];
  detected_at: string;
}

export type AnomalyType = 
  | 'UNUSUAL_AMOUNT'
  | 'UNUSUAL_TIME' 
  | 'UNUSUAL_FREQUENCY'
  | 'UNUSUAL_LOCATION'
  | 'UNUSUAL_MERCHANT'
  | 'VELOCITY_SPIKE'
  | 'AMOUNT_PATTERN'
  | 'GEOGRAPHIC_OUTLIER';

export interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  created_at: string;
  risk_profile: 'LOW' | 'MEDIUM' | 'HIGH';
  verified: boolean;
}

export interface Card {
  id: string;
  customer_id: string;
  card_number_masked: string;
  card_type: 'CREDIT' | 'DEBIT';
  status: 'ACTIVE' | 'FROZEN' | 'CANCELLED';
  issued_at: string;
  expires_at: string;
}

// Agent interaction types
export interface AgentMessage {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: string;
  metadata?: {
    transaction_id?: string;
    anomaly_id?: string;
    risk_level?: string;
    confidence_score?: number;
    tool_calls?: ToolCall[];
  };
}

export interface ToolCall {
  id: string;
  tool_name: string;
  parameters: Record<string, any>;
  result?: any;
  status: 'pending' | 'success' | 'error';
  executed_at?: string;
}

// Dashboard state types
export interface DashboardState {
  transactions: Transaction[];
  anomalies: AnomalyResult[];
  active_alerts: Alert[];
  agent_conversation: AgentMessage[];
  system_status: {
    cedar_stream_connected: boolean;
    agent_online: boolean;
    last_update: string;
    stream_metrics?: {
      messages_received: number;
      connection_uptime: number;
      average_latency: number;
    };
  };
}

export interface Alert {
  id: string;
  type: 'ANOMALY' | 'SYSTEM' | 'CUSTOMER';
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  title: string;
  message: string;
  transaction_id?: string;
  customer_id?: string;
  created_at: string;
  acknowledged: boolean;
  actions?: AlertAction[];
}

export interface AlertAction {
  id: string;
  label: string;
  action: 'FREEZE_CARD' | 'CALL_CUSTOMER' | 'FLAG_TRANSACTION' | 'DISMISS' | 'ESCALATE';
  parameters?: Record<string, any>;
  dangerous?: boolean;
}

// API response types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PhoneCallResult {
  success: boolean;
  call_id?: string;
  status: 'initiated' | 'in_progress' | 'completed' | 'failed';
  duration?: number;
  message: string;
}

export interface CardFreezeResult {
  success: boolean;
  card_id: string;
  customer_id: string;
  frozen_at: string;
  reason: string;
  card_status: 'FROZEN' | 'ERROR';
}

// Real-time event types
export interface RealtimeEvent {
  type: 'transaction' | 'anomaly' | 'alert' | 'agent_response' | 'system_status';
  data: any;
  timestamp: string;
}

export interface TransactionEvent extends RealtimeEvent {
  type: 'transaction';
  data: {
    transaction: Transaction;
    anomaly?: AnomalyResult;
  };
}

export interface AnomalyEvent extends RealtimeEvent {
  type: 'anomaly';
  data: {
    transaction: Transaction;
    anomaly: AnomalyResult;
    agent_triggered: boolean;
  };
}

// Cedar-OS specific types
export interface CedarState {
  // Global application state that Cedar-OS can access
  current_user: {
    id: string;
    role: 'ANALYST' | 'MANAGER' | 'ADMIN';
    permissions: string[];
  };
  active_session: {
    session_id: string;
    started_at: string;
    transactions_monitored: number;
    anomalies_detected: number;
  };
  preferences: {
    auto_freeze_critical: boolean;
    auto_call_high_risk: boolean;
    notification_channels: ('email' | 'sms' | 'push')[];
    risk_threshold: number;
  };
}

export interface CedarSpell {
  id: string;
  name: string;
  description: string;
  category: 'ANALYSIS' | 'PROTECTION' | 'COMMUNICATION' | 'INVESTIGATION';
  parameters: Record<string, any>;
  executable: boolean;
}

// Utility types
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type TransactionType = 'PURCHASE' | 'WITHDRAWAL' | 'TRANSFER' | 'REFUND';
export type NotificationChannel = 'email' | 'sms' | 'push' | 'phone' | 'cedar_stream';
