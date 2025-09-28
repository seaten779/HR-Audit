"""
Transaction Simulator
Generates realistic financial transactions using mock data and Nessie API
"""

import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import httpx
from app.core.config import settings
from app.models import Transaction, TransactionType, MerchantCategory

logger = logging.getLogger(__name__)


class TransactionSimulator:
    """Simulates realistic financial transactions"""
    
    def __init__(self):
        self.customer_profiles = self._generate_customer_profiles()
        self.merchant_data = self._generate_merchant_data()
        self.transaction_history: List[Transaction] = []
        
        # Anomaly injection tracking
        self.transaction_counter = 0
        self.anomaly_interval = random.randint(20, 30)  # Inject anomaly every 20-30 transactions
        self.last_anomaly_transaction = 0
        
        # Nessie API client (if enabled)
        self.nessie_client = None
        if settings.ENABLE_NESSIE_API and settings.NESSIE_API_KEY:
            self.nessie_client = httpx.AsyncClient(
                base_url=settings.NESSIE_BASE_URL,
                headers={"Authorization": f"Bearer {settings.NESSIE_API_KEY}"}
            )
    
    def _generate_customer_profiles(self) -> List[Dict[str, Any]]:
        """Generate mock customer profiles with spending patterns"""
        profiles = []
        
        # Profile archetypes with different spending behaviors
        archetypes = [
            {
                "type": "conservative_saver",
                "daily_budget": 50.0,
                "preferred_categories": [MerchantCategory.GROCERY, MerchantCategory.GAS_STATION],
                "transaction_frequency": 0.3,
                "risk_tolerance": 0.1
            },
            {
                "type": "average_spender", 
                "daily_budget": 120.0,
                "preferred_categories": [MerchantCategory.GROCERY, MerchantCategory.RESTAURANT, MerchantCategory.RETAIL],
                "transaction_frequency": 0.6,
                "risk_tolerance": 0.3
            },
            {
                "type": "high_spender",
                "daily_budget": 300.0,
                "preferred_categories": [MerchantCategory.RESTAURANT, MerchantCategory.RETAIL, MerchantCategory.ENTERTAINMENT],
                "transaction_frequency": 1.0,
                "risk_tolerance": 0.5
            },
            {
                "type": "frequent_traveler",
                "daily_budget": 200.0,
                "preferred_categories": [MerchantCategory.TRAVEL, MerchantCategory.RESTAURANT, MerchantCategory.GAS_STATION],
                "transaction_frequency": 0.8,
                "risk_tolerance": 0.4
            }
        ]
        
        # Generate 20 customer profiles
        for i in range(20):
            archetype = random.choice(archetypes)
            profiles.append({
                "customer_id": f"customer_{i+1:03d}",
                "account_id": f"account_{i+1:03d}",
                "name": f"Customer {i+1}",
                "balance": random.uniform(1000, 10000),
                **archetype,
                "location": {
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "lat": round(random.uniform(25.0, 49.0), 6),
                    "lng": round(random.uniform(-125.0, -65.0), 6)
                }
            })
        
        return profiles
    
    def _generate_merchant_data(self) -> Dict[MerchantCategory, List[Dict[str, Any]]]:
        """Generate realistic merchant data by category"""
        merchants = {
            MerchantCategory.GROCERY: [
                {"name": "Whole Foods Market", "avg_amount": 85.0},
                {"name": "Safeway", "avg_amount": 65.0},
                {"name": "Trader Joe's", "avg_amount": 45.0},
                {"name": "Kroger", "avg_amount": 75.0},
                {"name": "Target Grocery", "avg_amount": 55.0}
            ],
            MerchantCategory.RESTAURANT: [
                {"name": "McDonald's", "avg_amount": 12.0},
                {"name": "Starbucks", "avg_amount": 8.0},
                {"name": "Chipotle", "avg_amount": 18.0},
                {"name": "The Cheesecake Factory", "avg_amount": 45.0},
                {"name": "Local Bistro", "avg_amount": 65.0}
            ],
            MerchantCategory.GAS_STATION: [
                {"name": "Shell", "avg_amount": 45.0},
                {"name": "Exxon", "avg_amount": 50.0},
                {"name": "BP", "avg_amount": 42.0},
                {"name": "Chevron", "avg_amount": 48.0}
            ],
            MerchantCategory.RETAIL: [
                {"name": "Amazon", "avg_amount": 125.0},
                {"name": "Target", "avg_amount": 85.0},
                {"name": "Walmart", "avg_amount": 65.0},
                {"name": "Best Buy", "avg_amount": 250.0},
                {"name": "Macy's", "avg_amount": 120.0}
            ],
            MerchantCategory.ENTERTAINMENT: [
                {"name": "Netflix", "avg_amount": 15.99},
                {"name": "AMC Theaters", "avg_amount": 28.0},
                {"name": "Spotify", "avg_amount": 9.99},
                {"name": "Concert Venue", "avg_amount": 85.0}
            ],
            MerchantCategory.TRAVEL: [
                {"name": "Delta Airlines", "avg_amount": 350.0},
                {"name": "Hilton Hotels", "avg_amount": 180.0},
                {"name": "Uber", "avg_amount": 25.0},
                {"name": "Hertz", "avg_amount": 120.0}
            ],
            MerchantCategory.HEALTHCARE: [
                {"name": "CVS Pharmacy", "avg_amount": 35.0},
                {"name": "Walgreens", "avg_amount": 28.0},
                {"name": "Medical Center", "avg_amount": 150.0}
            ],
            MerchantCategory.ONLINE: [
                {"name": "PayPal", "avg_amount": 75.0},
                {"name": "Amazon Web Services", "avg_amount": 45.0},
                {"name": "eBay", "avg_amount": 85.0}
            ],
            MerchantCategory.ATM: [
                {"name": "Bank of America ATM", "avg_amount": 100.0},
                {"name": "Chase ATM", "avg_amount": 80.0},
                {"name": "Wells Fargo ATM", "avg_amount": 120.0}
            ]
        }
        
        return merchants
    
    async def generate_transaction(self, customer_profile: Optional[Dict] = None) -> Transaction:
        """Generate a single realistic transaction"""
        
        # Increment transaction counter
        self.transaction_counter += 1
        
        # Check if we should inject an anomaly
        if (self.transaction_counter - self.last_anomaly_transaction) >= self.anomaly_interval:
            logger.info(f"🎯 Injecting anomaly at transaction #{self.transaction_counter}")
            self.last_anomaly_transaction = self.transaction_counter
            self.anomaly_interval = random.randint(20, 30)  # Reset interval for next anomaly
            
            # Generate a suspicious transaction instead
            return await self.generate_suspicious_transaction()
        
        # Select customer profile
        if not customer_profile:
            customer_profile = random.choice(self.customer_profiles)
        
        # Determine transaction type and category based on profile
        transaction_type = self._select_transaction_type(customer_profile)
        merchant_category = self._select_merchant_category(customer_profile)
        
        # Ensure we have merchant data for this category
        if merchant_category not in self.merchant_data:
            # Fallback to GROCERY if somehow an unsupported category is selected
            merchant_category = MerchantCategory.GROCERY
        
        # Select merchant and calculate amount
        merchant_info = random.choice(self.merchant_data[merchant_category])
        amount = self._calculate_transaction_amount(merchant_info, customer_profile, merchant_category)
        
        try:
            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                account_id=customer_profile["account_id"],
                customer_id=customer_profile["customer_id"],
                amount=amount,
                type=transaction_type,
                merchant_name=merchant_info["name"],
                merchant_category=merchant_category,
                location=customer_profile["location"].copy(),
                timestamp=datetime.utcnow(),
                description=f"{transaction_type.value} at {merchant_info['name']}",
                balance_before=customer_profile["balance"],
                balance_after=customer_profile["balance"] - amount if transaction_type in [TransactionType.PURCHASE, TransactionType.WITHDRAWAL] else customer_profile["balance"] + amount
            )
        except Exception as e:
            logger.error(f"Error creating transaction with category {merchant_category}: {e}")
            raise
        
        # Update customer balance
        if transaction_type in [TransactionType.PURCHASE, TransactionType.WITHDRAWAL]:
            customer_profile["balance"] -= amount
        else:
            customer_profile["balance"] += amount
        
        # Add to history
        self.transaction_history.append(transaction)
        
        # Keep history manageable
        if len(self.transaction_history) > 1000:
            self.transaction_history = self.transaction_history[-500:]
        
        return transaction
    
    def _select_transaction_type(self, customer_profile: Dict) -> TransactionType:
        """Select transaction type based on customer profile"""
        # Most transactions are purchases
        weights = {
            TransactionType.PURCHASE: 0.75,
            TransactionType.WITHDRAWAL: 0.15,
            TransactionType.DEPOSIT: 0.05,
            TransactionType.TRANSFER: 0.03,
            TransactionType.PAYMENT: 0.02
        }
        
        return random.choices(
            list(weights.keys()),
            weights=list(weights.values())
        )[0]
    
    def _select_merchant_category(self, customer_profile: Dict) -> MerchantCategory:
        """Select merchant category based on customer preferences"""
        preferred = customer_profile["preferred_categories"]
        
        # 70% chance to use preferred category
        if random.random() < 0.7 and preferred:
            return random.choice(preferred)
        
        # Otherwise random category (excluding UNKNOWN)
        available_categories = [
            MerchantCategory.GROCERY,
            MerchantCategory.RESTAURANT,
            MerchantCategory.GAS_STATION,
            MerchantCategory.RETAIL,
            MerchantCategory.ENTERTAINMENT,
            MerchantCategory.HEALTHCARE,
            MerchantCategory.TRAVEL,
            MerchantCategory.ONLINE,
            MerchantCategory.ATM
        ]
        return random.choice(available_categories)
    
    def _calculate_transaction_amount(self, merchant_info: Dict, customer_profile: Dict, category: MerchantCategory) -> float:
        """Calculate transaction amount with some randomness"""
        base_amount = merchant_info["avg_amount"]
        
        # Add randomness (±50%)
        variation = random.uniform(0.5, 1.5)
        amount = base_amount * variation
        
        # Apply customer-specific factors
        spender_multiplier = {
            "conservative_saver": 0.7,
            "average_spender": 1.0,
            "high_spender": 1.8,
            "frequent_traveler": 1.3
        }.get(customer_profile["type"], 1.0)
        
        amount *= spender_multiplier
        
        # Occasional large purchases (5% chance)
        if random.random() < 0.05:
            amount *= random.uniform(3.0, 8.0)
        
        # Round to 2 decimal places
        return round(amount, 2)
    
    async def generate_suspicious_transaction(self, scenario: str = "random") -> Transaction:
        """Generate a transaction designed to trigger anomaly detection"""
        customer_profile = random.choice(self.customer_profiles)
        
        # List of anomaly scenarios with weights
        anomaly_scenarios = [
            ("large_amount", 0.25),
            ("unusual_merchant", 0.20),
            ("unusual_location", 0.15),
            ("unusual_time", 0.15),
            ("high_frequency", 0.15),
            ("round_amount", 0.10)
        ]
        
        if scenario == "random":
            # Select scenario based on weights
            scenarios, weights = zip(*anomaly_scenarios)
            scenario = random.choices(scenarios, weights=weights)[0]
        
        if scenario == "large_amount":
            # Unusually large transaction (5-50x normal)
            merchant_names = ["Luxury Car Dealership", "High-End Electronics", "Designer Boutique", "Premium Jewelry Store", "Expensive Restaurant"]
            merchant_info = {"name": random.choice(merchant_names), "avg_amount": 1000.0}
            
            # Get customer's average spending and multiply by 5-50x
            avg_spending = customer_profile["daily_budget"]
            multiplier = random.uniform(5.0, 50.0)
            amount = round(avg_spending * multiplier, 2)
            category = random.choice([MerchantCategory.RETAIL, MerchantCategory.ENTERTAINMENT, MerchantCategory.TRAVEL])
            
        elif scenario == "unusual_merchant":
            # Transaction at unusual merchant category
            unusual_merchants = [
                {"name": "Lucky Casino", "category": MerchantCategory.ENTERTAINMENT, "amount_range": (500, 5000)},
                {"name": "Crypto Exchange Pro", "category": MerchantCategory.ONLINE, "amount_range": (1000, 10000)},
                {"name": "Adult Entertainment Club", "category": MerchantCategory.ENTERTAINMENT, "amount_range": (200, 2000)},
                {"name": "Precious Metals Dealer", "category": MerchantCategory.RETAIL, "amount_range": (2000, 20000)},
                {"name": "Private Investigation Services", "category": MerchantCategory.UNKNOWN, "amount_range": (1000, 5000)}
            ]
            
            merchant = random.choice(unusual_merchants)
            merchant_info = {"name": merchant["name"], "avg_amount": sum(merchant["amount_range"]) / 2}
            amount = random.uniform(*merchant["amount_range"])
            category = merchant["category"]
            
        elif scenario == "unusual_location":
            # Transaction in foreign/distant location
            foreign_locations = [
                {"city": "Tokyo", "state": "JP", "lat": 35.6762, "lng": 139.6503},
                {"city": "London", "state": "UK", "lat": 51.5074, "lng": -0.1278},
                {"city": "Dubai", "state": "AE", "lat": 25.2048, "lng": 55.2708},
                {"city": "Moscow", "state": "RU", "lat": 55.7558, "lng": 37.6176},
                {"city": "Bangkok", "state": "TH", "lat": 13.7563, "lng": 100.5018}
            ]
            
            merchant_info = {"name": "International Duty Free", "avg_amount": 200.0}
            amount = random.uniform(150, 800)
            category = MerchantCategory.RETAIL
            
            # Update customer location
            customer_profile = customer_profile.copy()
            customer_profile["location"] = random.choice(foreign_locations)
            
        elif scenario == "unusual_time":
            # Transaction at very early or very late hours
            merchant_info = {"name": random.choice(["24/7 ATM", "Late Night Diner", "Emergency Store", "Night Club"]), "avg_amount": 100.0}
            amount = random.uniform(50, 500)
            category = random.choice([MerchantCategory.ATM, MerchantCategory.RESTAURANT, MerchantCategory.ENTERTAINMENT])
            
            # Set unusual timestamp (very early morning)
            unusual_hour = random.choice([1, 2, 3, 4, 23])
            current_time = datetime.utcnow()
            unusual_timestamp = current_time.replace(hour=unusual_hour, minute=random.randint(0, 59))
            
        elif scenario == "high_frequency":
            # Part of a rapid series of transactions (velocity spike)
            merchant_info = {"name": random.choice(["Quick Mart", "Gas Station", "Fast Food", "Corner Store"]), "avg_amount": 30.0}
            amount = random.uniform(15, 100)
            category = random.choice([MerchantCategory.GROCERY, MerchantCategory.GAS_STATION, MerchantCategory.RESTAURANT])
            
        elif scenario == "round_amount":
            # Suspiciously round amounts (often indicates money laundering)
            round_amounts = [1000, 2000, 2500, 3000, 5000, 7500, 10000]
            amount = random.choice(round_amounts)
            merchant_info = {"name": random.choice(["Wire Transfer Service", "Money Exchange", "Check Cashing"]), "avg_amount": amount}
            category = MerchantCategory.UNKNOWN
            
        else:
            # Fallback to large_amount
            return await self.generate_suspicious_transaction("large_amount")
        
        # Handle special timestamp for unusual_time scenario
        if scenario == "unusual_time" and 'unusual_timestamp' in locals():
            transaction_timestamp = unusual_timestamp
        else:
            transaction_timestamp = datetime.utcnow()
        
        # Create the suspicious transaction
        transaction = Transaction(
            id=str(uuid.uuid4()),
            account_id=customer_profile["account_id"],
            customer_id=customer_profile["customer_id"],
            amount=amount,
            type=TransactionType.PURCHASE,
            merchant_name=merchant_info["name"],
            merchant_category=category,
            location=customer_profile["location"].copy(),
            timestamp=transaction_timestamp,
            description=f"⚠️ Suspicious {scenario} transaction - {merchant_info['name']}",
            balance_before=customer_profile["balance"],
            balance_after=customer_profile["balance"] - amount,
            metadata={
                "scenario": scenario, 
                "is_anomalous": True, 
                "auto_generated": True,
                "reason": f"Automatically generated anomaly: {scenario}"
            }
        )
        
        logger.info(f"🚨 Generated {scenario} anomaly: {merchant_info['name']} - ${amount:.2f}")
        return transaction
    
    def get_customer_transaction_history(self, customer_id: str, limit: int = 100) -> List[Transaction]:
        """Get recent transactions for a specific customer"""
        customer_transactions = [
            t for t in self.transaction_history 
            if t.customer_id == customer_id
        ]
        return sorted(customer_transactions, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_anomaly_stats(self) -> Dict[str, Any]:
        """Get statistics about anomaly injection"""
        total_transactions = len(self.transaction_history)
        anomalous_transactions = sum(
            1 for t in self.transaction_history 
            if hasattr(t, 'metadata') and t.metadata and t.metadata.get('is_anomalous')
        )
        
        anomaly_rate = (anomalous_transactions / max(total_transactions, 1)) * 100
        next_anomaly_in = self.anomaly_interval - (self.transaction_counter - self.last_anomaly_transaction)
        
        return {
            "total_transactions": total_transactions,
            "anomalous_transactions": anomalous_transactions,
            "anomaly_rate_percent": round(anomaly_rate, 2),
            "next_anomaly_in": max(next_anomaly_in, 0),
            "current_interval": self.anomaly_interval,
            "transaction_counter": self.transaction_counter
        }
