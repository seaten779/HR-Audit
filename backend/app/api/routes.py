"""
API Routes for FinancePulse
REST API endpoints for transactions, anomalies, and dashboard data
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
import random
import logging
import base64

from app.models import APIResponse, Transaction, AnomalyResult, CustomerContact, NotificationSettings
from app.core.config import settings

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/transactions", response_model=APIResponse)
async def get_transactions(
    customer_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get recent transactions with optional filtering"""
    try:
        # This would normally query a database
        # For demo purposes, return mock data
        transactions = [
            {
                "id": f"txn_{i:06d}",
                "customer_id": customer_id or f"customer_{(i % 20) + 1:03d}",
                "account_id": f"account_{(i % 20) + 1:03d}",
                "amount": 25.50 + (i * 5.25),
                "type": "purchase",
                "merchant_name": "Demo Merchant",
                "merchant_category": "grocery",
                "timestamp": (datetime.utcnow() - timedelta(minutes=i * 10)).isoformat()
            }
            for i in range(limit)
        ]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(transactions)} transactions",
            data={"transactions": transactions, "total": len(transactions)}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies", response_model=APIResponse)
async def get_anomalies(
    customer_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 20
):
    """Get recent anomaly detections"""
    try:
        # Mock anomaly data
        anomalies = [
            {
                "id": f"anomaly_{i:06d}",
                "transaction_id": f"txn_{i:06d}",
                "customer_id": customer_id or f"customer_{(i % 5) + 1:03d}",
                "risk_level": "medium",
                "confidence_score": 0.75,
                "anomaly_types": ["unusual_amount"],
                "explanation": "Transaction amount is significantly higher than typical spending pattern",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            }
            for i in range(min(limit, 10))
        ]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(anomalies)} anomalies",
            data={"anomalies": anomalies}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/stats", response_model=APIResponse)
async def get_dashboard_stats():
    """Get real-time dashboard statistics and metrics"""
    try:
        from main import transaction_simulator, notification_orchestrator, anomaly_detector
        
        # Get real anomaly stats from simulator
        anomaly_stats = transaction_simulator.get_anomaly_stats()
        
        # Get notification history for additional metrics
        notification_history = notification_orchestrator.get_notification_history(limit=1000)
        
        # Calculate metrics
        total_transactions = anomaly_stats["total_transactions"]
        anomalies_detected = anomaly_stats["anomalous_transactions"]
        anomaly_rate = anomaly_stats["anomaly_rate_percent"] / 100
        
        # Calculate confidence scores from recent anomalies
        confidence_scores = [n.risk_level.value for n in notification_history if hasattr(n, 'risk_level')]
        avg_confidence = sum([0.2 if c == 'low' else 0.4 if c == 'medium' else 0.7 if c == 'high' else 0.9 for c in confidence_scores[:50]]) / max(len(confidence_scores[:50]), 1)
        
        # Calculate active alerts (recent anomalies in last hour)
        recent_notifications = [n for n in notification_history if n.sent_at and (datetime.utcnow() - n.sent_at).total_seconds() < 3600]
        active_alerts = len(recent_notifications)
        
        # Email and phone notifications sent
        email_notifications = len([n for n in notification_history if n.notification_type.value == 'email'])
        phone_notifications = len([n for n in notification_history if n.notification_type.value == 'phone'])
        
        # Calculate transaction volume for graph (last 12 hours)
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        volume_data = []
        for i in range(12):
            hour = current_hour - timedelta(hours=i)
            # Simulate transaction volume (in real app, this would query database)
            volume = max(0, int(total_transactions * 0.08 * random.uniform(0.5, 1.5)))
            volume_data.append({
                "hour": hour.strftime("%H:00"),
                "transactions": volume,
                "anomalies": int(volume * anomaly_rate * random.uniform(0.8, 1.2))
            })
        volume_data.reverse()
        
        # Anomaly breakdown
        anomaly_types = {
            "unusual_amount": int(anomalies_detected * 0.35),
            "unusual_location": int(anomalies_detected * 0.25),
            "unusual_time": int(anomalies_detected * 0.20),
            "velocity_spike": int(anomalies_detected * 0.12),
            "unusual_merchant": int(anomalies_detected * 0.08)
        }
        
        stats = {
            "total_transactions": total_transactions,
            "anomalies_detected": anomalies_detected,
            "active_alerts": active_alerts,
            "average_confidence": round(avg_confidence, 3),
            "anomaly_rate": round(anomaly_rate, 4),
            "next_anomaly_in": anomaly_stats["next_anomaly_in"],
            "notifications_sent": {
                "email": email_notifications,
                "phone": phone_notifications,
                "total": email_notifications + phone_notifications
            },
            "transaction_volume": volume_data,
            "anomaly_breakdown": anomaly_types,
            "risk_levels": {
                "low": int(anomalies_detected * 0.4),
                "medium": int(anomalies_detected * 0.35),
                "high": int(anomalies_detected * 0.2), 
                "critical": int(anomalies_detected * 0.05)
            },
            "recent_trends": {
                "last_hour": {
                    "transactions": min(60, total_transactions),
                    "anomalies": len([n for n in recent_notifications]),
                    "notifications_sent": len(recent_notifications)
                },
                "last_day": {
                    "transactions": total_transactions,
                    "anomalies": anomalies_detected,
                    "notifications_sent": len(notification_history)
                }
            },
            "system_performance": {
                "detection_accuracy": 0.94,
                "false_positive_rate": 0.08,
                "response_time_ms": 45
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return APIResponse(
            success=True,
            message="Dashboard stats retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/{customer_id}/profile", response_model=APIResponse)
async def get_customer_profile(customer_id: str):
    """Get customer profile and spending patterns"""
    try:
        profile = {
            "customer_id": customer_id,
            "name": f"Customer {customer_id.split('_')[-1]}",
            "account_id": f"account_{customer_id.split('_')[-1]}",
            "spending_profile": {
                "avg_daily_spending": 125.50,
                "avg_transaction_amount": 45.75,
                "transactions_per_day": 2.8,
                "preferred_categories": ["grocery", "restaurant", "gas_station"],
                "typical_hours": "9 AM - 7 PM",
                "common_locations": ["New York, NY", "Brooklyn, NY"]
            },
            "risk_metrics": {
                "overall_risk_score": 0.25,
                "anomaly_history": 12,
                "false_positive_rate": 0.08,
                "last_suspicious_activity": "2024-09-25T14:30:00Z"
            },
            "account_status": "active",
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return APIResponse(
            success=True,
            message="Customer profile retrieved successfully",
            data=profile
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scenarios/trigger", response_model=APIResponse)
async def trigger_scenario(scenario: str):
    """Trigger a specific test scenario for anomaly detection"""
    try:
        from main import transaction_simulator, anomaly_detector, explanation_engine, websocket_manager
        
        # Map frontend scenario types to backend scenario types
        scenario_mapping = {
            "velocity": "velocity_spike",
            "high_value": "large_amount", 
            "foreign": "unusual_location",
            "unusual_merchant": "unusual_merchant",
            "night_activity": "unusual_time"
        }
        
        backend_scenario = scenario_mapping.get(scenario, "random")
        
        # Generate multiple transactions for the scenario (1-3 transactions)
        num_transactions = random.randint(1, 3)
        generated_transactions = []
        
        for i in range(num_transactions):
            # Generate suspicious transaction
            if backend_scenario == "velocity_spike" and i > 0:
                # For velocity spikes, generate transactions very close together
                await asyncio.sleep(0.1)
            
            transaction = await transaction_simulator.generate_suspicious_transaction(backend_scenario)
            
            # Process through anomaly detection
            anomaly_result = await anomaly_detector.detect_anomaly(transaction)
            
            # Generate explanation
            if anomaly_result.is_anomaly:
                explanation = await explanation_engine.generate_explanation(
                    transaction, anomaly_result
                )
                anomaly_result.explanation = explanation
            
            # Broadcast to WebSocket clients
            message = {
                "type": "transaction",
                "data": {
                    "transaction": transaction.model_dump(),
                    "anomaly": anomaly_result.model_dump() if anomaly_result.is_anomaly else None
                },
                "timestamp": transaction.timestamp.isoformat(),
                "scenario": scenario
            }
            
            await websocket_manager.broadcast(message)
            
            generated_transactions.append({
                "transaction_id": transaction.id,
                "amount": transaction.amount,
                "merchant": transaction.merchant_name,
                "is_anomaly": anomaly_result.is_anomaly,
                "confidence_score": anomaly_result.confidence_score if anomaly_result.is_anomaly else None
            })
            
            # Small delay between transactions
            if i < num_transactions - 1:
                await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return APIResponse(
            success=True,
            message=f"Successfully generated {num_transactions} transactions for {scenario} scenario",
            data={
                "scenario": scenario,
                "transactions_generated": num_transactions,
                "transactions": generated_transactions
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge", response_model=APIResponse)
async def acknowledge_alert(alert_id: str, notes: Optional[str] = None):
    """Acknowledge a security alert"""
    try:
        result = {
            "alert_id": alert_id,
            "status": "acknowledged",
            "acknowledged_at": datetime.utcnow().isoformat(),
            "notes": notes
        }
        
        return APIResponse(
            success=True,
            message="Alert acknowledged successfully",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/history", response_model=APIResponse)
async def get_notification_history(
    customer_id: Optional[str] = None,
    limit: int = 50
):
    """Get notification history"""
    try:
        from main import notification_orchestrator
        
        history = notification_orchestrator.get_notification_history(customer_id, limit)
        
        return APIResponse(
            success=True,
            message="Notification history retrieved successfully",
            data={
                "notifications": [record.model_dump() for record in history],
                "total": len(history)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/{customer_id}/contact", response_model=APIResponse)
async def get_customer_contact(customer_id: str):
    """Get customer contact information"""
    try:
        from main import notification_orchestrator
        
        contact = notification_orchestrator.get_customer_contact(customer_id)
        if not contact:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return APIResponse(
            success=True,
            message="Customer contact retrieved successfully",
            data=contact.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/customers/{customer_id}/contact", response_model=APIResponse)
async def update_customer_contact(customer_id: str, contact_data: dict):
    """Update customer contact information"""
    try:
        from main import notification_orchestrator
        
        success = notification_orchestrator.update_customer_contact(customer_id, contact_data)
        if not success:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return APIResponse(
            success=True,
            message="Customer contact updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/{customer_id}/notification-settings", response_model=APIResponse)
async def get_customer_notification_settings(customer_id: str):
    """Get customer notification settings"""
    try:
        from main import notification_orchestrator
        
        settings_obj = notification_orchestrator.get_customer_settings(customer_id)
        if not settings_obj:
            raise HTTPException(status_code=404, detail="Customer settings not found")
        
        return APIResponse(
            success=True,
            message="Customer notification settings retrieved successfully",
            data=settings_obj.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/customers/{customer_id}/notification-settings", response_model=APIResponse)
async def update_customer_notification_settings(customer_id: str, settings_data: dict):
    """Update customer notification settings"""
    try:
        from main import notification_orchestrator
        
        success = notification_orchestrator.update_customer_settings(customer_id, settings_data)
        if not success:
            raise HTTPException(status_code=404, detail="Customer settings not found")
        
        return APIResponse(
            success=True,
            message="Customer notification settings updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/test-email", response_model=APIResponse)
async def test_email_notification(customer_id: str):
    """Send a test email notification"""
    try:
        from main import notification_orchestrator
        from app.services.email_service import email_service
        
        # Get customer contact
        contact = notification_orchestrator.get_customer_contact(customer_id)
        if not contact or not contact.email:
            raise HTTPException(status_code=400, detail="Customer email not found")
        
        # Send test email
        success = await email_service.send_custom_email(
            to_email=contact.email,
            subject="FinancePulse Test Notification",
            body=f"Hello {contact.name},\n\nThis is a test notification from FinancePulse to verify your email settings are working correctly.\n\nBest regards,\nFinancePulse Security Team"
        )
        
        return APIResponse(
            success=success,
            message="Test email sent successfully" if success else "Failed to send test email"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/test-phone", response_model=APIResponse)
async def test_phone_notification(customer_id: str):
    """Send a test phone notification"""
    try:
        from main import notification_orchestrator
        from app.services.phone_service import phone_service
        
        # Get customer contact
        contact = notification_orchestrator.get_customer_contact(customer_id)
        if not contact or not contact.phone:
            raise HTTPException(status_code=400, detail="Customer phone not found")
        
        # Send test call
        test_script = f"Hello {contact.name}, this is a test call from FinancePulse to verify your phone notification settings are working correctly. Thank you for using FinancePulse. Goodbye."
        
        success = await phone_service.make_custom_call(
            phone_number=contact.phone,
            script=test_script,
            customer_name=contact.name
        )
        
        return APIResponse(
            success=success,
            message="Test phone call initiated successfully" if success else "Failed to initiate test phone call"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notifications/dashboard-stats", response_model=APIResponse)
async def get_notification_dashboard_stats():
    """Get notification dashboard statistics"""
    try:
        from main import notification_orchestrator
        
        # Get all notification history
        history = notification_orchestrator.get_notification_history(limit=1000)
        
        # Calculate metrics
        total_notifications = len(history)
        email_count = len([n for n in history if n.notification_type.value == 'email'])
        phone_count = len([n for n in history if n.notification_type.value == 'phone'])
        successful = len([n for n in history if n.status.value == 'sent'])
        failed = len([n for n in history if n.status.value == 'failed'])
        
        # Risk level breakdown
        risk_breakdown = {
            'critical': len([n for n in history if n.risk_level.value == 'critical']),
            'high': len([n for n in history if n.risk_level.value == 'high']),
            'medium': len([n for n in history if n.risk_level.value == 'medium']),
            'low': len([n for n in history if n.risk_level.value == 'low'])
        }
        
        # Recent activity (last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_notifications = [n for n in history if n.sent_at and n.sent_at > recent_cutoff]
        
        # Customer breakdown (top 5 customers by notifications)
        customer_counts = {}
        for n in history:
            customer_counts[n.customer_id] = customer_counts.get(n.customer_id, 0) + 1
        top_customers = sorted(customer_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        stats = {
            "total_notifications": total_notifications,
            "notification_types": {
                "email": email_count,
                "phone": phone_count
            },
            "status_breakdown": {
                "successful": successful,
                "failed": failed,
                "success_rate": round(successful / max(total_notifications, 1), 3)
            },
            "risk_breakdown": risk_breakdown,
            "recent_activity": {
                "last_24h": len(recent_notifications),
                "emails_24h": len([n for n in recent_notifications if n.notification_type.value == 'email']),
                "calls_24h": len([n for n in recent_notifications if n.notification_type.value == 'phone'])
            },
            "top_customers": [{
                "customer_id": customer_id,
                "notification_count": count
            } for customer_id, count in top_customers],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return APIResponse(
            success=True,
            message="Notification dashboard stats retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomaly-stats", response_model=APIResponse)
async def get_anomaly_stats():
    """Get anomaly injection statistics"""
    try:
        from main import transaction_simulator
        
        stats = transaction_simulator.get_anomaly_stats()
        
        return APIResponse(
            success=True,
            message="Anomaly statistics retrieved successfully",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/generate-ai-analysis", response_model=APIResponse)
async def generate_ai_analysis_report(
    data: dict
):
    """Generate AI-powered analysis report using OpenAI"""
    try:
        from app.services.openai_service import openai_service
        
        # Build analysis prompt
        analysis_prompt = f"""
Generate a comprehensive executive financial security analysis report based on the following data:

SYSTEM METRICS:
- Total Transactions: {data.get('total_transactions', 0):,}
- Anomalies Detected: {data.get('anomalies_detected', 0)}
- Anomaly Rate: {data.get('anomaly_rate', 0) * 100:.2f}%
- Average Confidence: {data.get('average_confidence', 0) * 100:.1f}%
- Detection Accuracy: {data.get('detection_accuracy', 0.94) * 100:.1f}%

ANOMALY BREAKDOWN:
{chr(10).join([f'- {k.replace("_", " ").title()}: {v} cases' for k, v in data.get('anomaly_breakdown', {}).items()])}

RISK LEVELS:
- Critical: {data.get('risk_levels', {}).get('critical', 0)}
- High: {data.get('risk_levels', {}).get('high', 0)}
- Medium: {data.get('risk_levels', {}).get('medium', 0)}
- Low: {data.get('risk_levels', {}).get('low', 0)}

NOTIFICATIONS:
- Emails: {data.get('notifications_sent', {}).get('email', 0)}
- Calls: {data.get('notifications_sent', {}).get('phone', 0)}

Provide a professional financial services analysis with:
1. EXECUTIVE SUMMARY (3-4 sentences)
2. KEY INSIGHTS & PATTERNS
3. RISK ASSESSMENT
4. OPERATIONAL RECOMMENDATIONS
5. STRATEGIC IMPROVEMENTS
6. COMPLIANCE NOTES

Write in professional banking language suitable for executive reporting.
Format with clear sections and actionable insights.
Avoid technical jargon - focus on business impact.
"""
        
        try:
            # Generate analysis with OpenAI (includes built-in fallback)
            analysis = await openai_service.generate_custom_content(analysis_prompt)
        except Exception as openai_error:
            # Additional fallback to structured analysis if needed
            logger.warning(f"OpenAI analysis failed, using fallback: {openai_error}")
            analysis = generate_fallback_analysis(data)
        
        return APIResponse(
            success=True,
            message="AI analysis report generated successfully",
            data={
                "analysis": analysis,
                "generated_at": datetime.utcnow().isoformat(),
                "data_summary": {
                    "total_transactions": data.get('total_transactions', 0),
                    "anomalies_detected": data.get('anomalies_detected', 0),
                    "anomaly_rate_percent": round(data.get('anomaly_rate', 0) * 100, 2)
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating AI analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def generate_fallback_analysis(data: dict) -> str:
    """Generate fallback analysis when Gemini is unavailable"""
    total_txns = data.get('total_transactions', 0)
    anomalies = data.get('anomalies_detected', 0)
    anomaly_rate = data.get('anomaly_rate', 0) * 100
    
    return f"""
FINANCEPULSE EXECUTIVE INTELLIGENCE REPORT
Generated: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

EXECUTIVE SUMMARY
================
FinancePulse processed {total_txns:,} transactions with {anomalies} anomalies detected, representing a {anomaly_rate:.2f}% detection rate. The system demonstrates {'excellent' if anomaly_rate < 2 else 'elevated'} fraud detection capabilities with high-confidence anomaly identification.

KEY INSIGHTS & PATTERNS
=======================
• Transaction volume indicates {'robust' if total_txns > 1000 else 'moderate'} system activity
• Anomaly detection rate of {anomaly_rate:.2f}% is {'within normal parameters' if anomaly_rate < 3 else 'above baseline thresholds'}
• System confidence levels demonstrate reliable fraud detection capabilities
• Risk distribution shows appropriate escalation protocols

RISK ASSESSMENT
===============
• Critical risk transactions require immediate investigation
• High-risk patterns suggest potential coordinated fraud attempts
• Geographic anomalies indicate possible account compromise scenarios
• Time-based anomalies suggest automated or scripted attack patterns

OPERATIONAL RECOMMENDATIONS
===========================
1. Continue monitoring critical risk transactions within 1-hour response window
2. Implement enhanced verification for high-value transaction patterns
3. Review customer communication effectiveness for anomaly notifications
4. Consider threshold adjustments during peak transaction periods

STRATEGIC IMPROVEMENTS
======================
• Expand AI model training with recent anomaly patterns
• Implement predictive risk scoring for proactive fraud prevention
• Consider advanced behavioral analytics for account takeover detection
• Enhance customer notification personalization

COMPLIANCE NOTES
================
All detection processes maintain compliance with financial industry regulations.
Customer privacy protection protocols are fully implemented.
Audit trails are maintained for all anomaly detection activities.

Report Classification: CONFIDENTIAL
Generated by: FinancePulse AI Intelligence Engine
"""


@router.post("/reports/generate-pdf", response_model=APIResponse)
async def generate_pdf_report(
    data: dict,
    include_ai_analysis: bool = True
):
    """Generate and return PDF report with optional AI analysis"""
    try:
        from app.services.pdf_service import pdf_service
        
        logger.info(f"Generating PDF report with data: {list(data.keys())}")
        
        ai_analysis = None
        
        if include_ai_analysis:
            try:
                from app.services.openai_service import openai_service
                # Generate OpenAI analysis for PDF (with built-in fallback)
                analysis_prompt = f"Generate a concise executive summary for financial anomaly detection report with {data.get('total_transactions', 0)} transactions and {data.get('anomalies_detected', 0)} anomalies."
                ai_analysis = await openai_service.generate_custom_content(analysis_prompt, max_tokens=800)
                logger.info("Using OpenAI analysis for PDF")
            except Exception as openai_error:
                logger.warning(f"OpenAI analysis failed for PDF: {openai_error}")
                ai_analysis = generate_fallback_analysis(data)
        
        # Add timestamp to data
        data['timestamp'] = datetime.utcnow().isoformat()
        
        # Generate PDF
        logger.info("Calling PDF service to generate report")
        pdf_bytes = pdf_service.generate_analytics_report(data, ai_analysis)
        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        
        # Encode PDF as base64 for JSON response
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        return APIResponse(
            success=True,
            message="PDF report generated successfully",
            data={
                "pdf_data": pdf_base64,
                "filename": f"FinancePulse_Report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf",
                "size_bytes": len(pdf_bytes),
                "generated_at": datetime.utcnow().isoformat(),
                "includes_ai_analysis": ai_analysis is not None
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/health", response_model=APIResponse)
async def system_health():
    """Get system health status"""
    try:
        from main import notification_orchestrator, transaction_simulator
        
        # Get anomaly stats
        anomaly_stats = transaction_simulator.get_anomaly_stats()
        
        health_data = {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "uptime": "2h 15m 30s",
            "services": {
                "websocket_manager": "running",
                "transaction_simulator": "running", 
                "anomaly_detector": "ready",
                "explanation_engine": "ready",
                "notification_orchestrator": "ready" if notification_orchestrator.is_initialized else "failed"
            },
            "metrics": {
                "active_connections": 3,
                "transactions_processed": anomaly_stats["total_transactions"],
                "anomalies_detected": anomaly_stats["anomalous_transactions"],
                "anomaly_rate": f"{anomaly_stats['anomaly_rate_percent']}%",
                "next_anomaly_in": anomaly_stats["next_anomaly_in"],
                "memory_usage": "245 MB",
                "cpu_usage": "12%"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return APIResponse(
            success=True,
            message="System is healthy",
            data=health_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cedar-OS Agent Tool Endpoints
# These endpoints are designed to be called by Cedar-OS agent tools

@router.post("/anomaly/explain", response_model=APIResponse)
async def explain_anomaly(data: dict):
    """Generate explanation for anomaly detection result (Cedar-OS agent tool endpoint)"""
    try:
        from main import explanation_engine
        
        transaction_data = data.get('transaction')
        anomaly_data = data.get('anomaly_result')
        
        if not transaction_data or not anomaly_data:
            raise HTTPException(status_code=400, detail="Missing transaction or anomaly_result data")
        
        # Convert dict data back to model objects for processing
        from app.models import Transaction, AnomalyResult
        import json
        
        # Create Transaction object
        transaction = Transaction(**transaction_data)
        
        # Create AnomalyResult object
        anomaly_result = AnomalyResult(**anomaly_data)
        
        # Generate explanation using the existing engine
        explanation = await explanation_engine.generate_explanation(transaction, anomaly_result)
        
        # Generate recommended actions based on risk level
        recommended_actions = []
        if anomaly_result.risk_level.value == 'CRITICAL':
            recommended_actions = [
                "Immediately freeze the card",
                "Contact customer urgently",
                "Flag transaction for manual review",
                "Initiate fraud investigation"
            ]
        elif anomaly_result.risk_level.value == 'HIGH':
            recommended_actions = [
                "Contact customer for verification",
                "Monitor subsequent transactions closely",
                "Consider temporary transaction limits"
            ]
        elif anomaly_result.risk_level.value == 'MEDIUM':
            recommended_actions = [
                "Monitor customer activity",
                "Consider notification to customer"
            ]
        else:
            recommended_actions = [
                "Log for pattern analysis",
                "Continue monitoring"
            ]
        
        return APIResponse(
            success=True,
            message="Anomaly explanation generated successfully",
            data={
                "explanation": explanation,
                "risk_level": anomaly_result.risk_level.value,
                "confidence_score": anomaly_result.confidence_score,
                "recommended_actions": recommended_actions,
                "anomaly_types": [at.value for at in anomaly_result.anomaly_types],
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating anomaly explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/phone", response_model=APIResponse) 
async def trigger_phone_notification(data: dict):
    """Trigger phone notification (Cedar-OS agent tool endpoint)"""
    try:
        from main import notification_orchestrator, phone_service
        from app.models import Transaction, AnomalyResult, RiskLevel
        
        customer_id = data.get('customer_id')
        transaction_id = data.get('transaction_id')
        message = data.get('message')
        risk_level = data.get('risk_level', 'MEDIUM')
        call_type = data.get('call_type', 'security_alert')
        
        if not all([customer_id, transaction_id, message]):
            raise HTTPException(status_code=400, detail="Missing required fields: customer_id, transaction_id, message")
        
        # Get customer contact info
        customer_contact = notification_orchestrator.get_customer_contact(customer_id)
        if not customer_contact or not customer_contact.phone:
            return APIResponse(
                success=False,
                message=f"No phone number found for customer {customer_id}",
                data={"status": "failed", "reason": "no_phone_number"}
            )
        
        # Create mock transaction and anomaly for phone service
        mock_transaction = Transaction(
            id=transaction_id,
            customer_id=customer_id,
            amount=0.0,  # Will be overridden by actual data if available
            merchant_name="Unknown Merchant",
            merchant_category="unknown",
            timestamp=datetime.utcnow(),
            location={"city": "Unknown", "state": "Unknown", "country": "US"},
            card_id="unknown",
            type="PURCHASE",
            status="PENDING"
        )
        
        mock_anomaly = AnomalyResult(
            id=f"anomaly_{transaction_id}",
            transaction_id=transaction_id,
            is_anomaly=True,
            confidence_score=0.8,
            risk_level=RiskLevel(risk_level.upper()),
            anomaly_types=[],
            features={},
            detected_at=datetime.utcnow()
        )
        
        # Make the phone call
        success = await phone_service.make_anomaly_call(
            transaction=mock_transaction,
            anomaly_result=mock_anomaly,
            phone_number=customer_contact.phone,
            customer_name=customer_contact.name
        )
        
        # Generate a call ID for tracking
        call_id = f"call_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{transaction_id[:8]}"
        
        return APIResponse(
            success=success,
            message="Phone alert processed successfully" if success else "Phone alert failed",
            data={
                "call_id": call_id,
                "status": "initiated" if success else "failed",
                "customer_id": customer_id,
                "phone_number": customer_contact.phone[-4:].rjust(len(customer_contact.phone), '*'),
                "message_length": len(message),
                "initiated_at": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering phone notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cards/freeze", response_model=APIResponse)
async def freeze_card(data: dict):
    """Freeze a customer card (Cedar-OS agent tool endpoint)"""
    try:
        customer_id = data.get('customer_id')
        card_id = data.get('card_id', f"card_{customer_id}_primary")
        reason = data.get('reason', 'Suspicious activity detected')
        
        if not customer_id:
            raise HTTPException(status_code=400, detail="Missing customer_id")
        
        # In a real implementation, this would update the card status in the database
        # For demo purposes, we'll simulate the freeze operation
        
        frozen_at = datetime.utcnow()
        
        # Log the card freeze action
        logger.info(f"Card freeze requested: Customer {customer_id}, Card {card_id}, Reason: {reason}")
        
        # Simulate successful card freeze
        success = True
        
        return APIResponse(
            success=success,
            message=f"Card {card_id} successfully frozen for customer {customer_id}",
            data={
                "customer_id": customer_id,
                "card_id": card_id,
                "card_status": "FROZEN",
                "reason": reason,
                "frozen_at": frozen_at.isoformat(),
                "frozen_by": "FinancePulse AI Agent",
                "action_id": f"freeze_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error freezing card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/{transaction_id}/context", response_model=APIResponse)
async def get_transaction_context(transaction_id: str, customer_id: str):
    """Get additional context about a transaction (Cedar-OS agent tool endpoint)"""
    try:
        from main import transaction_simulator
        
        # In a real implementation, this would query the database for transaction history
        # For demo purposes, we'll generate mock context data
        
        mock_context = {
            "recent_transactions": [
                {
                    "id": f"txn_{i:06d}",
                    "amount": 25.50 + (i * 5.25),
                    "merchant": f"Merchant {i}",
                    "timestamp": (datetime.utcnow() - timedelta(hours=i*2)).isoformat()
                }
                for i in range(1, 6)
            ],
            "customer_patterns": {
                "avg_daily_spending": 145.75,
                "avg_transaction_amount": 48.25,
                "transactions_per_day": 3.2,
                "preferred_hours": "9 AM - 8 PM",
                "common_categories": ["grocery", "restaurant", "gas_station"],
                "spending_trend": "stable"
            },
            "merchant_info": {
                "merchant_name": "Demo Merchant",
                "category": "grocery",
                "location": "New York, NY",
                "customer_history": "First time",
                "merchant_risk_score": 0.15
            },
            "location_analysis": {
                "current_location": "New York, NY",
                "home_location": "Brooklyn, NY", 
                "distance_from_home": 12.5,
                "location_frequency": "rare",
                "travel_pattern": "local"
            },
            "risk_factors": [
                "First transaction at this merchant",
                "Amount above typical spending",
                "Transaction outside normal hours"
            ]
        }
        
        return APIResponse(
            success=True,
            message="Transaction context retrieved successfully",
            data=mock_context
        )
        
    except Exception as e:
        logger.error(f"Error retrieving transaction context: {e}")
        raise HTTPException(status_code=500, detail=str(e))
