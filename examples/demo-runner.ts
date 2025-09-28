/**
 * 🎬 DEMO RUNNER - Showcase Ultimate Mastra System
 * 
 * This demo runner can work with or without API keys,
 * using mock data to demonstrate all capabilities.
 */

import { runUltimateDemo } from './ultimate-mastra-demo';
import { demonstrateProductivityAgentCapabilities } from './productivity-agent-demo';

// Mock environment for demo purposes
if (!process.env.GEMINI_API_KEY) {
  console.log('🔧 Running in DEMO MODE with mock responses');
  console.log('   (Set GEMINI_API_KEY in .env.local for live AI responses)\n');
  
  // Set demo mode
  process.env.DEMO_MODE = 'true';
  process.env.MOCK_RESPONSES = 'true';
}

async function runFullDemo() {
  console.log('🏆 ULTIMATE MASTRA MULTI-AGENT SYSTEM DEMO');
  console.log('==========================================\n');

  try {
    // Show system capabilities overview
    showSystemCapabilities();
    
    // Wait for user to continue
    console.log('\n⏱️  Starting demo in 3 seconds...');
    await sleep(3000);

    if (process.env.DEMO_MODE === 'true') {
      // Run mock demo
      await runMockDemo();
    } else {
      // Run live demo with actual AI
      await runUltimateDemo();
    }

  } catch (error) {
    console.error('❌ Demo failed:', error);
    console.log('\n💡 Try running in demo mode by setting DEMO_MODE=true');
  }
}

function showSystemCapabilities() {
  console.log('🚀 SYSTEM CAPABILITIES OVERVIEW:');
  console.log('================================');
  console.log('');
  
  const capabilities = [
    '🤖 Multi-Agent Coordination - 4 specialized AI agents working together',
    '🧠 Advanced RAG Knowledge - Semantic document search and Q&A',
    '🔮 Persistent Learning - Remembers preferences and adapts behavior',
    '📧 Intelligent Email System - AI-generated content with SendGrid',
    '📅 Smart Calendar Management - Automated scheduling and coordination',
    '📊 Business Intelligence - Advanced analytics and insights',
    '🔄 Workflow Orchestration - Complex multi-step automation',
    '🎯 Personalized Optimization - Learns and improves over time'
  ];

  capabilities.forEach(capability => {
    console.log(`  ${capability}`);
  });

  console.log('\n🏆 COMPETITIVE ADVANTAGES:');
  console.log('==========================');
  console.log('  ✅ Multiple specialized agents (not just one chatbot)');
  console.log('  ✅ Learns and remembers across sessions');
  console.log('  ✅ Processes documents with semantic understanding');
  console.log('  ✅ Coordinates complex workflows automatically');
  console.log('  ✅ Provides predictive and proactive assistance');
  console.log('  ✅ Enterprise-grade security and fraud detection');
}

async function runMockDemo() {
  console.log('\n🎭 MOCK DEMO - Simulating AI Agent Responses');
  console.log('============================================\n');

  // Mock Multi-Agent Coordination
  console.log('1. 🤖 MULTI-AGENT COORDINATION DEMO');
  console.log('Simulating coordination between specialized agents...\n');
  
  await simulateAgentResponse('Fraud Detection Agent', {
    analysis: 'CRITICAL anomaly detected in transaction TX-789123',
    risk_level: 'HIGH',
    confidence: 0.95,
    explanation: 'Transaction pattern deviates significantly from customer baseline'
  });

  await simulateAgentResponse('Customer Service Agent', {
    communication_drafted: true,
    tone: 'empathetic and reassuring',
    message_preview: 'We detected unusual activity and are taking protective measures...'
  });

  await simulateAgentResponse('Productivity Agent', {
    meeting_scheduled: true,
    participants: ['security@company.com', 'fraud@company.com'],
    time: 'Today 4:00 PM',
    calendar_invites_sent: true
  });

  await simulateAgentResponse('Analytics Agent', {
    pattern_analysis: 'Similar patterns found in 3 other cases this month',
    trend: 'Increasing sophistication in fraud attempts',
    recommendations: ['Update detection thresholds', 'Enhanced monitoring for similar patterns']
  });

  console.log('\n' + '='.repeat(60) + '\n');

  // Mock RAG Knowledge System
  console.log('2. 🧠 RAG KNOWLEDGE SYSTEM DEMO');
  console.log('Simulating intelligent document processing...\n');
  
  await simulateKnowledgeResponse({
    documents_processed: 15,
    knowledge_base_size: '2.3GB',
    query: 'transaction anomaly thresholds',
    results: [
      {
        source: 'Financial Security Policy v2.1',
        relevance: 0.94,
        answer: 'Anomaly threshold set at 3 standard deviations from user baseline'
      },
      {
        source: 'Compliance Regulations 2024',
        relevance: 0.87, 
        answer: 'Customer notification required within 24 hours for HIGH risk transactions'
      }
    ]
  });

  console.log('\n' + '='.repeat(60) + '\n');

  // Mock Learning System
  console.log('3. 🔮 ADAPTIVE LEARNING DEMO');
  console.log('Simulating preference learning and prediction...\n');
  
  await simulateLearningResponse({
    preferences_learned: [
      'Prefers detailed technical reports',
      'Wants security alerts on Friday 3 PM',
      'Likes 24-hour follow-up meetings for critical issues'
    ],
    predictions: [
      'User will request Q4 fraud analysis next week',
      'Security team meeting needed for pattern review',
      'Email template optimization based on user feedback'
    ],
    proactive_actions: [
      'Prepared draft fraud report for next Friday',
      'Blocked calendar time for security sync',
      'Generated improved email templates'
    ]
  });

  console.log('\n' + '='.repeat(60) + '\n');

  // Show final summary
  console.log('🎉 DEMO COMPLETED SUCCESSFULLY!');
  console.log('==============================');
  console.log('');
  console.log('🏆 This demonstrates a complete multi-agent intelligence system');
  console.log('   that goes far beyond basic productivity tools!');
  console.log('');
  console.log('💡 To see this with live AI responses:');
  console.log('   1. Add your API keys to .env.local');
  console.log('   2. Set DEMO_MODE=false');
  console.log('   3. Run: npm run demo:ultimate');
}

async function simulateAgentResponse(agentName: string, response: any) {
  console.log(`📡 ${agentName} Response:`);
  console.log(JSON.stringify(response, null, 2));
  console.log('');
  await sleep(1500);
}

async function simulateKnowledgeResponse(response: any) {
  console.log('🔍 Knowledge Search Results:');
  console.log(JSON.stringify(response, null, 2));
  console.log('');
  await sleep(2000);
}

async function simulateLearningResponse(response: any) {
  console.log('🤖 Learning System Analysis:');
  console.log(JSON.stringify(response, null, 2));
  console.log('');
  await sleep(2000);
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the demo
if (require.main === module) {
  runFullDemo().catch(console.error);
}

export { runFullDemo };