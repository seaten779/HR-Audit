import sgMail from '@sendgrid/mail';

// Configure SendGrid
sgMail.setApiKey(process.env.SENDGRID_API_KEY || '');

interface EmailTemplate {
  subject: string;
  htmlContent: string;
  textContent: string;
}

interface EmailAnalytics {
  sent: number;
  opened: number;
  clicked: number;
  delivered: number;
  bounced: number;
}

// Advanced Email Productivity Tools for Mastra Agent
export const emailProductivityTools = {
  send_smart_email: {
    description: 'Send intelligent, context-aware emails with AI-generated content and scheduling',
    parameters: {
      type: 'object',
      properties: {
        to: {
          type: 'array',
          items: { type: 'string' },
          description: 'Recipient email addresses'
        },
        subject_context: {
          type: 'string',
          description: 'Context or topic for AI to generate email subject'
        },
        message_context: {
          type: 'string',
          description: 'Context or key points for AI to generate email content'
        },
        tone: {
          type: 'string',
          enum: ['professional', 'casual', 'urgent', 'friendly', 'formal'],
          description: 'Tone of the email'
        },
        priority: {
          type: 'string',
          enum: ['low', 'normal', 'high', 'urgent'],
          default: 'normal',
          description: 'Email priority level'
        },
        schedule_send: {
          type: 'string',
          description: 'ISO timestamp to schedule email sending (optional)'
        },
        follow_up_days: {
          type: 'number',
          description: 'Days after which to schedule a follow-up (optional)'
        }
      },
      required: ['to', 'subject_context', 'message_context']
    },
    execute: async ({ 
      to, 
      subject_context, 
      message_context, 
      tone = 'professional',
      priority = 'normal',
      schedule_send,
      follow_up_days
    }: {
      to: string[];
      subject_context: string;
      message_context: string;
      tone: string;
      priority: string;
      schedule_send?: string;
      follow_up_days?: number;
    }) => {
      try {
        // AI-generated email content (you would integrate with your LLM here)
        const aiGeneratedContent = await generateEmailContent(message_context, tone);
        const aiGeneratedSubject = await generateEmailSubject(subject_context, tone);

        const msg = {
          to: to,
          from: process.env.SENDGRID_FROM_EMAIL || 'noreply@financepulse.com',
          subject: aiGeneratedSubject,
          text: aiGeneratedContent.text,
          html: aiGeneratedContent.html,
          priority: priority,
          headers: {
            'X-Priority': priority === 'urgent' ? '1' : priority === 'high' ? '2' : '3'
          },
          sendAt: schedule_send ? Math.floor(new Date(schedule_send).getTime() / 1000) : undefined,
          trackingSettings: {
            clickTracking: { enable: true },
            openTracking: { enable: true },
            subscriptionTracking: { enable: false }
          }
        };

        const result = await sgMail.sendMultiple(msg);
        
        // Schedule follow-up if requested
        if (follow_up_days) {
          await scheduleFollowUp(to, aiGeneratedSubject, follow_up_days);
        }

        return {
          success: true,
          message_id: result[0]?.headers?.['x-message-id'],
          sent_to: to,
          scheduled: !!schedule_send,
          follow_up_scheduled: !!follow_up_days,
          content_preview: aiGeneratedContent.text.substring(0, 100) + '...'
        };

      } catch (error) {
        console.error('Error sending smart email:', error);
        return {
          success: false,
          error: `Failed to send email: ${error.message}`
        };
      }
    }
  },

  analyze_email_performance: {
    description: 'Analyze email campaign performance and suggest improvements',
    parameters: {
      type: 'object',
      properties: {
        days_back: {
          type: 'number',
          default: 30,
          description: 'Number of days back to analyze'
        },
        campaign_type: {
          type: 'string',
          description: 'Type of campaign to analyze (optional filter)'
        }
      }
    },
    execute: async ({ days_back = 30, campaign_type }: {
      days_back: number;
      campaign_type?: string;
    }) => {
      try {
        // Get email statistics from SendGrid
        const stats = await getEmailAnalytics(days_back);
        const insights = analyzeEmailPerformance(stats);

        return {
          success: true,
          period: `${days_back} days`,
          analytics: stats,
          insights: insights,
          recommendations: generateEmailRecommendations(stats)
        };

      } catch (error) {
        console.error('Error analyzing email performance:', error);
        return {
          success: false,
          error: `Failed to analyze performance: ${error.message}`
        };
      }
    }
  },

  create_email_sequence: {
    description: 'Create an automated email sequence for nurturing or onboarding',
    parameters: {
      type: 'object',
      properties: {
        sequence_name: {
          type: 'string',
          description: 'Name for the email sequence'
        },
        target_audience: {
          type: 'string',
          description: 'Description of target audience'
        },
        sequence_goal: {
          type: 'string',
          description: 'Goal of the sequence (onboarding, nurturing, etc.)'
        },
        number_of_emails: {
          type: 'number',
          default: 5,
          description: 'Number of emails in sequence'
        },
        interval_days: {
          type: 'array',
          items: { type: 'number' },
          description: 'Days between each email (e.g., [1, 3, 7, 14])'
        }
      },
      required: ['sequence_name', 'target_audience', 'sequence_goal']
    },
    execute: async ({ 
      sequence_name, 
      target_audience, 
      sequence_goal, 
      number_of_emails = 5,
      interval_days = [1, 3, 7, 14, 30]
    }: {
      sequence_name: string;
      target_audience: string;
      sequence_goal: string;
      number_of_emails: number;
      interval_days: number[];
    }) => {
      try {
        // Generate AI-powered email sequence
        const emailSequence = await generateEmailSequence({
          name: sequence_name,
          audience: target_audience,
          goal: sequence_goal,
          count: number_of_emails,
          intervals: interval_days
        });

        return {
          success: true,
          sequence_name,
          emails: emailSequence,
          total_duration: Math.max(...interval_days) + ' days',
          automation_ready: true
        };

      } catch (error) {
        console.error('Error creating email sequence:', error);
        return {
          success: false,
          error: `Failed to create sequence: ${error.message}`
        };
      }
    }
  },

  smart_email_reply: {
    description: 'Generate intelligent email replies based on context and intent',
    parameters: {
      type: 'object',
      properties: {
        original_email: {
          type: 'string',
          description: 'The original email content to reply to'
        },
        reply_intent: {
          type: 'string',
          enum: ['accept', 'decline', 'request_info', 'schedule_meeting', 'follow_up', 'custom'],
          description: 'Intent of the reply'
        },
        custom_context: {
          type: 'string',
          description: 'Additional context for custom replies'
        },
        tone: {
          type: 'string',
          enum: ['professional', 'casual', 'apologetic', 'enthusiastic'],
          default: 'professional'
        }
      },
      required: ['original_email', 'reply_intent']
    },
    execute: async ({ 
      original_email, 
      reply_intent, 
      custom_context,
      tone = 'professional'
    }: {
      original_email: string;
      reply_intent: string;
      custom_context?: string;
      tone: string;
    }) => {
      try {
        const replyContent = await generateSmartReply({
          originalEmail: original_email,
          intent: reply_intent,
          context: custom_context,
          tone: tone
        });

        return {
          success: true,
          generated_reply: replyContent,
          intent: reply_intent,
          tone: tone,
          ready_to_send: true
        };

      } catch (error) {
        console.error('Error generating smart reply:', error);
        return {
          success: false,
          error: `Failed to generate reply: ${error.message}`
        };
      }
    }
  },

  schedule_smart_follow_ups: {
    description: 'Automatically schedule intelligent follow-up emails based on recipient behavior',
    parameters: {
      type: 'object',
      properties: {
        original_email_id: {
          type: 'string',
          description: 'ID of the original email to follow up on'
        },
        follow_up_strategy: {
          type: 'string',
          enum: ['gentle_reminder', 'value_add', 'urgent', 'final_attempt'],
          description: 'Type of follow-up strategy'
        },
        wait_for_response_days: {
          type: 'number',
          default: 3,
          description: 'Days to wait for response before follow-up'
        },
        max_follow_ups: {
          type: 'number',
          default: 3,
          description: 'Maximum number of follow-ups'
        }
      },
      required: ['original_email_id', 'follow_up_strategy']
    },
    execute: async ({ 
      original_email_id, 
      follow_up_strategy, 
      wait_for_response_days = 3,
      max_follow_ups = 3
    }: {
      original_email_id: string;
      follow_up_strategy: string;
      wait_for_response_days: number;
      max_follow_ups: number;
    }) => {
      try {
        const followUpSchedule = await createFollowUpSchedule({
          emailId: original_email_id,
          strategy: follow_up_strategy,
          waitDays: wait_for_response_days,
          maxFollowUps: max_follow_ups
        });

        return {
          success: true,
          original_email_id,
          follow_up_count: followUpSchedule.length,
          schedule: followUpSchedule,
          strategy: follow_up_strategy
        };

      } catch (error) {
        console.error('Error scheduling follow-ups:', error);
        return {
          success: false,
          error: `Failed to schedule follow-ups: ${error.message}`
        };
      }
    }
  }
};

// Helper functions (you would implement these with your AI model)
async function generateEmailContent(context: string, tone: string): Promise<{ text: string; html: string }> {
  // Integrate with your AI model (Gemini in your case) to generate email content
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/generate-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ context, tone, type: 'content' })
  });
  
  const data = await response.json();
  return {
    text: data.text_content,
    html: data.html_content
  };
}

async function generateEmailSubject(context: string, tone: string): Promise<string> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai/generate-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ context, tone, type: 'subject' })
  });
  
  const data = await response.json();
  return data.subject;
}

async function getEmailAnalytics(daysBack: number): Promise<EmailAnalytics> {
  // Mock implementation - replace with actual SendGrid stats API call
  return {
    sent: 150,
    opened: 120,
    clicked: 45,
    delivered: 148,
    bounced: 2
  };
}

function analyzeEmailPerformance(stats: EmailAnalytics) {
  const openRate = (stats.opened / stats.sent) * 100;
  const clickRate = (stats.clicked / stats.opened) * 100;
  const deliveryRate = (stats.delivered / stats.sent) * 100;
  
  return {
    open_rate: `${openRate.toFixed(2)}%`,
    click_rate: `${clickRate.toFixed(2)}%`,
    delivery_rate: `${deliveryRate.toFixed(2)}%`,
    engagement_score: calculateEngagementScore(openRate, clickRate)
  };
}

function calculateEngagementScore(openRate: number, clickRate: number): string {
  const score = (openRate * 0.6) + (clickRate * 0.4);
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Average';
  return 'Needs Improvement';
}

function generateEmailRecommendations(stats: EmailAnalytics): string[] {
  const recommendations = [];
  const openRate = (stats.opened / stats.sent) * 100;
  const clickRate = (stats.clicked / stats.opened) * 100;
  
  if (openRate < 20) {
    recommendations.push('Improve subject lines to increase open rates');
    recommendations.push('Send emails at optimal times for your audience');
  }
  
  if (clickRate < 3) {
    recommendations.push('Add clear call-to-action buttons');
    recommendations.push('Personalize content based on recipient interests');
  }
  
  if (stats.bounced / stats.sent > 0.02) {
    recommendations.push('Clean up your email list to reduce bounce rates');
  }
  
  return recommendations;
}

// Additional helper functions would be implemented here...
async function generateEmailSequence(params: any): Promise<any[]> {
  // Implementation for generating AI-powered email sequences
  return [];
}

async function generateSmartReply(params: any): Promise<string> {
  // Implementation for generating smart email replies
  return "Generated smart reply content";
}

async function createFollowUpSchedule(params: any): Promise<any[]> {
  // Implementation for creating follow-up schedules
  return [];
}

async function scheduleFollowUp(recipients: string[], subject: string, days: number): Promise<void> {
  // Implementation for scheduling follow-ups
}