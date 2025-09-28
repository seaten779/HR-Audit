#!/usr/bin/env python3
"""
Advanced Fraud Detection System for FinancePulse
Based on US Banking Standards and Real-World Fraud Patterns
"""

import json
import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
from decimal import Decimal

logger = logging.getLogger(__name__)

class FraudRiskLevel(Enum):
    """Fraud risk levels based on US banking standards"""
    LOW = "low"           # 0-30% risk score
    MEDIUM = "medium"     # 31-60% risk score  
    HIGH = "high"         # 61-80% risk score
    CRITICAL = "critical" # 81-100% risk score

class FraudCategory(Enum):
    """Types of fraud patterns based on US banking regulations"""
    VELOCITY_FRAUD = "velocity_fraud"           # Multiple transactions in short time
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"   # Unusual location patterns
    HIGH_VALUE_ANOMALY = "high_value_anomaly"   # Amounts significantly above normal
    MERCHANT_ANOMALY = "merchant_anomaly"       # Unusual merchant categories
    TIME_ANOMALY = "time_anomaly"               # Off-hours transactions
    ACCOUNT_TAKEOVER = "account_takeover"       # Signs of compromised account
    CARD_NOT_PRESENT = "card_not_present"       # CNP transaction risks
    SYNTHETIC_IDENTITY = "synthetic_identity"   # Fake identity indicators

@dataclass
class FraudFlag:
    """Individual fraud indicator"""
    category: FraudCategory
    severity: float  # 0.0 to 1.0
    description: str
    confidence: float  # 0.0 to 1.0
    evidence: Dict[str, Any]

@dataclass
class CustomerProfile:
    """Customer spending profile and behavior patterns"""
    customer_id: int
    name: str
    email: str
    age: int
    address: str
    usual_location: str
    avg_bank_balance: float
    avg_monthly_purchases: float
    avg_yearly_purchases: float
    avg_closing_balance: float

@dataclass  
class TransactionAnalysis:
    """Complete fraud analysis of a transaction"""
    transaction_id: str
    customer: CustomerProfile
    transaction_amount: float
    merchant_name: str
    location: str
    timestamp: datetime
    fraud_flags: List[FraudFlag]
    overall_risk_score: float
    risk_level: FraudRiskLevel
    should_call_customer: bool
    call_urgency: str
    explanation: str

class USBankingFraudStandards:
    """US banking fraud detection criteria based on industry standards"""
    
    # Velocity thresholds (based on Federal Reserve guidelines)
    MAX_TRANSACTIONS_PER_HOUR = 5
    MAX_TRANSACTIONS_PER_DAY = 20
    MAX_AMOUNT_PER_DAY_MULTIPLIER = 3.0  # 3x normal daily spend
    
    # Geographic thresholds
    SUSPICIOUS_FOREIGN_COUNTRIES = [
        "Nigeria", "Russia", "China", "North Korea", "Iran", 
        "Romania", "Pakistan", "Vietnam", "Ukraine"
    ]
    
    # High-risk merchant categories (based on Visa/MasterCard MCCs)
    HIGH_RISK_MERCHANT_CATEGORIES = [
        "cryptocurrency", "gambling", "adult_entertainment", "money_transfer",
        "prepaid_cards", "payday_loans", "debt_collection", "telemarketing"
    ]
    
    # Time-based thresholds  
    OFF_HOURS_START = 23  # 11 PM
    OFF_HOURS_END = 6     # 6 AM
    
    # Amount-based thresholds
    STRUCTURING_THRESHOLD = 10000  # $10,000 CTR threshold
    UNUSUAL_AMOUNT_MULTIPLIER = 5.0  # 5x normal transaction

class AdvancedFraudDetector:
    """Advanced fraud detection using real customer data and US banking standards"""
    
    def __init__(self):
        self.customers: Dict[str, CustomerProfile] = {}
        self.transaction_history: List[Dict] = []
        self.fraud_patterns: Dict = {}
        self.load_customer_data()
        self.load_transaction_data()
    
    def load_customer_data(self):
        """Load customer data from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), "../../../data/customer_data.json")
            with open(data_path, 'r') as f:
                customers_data = json.load(f)
            
            for customer_data in customers_data:
                profile = CustomerProfile(
                    customer_id=customer_data["customer_id"],
                    name=customer_data["name"],
                    email=customer_data["email"],
                    age=customer_data["age"],
                    address=customer_data["address"],
                    usual_location=customer_data["usual_payment_location"],
                    avg_bank_balance=customer_data["background"]["average_bank_balance"],
                    avg_monthly_purchases=customer_data["average_monthly_purchases"],
                    avg_yearly_purchases=customer_data["average_yearly_purchases"],
                    avg_closing_balance=customer_data["average_closing_balance"]
                )
                self.customers[customer_data["name"]] = profile
            
            logger.info(f"✅ Loaded {len(self.customers)} customer profiles")
        except Exception as e:
            logger.error(f"Error loading customer data: {e}")
    
    def load_transaction_data(self):
        """Load transaction data from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), "../../../data/transaction_data.json")
            with open(data_path, 'r') as f:
                self.transaction_history = json.load(f)
            
            logger.info(f"✅ Loaded {len(self.transaction_history)} transaction records")
        except Exception as e:
            logger.error(f"Error loading transaction data: {e}")
    
    def analyze_transaction(self, customer_name: str, transaction_data: Dict) -> TransactionAnalysis:
        """Perform comprehensive fraud analysis on a transaction"""
        
        customer = self.customers.get(customer_name)
        if not customer:
            logger.error(f"Customer {customer_name} not found")
            return None
        
        # Parse transaction data
        if isinstance(transaction_data, dict):
            # Already flagged transaction
            transaction_detail = transaction_data
            amount = self._extract_amount(transaction_detail["description"])
            merchant = self._extract_merchant(transaction_detail["description"])
            location = self._extract_location(transaction_detail.get("description", ""))
        else:
            # Regular transaction string
            amount = self._extract_amount(transaction_data)
            merchant = self._extract_merchant(transaction_data)
            location = self._extract_location(transaction_data)
            transaction_detail = {"description": transaction_data}
        
        transaction_id = f"txn_{customer.customer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Analyze for fraud patterns
        fraud_flags = self._detect_fraud_patterns(
            customer, amount, merchant, location, transaction_detail
        )
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(fraud_flags, customer, amount)
        risk_level = self._determine_risk_level(risk_score)
        
        # Determine if customer call is needed
        should_call, urgency = self._should_call_customer(risk_level, fraud_flags)
        
        # Generate explanation
        explanation = self._generate_explanation(fraud_flags, customer, amount, merchant)
        
        return TransactionAnalysis(
            transaction_id=transaction_id,
            customer=customer,
            transaction_amount=amount,
            merchant_name=merchant,
            location=location,
            timestamp=datetime.now(),
            fraud_flags=fraud_flags,
            overall_risk_score=risk_score,
            risk_level=risk_level,
            should_call_customer=should_call,
            call_urgency=urgency,
            explanation=explanation
        )
    
    def _detect_fraud_patterns(self, customer: CustomerProfile, amount: float, 
                             merchant: str, location: str, transaction_data: Dict) -> List[FraudFlag]:
        """Detect various fraud patterns based on US banking standards"""
        flags = []
        
        # 1. HIGH-VALUE ANOMALY DETECTION
        monthly_avg = customer.avg_monthly_purchases / 30  # Daily average
        if amount > monthly_avg * USBankingFraudStandards.UNUSUAL_AMOUNT_MULTIPLIER:
            flags.append(FraudFlag(
                category=FraudCategory.HIGH_VALUE_ANOMALY,
                severity=min(1.0, amount / (monthly_avg * 10)),
                description=f"Transaction amount ${amount:.2f} is {amount/monthly_avg:.1f}x higher than daily average",
                confidence=0.85,
                evidence={"amount": amount, "daily_avg": monthly_avg, "multiplier": amount/monthly_avg}
            ))
        
        # 2. GEOGRAPHIC ANOMALY DETECTION  
        if location and location != customer.usual_location:
            # Check for foreign countries
            is_foreign = any(country in location for country in USBankingFraudStandards.SUSPICIOUS_FOREIGN_COUNTRIES)
            if is_foreign:
                flags.append(FraudFlag(
                    category=FraudCategory.GEOGRAPHIC_ANOMALY,
                    severity=0.9,
                    description=f"Transaction in suspicious foreign location: {location}",
                    confidence=0.95,
                    evidence={"location": location, "usual_location": customer.usual_location}
                ))
            elif "," in location and customer.usual_location not in location:
                flags.append(FraudFlag(
                    category=FraudCategory.GEOGRAPHIC_ANOMALY,
                    severity=0.6,
                    description=f"Transaction in unusual domestic location: {location}",
                    confidence=0.75,
                    evidence={"location": location, "usual_location": customer.usual_location}
                ))
        
        # 3. MERCHANT CATEGORY ANOMALY
        merchant_lower = merchant.lower()
        high_risk_indicators = [
            ("crypto", "cryptocurrency"), ("gambling", "betting"), ("casino", "gambling"),
            ("bitcoin", "cryptocurrency"), ("forex", "foreign_exchange"), ("lottery", "gambling"),
            ("adult", "adult_entertainment"), ("escort", "adult_entertainment")
        ]
        
        for indicator, category in high_risk_indicators:
            if indicator in merchant_lower:
                flags.append(FraudFlag(
                    category=FraudCategory.MERCHANT_ANOMALY,
                    severity=0.8,
                    description=f"High-risk merchant category detected: {category}",
                    confidence=0.9,
                    evidence={"merchant": merchant, "category": category, "indicator": indicator}
                ))
                break
        
        # 4. TIME-BASED ANOMALY (if we have timestamp info)
        current_hour = datetime.now().hour
        if (current_hour >= USBankingFraudStandards.OFF_HOURS_START or 
            current_hour <= USBankingFraudStandards.OFF_HOURS_END):
            flags.append(FraudFlag(
                category=FraudCategory.TIME_ANOMALY,
                severity=0.4,
                description=f"Transaction occurred during off-hours: {current_hour}:00",
                confidence=0.6,
                evidence={"hour": current_hour}
            ))
        
        # 5. VELOCITY PATTERNS (simulated based on existing data)
        if "5 transactions" in str(transaction_data) or "multiple" in str(transaction_data).lower():
            flags.append(FraudFlag(
                category=FraudCategory.VELOCITY_FRAUD,
                severity=0.85,
                description="Multiple transactions detected in short timeframe",
                confidence=0.9,
                evidence={"pattern": "velocity_spike"}
            ))
        
        # 6. STRUCTURING DETECTION (amounts just under $10,000)
        if 9000 <= amount < USBankingFraudStandards.STRUCTURING_THRESHOLD:
            flags.append(FraudFlag(
                category=FraudCategory.ACCOUNT_TAKEOVER,
                severity=0.7,
                description=f"Potential structuring: Amount ${amount:.2f} just under CTR threshold",
                confidence=0.8,
                evidence={"amount": amount, "ctr_threshold": USBankingFraudStandards.STRUCTURING_THRESHOLD}
            ))
        
        # 7. CARD-NOT-PRESENT INDICATORS
        online_indicators = ["online", "web", "internet", "digital", ".com"]
        if any(indicator in merchant_lower for indicator in online_indicators):
            # Higher risk for high amounts online
            if amount > customer.avg_monthly_purchases * 0.5:  # More than half monthly spending
                flags.append(FraudFlag(
                    category=FraudCategory.CARD_NOT_PRESENT,
                    severity=0.6,
                    description="High-value online transaction (card-not-present risk)",
                    confidence=0.7,
                    evidence={"merchant": merchant, "amount": amount, "channel": "online"}
                ))
        
        return flags
    
    def _calculate_risk_score(self, flags: List[FraudFlag], customer: CustomerProfile, amount: float) -> float:
        """Calculate overall risk score using weighted fraud flags"""
        if not flags:
            return 0.0
        
        # Base score from flags
        base_score = sum(flag.severity * flag.confidence for flag in flags)
        
        # Normalize by number of flags (avoid score inflation)
        base_score = base_score / len(flags) if flags else 0
        
        # Adjust based on customer profile
        customer_risk_multiplier = 1.0
        
        # Higher risk for customers with lower balances doing large transactions
        if amount > customer.avg_bank_balance * 0.1:  # More than 10% of balance
            customer_risk_multiplier += 0.2
        
        # Age-based adjustments (elderly more vulnerable)
        if customer.age >= 65:
            customer_risk_multiplier += 0.1
        elif customer.age <= 25:
            customer_risk_multiplier += 0.05
        
        final_score = min(1.0, base_score * customer_risk_multiplier)
        return final_score
    
    def _determine_risk_level(self, risk_score: float) -> FraudRiskLevel:
        """Determine risk level based on score"""
        if risk_score >= 0.81:
            return FraudRiskLevel.CRITICAL
        elif risk_score >= 0.61:
            return FraudRiskLevel.HIGH
        elif risk_score >= 0.31:
            return FraudRiskLevel.MEDIUM
        else:
            return FraudRiskLevel.LOW
    
    def _should_call_customer(self, risk_level: FraudRiskLevel, flags: List[FraudFlag]) -> Tuple[bool, str]:
        """Determine if customer should be called and urgency level"""
        if risk_level == FraudRiskLevel.CRITICAL:
            return True, "IMMEDIATE"
        elif risk_level == FraudRiskLevel.HIGH:
            return True, "URGENT"
        elif risk_level == FraudRiskLevel.MEDIUM:
            # Call if certain high-priority patterns detected
            high_priority_categories = {
                FraudCategory.GEOGRAPHIC_ANOMALY,
                FraudCategory.HIGH_VALUE_ANOMALY,
                FraudCategory.VELOCITY_FRAUD
            }
            if any(flag.category in high_priority_categories for flag in flags):
                return True, "STANDARD"
        
        return False, "NONE"
    
    def _generate_explanation(self, flags: List[FraudFlag], customer: CustomerProfile, 
                            amount: float, merchant: str) -> str:
        """Generate human-readable explanation of fraud detection"""
        if not flags:
            return "No fraud indicators detected. Transaction appears normal."
        
        explanations = []
        for flag in sorted(flags, key=lambda f: f.severity, reverse=True):
            explanations.append(f"• {flag.description} (Confidence: {flag.confidence*100:.0f}%)")
        
        summary = f"Detected {len(flags)} fraud indicator(s) for ${amount:.2f} transaction at {merchant}:"
        return summary + "\n" + "\n".join(explanations)
    
    def _extract_amount(self, transaction_str: str) -> float:
        """Extract dollar amount from transaction string"""
        import re
        # Look for $X,XXX.XX patterns
        amount_match = re.search(r'\$([0-9,]+\.?[0-9]*)', transaction_str)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            return float(amount_str)
        return 0.0
    
    def _extract_merchant(self, transaction_str: str) -> str:
        """Extract merchant name from transaction string"""
        import re
        # Look for text between quotes or after "at"
        merchant_match = re.search(r"at '([^']+)'", transaction_str)
        if merchant_match:
            return merchant_match.group(1)
        
        merchant_match = re.search(r"at ([^,]+)", transaction_str)
        if merchant_match:
            return merchant_match.group(1).strip()
        
        return "Unknown Merchant"
    
    def _extract_location(self, transaction_str: str) -> str:
        """Extract location from transaction string"""
        import re
        # Look for city, state patterns or country names
        location_match = re.search(r"in ([A-Za-z\s,]+)(?:\s|$)", transaction_str)
        if location_match:
            return location_match.group(1).strip()
        
        # Check for foreign countries
        for country in USBankingFraudStandards.SUSPICIOUS_FOREIGN_COUNTRIES + ["France", "Japan", "Germany", "UK"]:
            if country in transaction_str:
                return country
        
        return ""

    def get_flagged_transactions(self) -> List[Dict]:
        """Get all pre-flagged transactions from the data"""
        flagged = []
        for transaction in self.transaction_history:
            if isinstance(transaction["transaction_detail"], dict):
                if transaction["transaction_detail"].get("status") == "flagged":
                    flagged.append(transaction)
        return flagged

    def analyze_all_flagged_transactions(self) -> List[TransactionAnalysis]:
        """Analyze all flagged transactions in the dataset"""
        flagged_transactions = self.get_flagged_transactions()
        analyses = []
        
        for transaction in flagged_transactions:
            analysis = self.analyze_transaction(
                transaction["customer_name"],
                transaction["transaction_detail"]
            )
            if analysis:
                analyses.append(analysis)
        
        return analyses

# Global instance
advanced_fraud_detector = AdvancedFraudDetector()