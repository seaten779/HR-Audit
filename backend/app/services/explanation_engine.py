"""
Explanation Engine
Generates human-readable explanations for anomaly detection results
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from app.models import Transaction, AnomalyResult, AnomalyType, RiskLevel


logger = logging.getLogger(__name__)


class ExplanationEngine:
    """Generates human-readable explanations for detected anomalies"""
    
    def __init__(self):
        self.explanation_templates = self._load_explanation_templates()
    
    async def generate_explanation(self, transaction: Transaction, anomaly_result: AnomalyResult) -> str:
        """Generate a concise explanation for why a transaction was flagged"""
        try:
            if not anomaly_result.is_anomaly:
                return "Transaction appears normal based on customer patterns."
            
            # Build explanation based on anomaly types
            explanations = []
            
            for anomaly_type in anomaly_result.anomaly_types:
                explanation = self._get_type_explanation(anomaly_type, transaction, anomaly_result)
                if explanation:
                    explanations.append(explanation)
            
            # If no specific explanations, use generic one
            if not explanations:
                explanations.append(self._get_generic_explanation(transaction, anomaly_result))
            
            # Combine explanations
            combined_explanation = self._combine_explanations(explanations, anomaly_result.confidence_score)
            
            return combined_explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Transaction flagged for manual review due to unusual patterns."
    
    def _load_explanation_templates(self) -> Dict[AnomalyType, Dict[str, str]]:
        """Load explanation templates for different anomaly types"""
        return {
            AnomalyType.UNUSUAL_AMOUNT: {
                "template": "Transaction amount ${amount:.2f} is {multiplier}x larger than customer's typical spending of ${avg_amount:.2f}",
                "action": "verify large purchase"
            },
            AnomalyType.UNUSUAL_TIME: {
                "template": "Transaction occurred at {time} which is outside customer's normal hours ({typical_hours})",
                "action": "confirm transaction timing"
            },
            AnomalyType.UNUSUAL_FREQUENCY: {
                "template": "Customer has made {count} transactions today, {multiplier}x their typical daily volume",
                "action": "monitor account activity"
            },
            AnomalyType.UNUSUAL_LOCATION: {
                "template": "Transaction in {location} is {distance} miles from customer's usual area",
                "action": "verify customer location"
            },
            AnomalyType.UNUSUAL_MERCHANT: {
                "template": "First transaction at {merchant} - not in customer's regular merchant list",
                "action": "confirm new merchant"
            },
            AnomalyType.VELOCITY_SPIKE: {
                "template": "Multiple rapid transactions detected within {timeframe} minutes",
                "action": "check for card compromise"
            },
            AnomalyType.AMOUNT_PATTERN: {
                "template": "Transaction amount follows suspicious pattern (round numbers or card testing)",
                "action": "investigate transaction pattern"
            },
            AnomalyType.GEOGRAPHIC_OUTLIER: {
                "template": "Transaction location is geographically inconsistent with recent activity",
                "action": "verify travel plans"
            }
        }
    
    def _get_type_explanation(self, anomaly_type: AnomalyType, transaction: Transaction, anomaly_result: AnomalyResult) -> Optional[str]:
        """Get explanation for a specific anomaly type"""
        template_info = self.explanation_templates.get(anomaly_type)
        if not template_info:
            return None
        
        try:
            template = template_info["template"]
            
            # Fill in template variables based on anomaly type
            if anomaly_type == AnomalyType.UNUSUAL_AMOUNT:
                avg_amount = anomaly_result.features.get("amount_vs_avg", 1) * transaction.amount
                multiplier = transaction.amount / max(avg_amount, 1)
                return template.format(
                    amount=transaction.amount,
                    avg_amount=avg_amount,
                    multiplier=f"{multiplier:.1f}"
                )
            
            elif anomaly_type == AnomalyType.UNUSUAL_TIME:
                time_str = transaction.timestamp.strftime("%I:%M %p")
                typical_hours = "9 AM - 6 PM"  # Could be personalized
                return template.format(
                    time=time_str,
                    typical_hours=typical_hours
                )
            
            elif anomaly_type == AnomalyType.UNUSUAL_FREQUENCY:
                count = 5  # Would be calculated from actual data
                multiplier = 3  # Would be calculated from baseline
                return template.format(
                    count=count,
                    multiplier=multiplier
                )
            
            elif anomaly_type == AnomalyType.UNUSUAL_LOCATION:
                location = f"{transaction.location.get('city', 'Unknown')}, {transaction.location.get('state', '')}"
                distance = 150  # Would be calculated from actual data
                return template.format(
                    location=location,
                    distance=distance
                )
            
            elif anomaly_type == AnomalyType.UNUSUAL_MERCHANT:
                return template.format(merchant=transaction.merchant_name)
            
            elif anomaly_type == AnomalyType.VELOCITY_SPIKE:
                timeframe = 15  # Would be calculated from actual data
                return template.format(timeframe=timeframe)
            
            elif anomaly_type == AnomalyType.AMOUNT_PATTERN:
                return template
            
            elif anomaly_type == AnomalyType.GEOGRAPHIC_OUTLIER:
                return template
            
            else:
                return f"Unusual {anomaly_type.value.replace('_', ' ')} detected"
                
        except Exception as e:
            logger.error(f"Error formatting explanation template: {e}")
            return f"Unusual {anomaly_type.value.replace('_', ' ')} detected"
    
    def _get_generic_explanation(self, transaction: Transaction, anomaly_result: AnomalyResult) -> str:
        """Generate generic explanation when specific ones aren't available"""
        confidence_pct = int(anomaly_result.confidence_score * 100)
        
        if anomaly_result.risk_level == RiskLevel.CRITICAL:
            return f"High-risk transaction detected with {confidence_pct}% confidence - immediate action required"
        elif anomaly_result.risk_level == RiskLevel.HIGH:
            return f"Suspicious transaction patterns detected with {confidence_pct}% confidence"
        elif anomaly_result.risk_level == RiskLevel.MEDIUM:
            return f"Moderately unusual transaction flagged for review ({confidence_pct}% confidence)"
        else:
            return f"Minor anomaly detected - monitor for additional suspicious activity"
    
    def _combine_explanations(self, explanations: List[str], confidence_score: float) -> str:
        """Combine multiple explanations into a coherent message"""
        if len(explanations) == 1:
            explanation = explanations[0]
        elif len(explanations) == 2:
            explanation = f"{explanations[0]} and {explanations[1].lower()}"
        else:
            # Multiple explanations - summarize
            explanation = f"Multiple suspicious patterns detected: {explanations[0]} (plus {len(explanations) - 1} other factors)"
        
        # Add confidence qualifier
        confidence_pct = int(confidence_score * 100)
        if confidence_pct >= 90:
            qualifier = "Very high confidence"
        elif confidence_pct >= 70:
            qualifier = "High confidence"
        elif confidence_pct >= 50:
            qualifier = "Moderate confidence"
        else:
            qualifier = "Low confidence"
        
        return f"{explanation}. {qualifier} ({confidence_pct}%) anomaly detection."