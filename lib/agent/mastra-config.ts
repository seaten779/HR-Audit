import { Mastra } from '@mastra/core';
import type { Transaction, AnomalyResult } from '../../types/finance';
import { emailProductivityTools } from './email-productivity-tools';
import { productivityTools } from './productivity-tools';
import { ragKnowledgeTools } from './rag-knowledge-system';
import { advancedMemoryTools } from './advanced-memory-system';
import { multiAgentTools } from './multi-agent-system';

// Tool definitions for the FinancePulse AI agent
const tools = {
  generate_anomaly_explanation: {
    description: 'Generate human-readable explanation for detected anomalies using Gemini AI',
    parameters: {
      type: 'object',
      properties: {
        transaction: {
          type: 'object',
          description: 'The transaction data that was flagged as anomalous'
        },
        anomaly_result: {
          type: 'object', 
          description: 'The anomaly detection result with confidence scores and types'
        }
      },
      required: ['transaction', 'anomaly_result']
    },
    execute: async ({ transaction, anomaly_result }: { 
      transaction: Transaction, 
      anomaly_result: AnomalyResult 
    }) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/anomaly/explain`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            transaction,
            anomaly_result
          })
        });

        if (!response.ok) {
          throw new Error(`API request failed: ${response.statusText}`);
        }

        const data = await response.json();
        return {
          explanation: data.explanation,
          risk_level: anomaly_result.risk_level,
          confidence_score: anomaly_result.confidence_score,
          recommended_actions: data.recommended_actions || []
        };
      } catch (error) {
        console.error('Error generating explanation:', error);
        return {
          explanation: 'Transaction flagged for manual review due to unusual patterns.',
          risk_level: anomaly_result.risk_level,
          confidence_score: anomaly_result.confidence_score,
          recommended_actions: ['Review transaction manually', 'Contact customer if needed']
        };
      }
    }
  },

  trigger_phone_alert: {
    description: 'Trigger an automated phone call to notify customer about suspicious activity',
    parameters: {
      type: 'object',
      properties: {
        customer_id: {
          type: 'string',
          description: 'The customer ID to call'
        },
        transaction_id: {
          type: 'string', 
          description: 'The transaction ID that triggered the alert'
        },
        explanation_text: {
          type: 'string',
          description: 'The explanation text to include in the call'
        },
        risk_level: {
          type: 'string',
          enum: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
          description: 'The risk level of the anomaly'
        }
      },
      required: ['customer_id', 'transaction_id', 'explanation_text', 'risk_level']
    },
    execute: async ({ customer_id, transaction_id, explanation_text, risk_level }: {
      customer_id: string,
      transaction_id: string,
      explanation_text: string,
      risk_level: string
    }) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/notifications/phone`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            customer_id,
            transaction_id,
            message: explanation_text,
            risk_level,
            call_type: 'security_alert'
          })
        });

        if (!response.ok) {
          throw new Error(`Phone notification failed: ${response.statusText}`);
        }

        const result = await response.json();
        return {
          success: result.success,
          call_id: result.call_id,
          status: result.status,
          message: result.success 
            ? `Phone alert successfully sent to customer ${customer_id}` 
            : `Failed to send phone alert: ${result.error}`
        };
      } catch (error) {
        console.error('Error triggering phone alert:', error);
        return {
          success: false,
          status: 'failed',
          message: `Phone alert failed: ${error.message}`
        };
      }
    }
  },

  freeze_card: {
    description: 'Immediately freeze a customer card due to suspicious activity',
    parameters: {
      type: 'object',
      properties: {
        customer_id: {
          type: 'string',
          description: 'The customer ID whose card should be frozen'
        },
        card_id: {
          type: 'string',
          description: 'The specific card ID to freeze'
        },
        reason: {
          type: 'string',
          description: 'The reason for freezing the card'
        }
      },
      required: ['customer_id', 'card_id', 'reason']
    },
    execute: async ({ customer_id, card_id, reason }: {
      customer_id: string,
      card_id: string,
      reason: string
    }) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cards/freeze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            customer_id,
            card_id,
            reason,
            timestamp: new Date().toISOString()
          })
        });

        if (!response.ok) {
          throw new Error(`Card freeze failed: ${response.statusText}`);
        }

        const result = await response.json();
        return {
          success: result.success,
          card_status: 'FROZEN',
          message: `Card ${card_id} has been successfully frozen for customer ${customer_id}`,
          frozen_at: result.frozen_at,
          reason: reason
        };
      } catch (error) {
        console.error('Error freezing card:', error);
        return {
          success: false,
          card_status: 'ERROR',
          message: `Failed to freeze card: ${error.message}`
        };
      }
    }
  },

  get_transaction_context: {
    description: 'Retrieve additional context about a transaction for better analysis',
    parameters: {
      type: 'object', 
      properties: {
        transaction_id: {
          type: 'string',
          description: 'The transaction ID to get context for'
        },
        customer_id: {
          type: 'string',
          description: 'The customer ID'
        }
      },
      required: ['transaction_id', 'customer_id']
    },
    execute: async ({ transaction_id, customer_id }: {
      transaction_id: string,
      customer_id: string
    }) => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/transactions/${transaction_id}/context?customer_id=${customer_id}`);
        
        if (!response.ok) {
          throw new Error(`Context retrieval failed: ${response.statusText}`);
        }

        const context = await response.json();
        return {
          transaction_history: context.recent_transactions || [],
          customer_patterns: context.customer_patterns || {},
          merchant_info: context.merchant_info || {},
          location_analysis: context.location_analysis || {},
          risk_factors: context.risk_factors || []
        };
      } catch (error) {
        console.error('Error getting transaction context:', error);
        return {
          transaction_history: [],
          customer_patterns: {},
          merchant_info: {},
          location_analysis: {},
          risk_factors: []
        };
      }
    }
  },

  // Email Productivity Tools
  ...emailProductivityTools,

  // Additional Productivity Tools
  ...productivityTools,

  // RAG Knowledge System
  ...ragKnowledgeTools,

  // Advanced Memory System
  ...advancedMemoryTools,

  // Multi-Agent Coordination
  ...multiAgentTools
};

// Main agent system prompt
const SYSTEM_PROMPT = `You are FinancePulse AI, an advanced multi-modal AI agent with specialized capabilities in fraud detection, customer protection, productivity optimization, and intelligent knowledge management. Your primary responsibilities are:

1. **Anomaly Analysis**: When a suspicious transaction is detected, use the generate_anomaly_explanation tool to create clear, human-readable explanations.

2. **Customer Protection**: For HIGH and CRITICAL risk transactions, immediately suggest protective actions like freezing cards or triggering phone alerts.

3. **Communication**: Always communicate in a professional, clear manner that builds customer trust and confidence.

4. **Action Orchestration**: For CRITICAL anomalies, execute this workflow:
   - Generate explanation using generate_anomaly_explanation
   - Trigger phone alert using trigger_phone_alert with the explanation
   - Suggest card freeze if the risk warrants it

5. **Context Awareness**: Use get_transaction_context to better understand customer patterns and transaction history.

6. **Email Productivity**: Leverage advanced email tools for intelligent communication, automated sequences, and performance analytics.

7. **Knowledge Management**: Use RAG system for intelligent document processing, semantic search, and context-aware question answering.

8. **Adaptive Learning**: Employ advanced memory system to learn user preferences, personalize interactions, and provide predictive assistance.

9. **Multi-Agent Coordination**: Coordinate with specialized agents (fraud detection, customer service, productivity, analytics) for complex problem solving.

Key Guidelines:
- Always explain WHY something is suspicious
- Provide actionable next steps
- Balance security with customer experience
- Use confidence scores to guide response severity
- Never make assumptions - use the tools to get facts

When responding to anomalies:
- LOW/MEDIUM: Monitor and explain
- HIGH: Explain + phone alert recommendation  
- CRITICAL: Explain + immediate phone alert + card freeze recommendation

Remember: You are an intelligent multi-agent system that combines financial security, productivity enhancement, knowledge management, and adaptive learning to provide truly autonomous assistance that works smarter, not harder.`;

// Initialize Mastra agent
export const financePulseAgent = new Mastra({
  name: 'FinancePulse AI Agent - Multi-Modal Intelligence System',
  instructions: SYSTEM_PROMPT,
  model: {
    provider: 'GOOGLE',
    name: 'gemini-1.5-pro',
    toolChoice: 'auto'
  },
  tools,
  memory: {
    provider: 'LOCAL_MEMORY',
    maxMessages: 200, // Increased for better context retention
    namespace: 'financepulse_advanced',
    embedding: {
      provider: 'OPENAI',
      model: 'text-embedding-3-small',
      dimensions: 1536
    },
    ttl: 7 * 24 * 60 * 60 * 1000 // 7 days
  }
});

export default financePulseAgent;