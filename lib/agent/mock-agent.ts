// Mock FinancePulse AI Agent for demonstration
export const financePulseAgent = {
  name: 'FinancePulse AI Agent',
  instructions: `You are FinancePulse AI, an advanced financial fraud detection and customer protection agent.`,
  
  // Mock tool execution
  async executeTools(toolCalls: any[]) {
    const results = [];
    
    for (const call of toolCalls) {
      let result;
      
      switch (call.tool_name) {
        case 'generate_anomaly_explanation':
          result = await this.generateExplanation(call.parameters);
          break;
        case 'trigger_phone_alert':
          result = await this.triggerPhoneAlert(call.parameters);
          break;
        case 'freeze_card':
          result = await this.freezeCard(call.parameters);
          break;
        case 'get_transaction_context':
          result = await this.getTransactionContext(call.parameters);
          break;
        default:
          result = { error: `Unknown tool: ${call.tool_name}` };
      }
      
      results.push({ ...call, result });
    }
    
    return results;
  },
  
  async generateExplanation(params: any) {
    // Simulate API call to backend
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/anomaly/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      if (response.ok) {
        return await response.json();
      } else {
        throw new Error('Failed to generate explanation');
      }
    } catch (error) {
      return {
        explanation: 'Transaction flagged for manual review due to unusual patterns.',
        recommended_actions: ['Review transaction manually', 'Contact customer if needed']
      };
    }
  },
  
  async triggerPhoneAlert(params: any) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/notifications/phone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      if (response.ok) {
        const result = await response.json();
        return {
          success: result.success,
          message: `Phone alert ${result.success ? 'sent successfully' : 'failed'} to ${params.customer_id}`
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Phone alert failed: ${error.message}`
      };
    }
  },
  
  async freezeCard(params: any) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/cards/freeze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      if (response.ok) {
        const result = await response.json();
        return {
          success: result.success,
          message: `Card ${params.card_id} ${result.success ? 'frozen successfully' : 'freeze failed'}`
        };
      }
    } catch (error) {
      return {
        success: false,
        message: `Card freeze failed: ${error.message}`
      };
    }
  },
  
  async getTransactionContext(params: any) {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/transactions/${params.transaction_id}/context?customer_id=${params.customer_id}`);
      
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      return {
        recent_transactions: [],
        customer_patterns: {},
        risk_factors: []
      };
    }
  }
};

export default financePulseAgent;