"use client"

import { useEffect, useState } from "react"

type Txn = {
  id: string
  account_id: string
  customer_id: string
  amount: number
  type: string
  merchant_name: string
  merchant_category: string
  timestamp: string
  description?: string
}

type Anomaly = {
  is_anomaly: boolean
  confidence_score: number
  risk_level: "low" | "medium" | "high" | "critical"
  anomaly_types: string[]
  explanation?: string
  recommendations?: string[]
}

type StreamMessage = {
  type: "transaction"
  data: {
    transaction: Txn
    anomaly: Anomaly | null
  }
  timestamp: string
}

type NotificationPopup = {
  type: "notification_popup"
  data: {
    type: string
    message: string
    customer_id: string
    customer_name: string
    email?: string
    phone?: string
    risk_level: string
    timestamp: string
  }
}

function RiskBadge({ level }: { level: Anomaly["risk_level"] }) {
  const colors: Record<Anomaly["risk_level"], string> = {
    low: "bg-yellow-500/20 text-yellow-300 border-yellow-500/40",
    medium: "bg-orange-500/20 text-orange-300 border-orange-500/40",
    high: "bg-red-500/20 text-red-300 border-red-500/40",
    critical: "bg-red-600/30 text-red-200 border-red-600/50",
  }
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${colors[level]}`}>
      {level.toUpperCase()}
    </span>
  )
}

export default function LiveFeed() {
  const [events, setEvents] = useState<StreamMessage[]>([])
  const [status, setStatus] = useState<string>("connecting")
  const [notifications, setNotifications] = useState<NotificationPopup["data"][]>([])

  // Simulate real-time transactions
  useEffect(() => {
    const generateMockTransaction = (): StreamMessage => {
      const customers = [
        { id: "1", name: "James Martinez", account: "acc_789" },
        { id: "2", name: "Christopher Miller", account: "acc_101" },
        { id: "3", name: "Amanda Taylor", account: "acc_202" },
        { id: "4", name: "Kevin Lee", account: "acc_122" },
        { id: "5", name: "Jennifer Wright", account: "acc_140" },
        { id: "6", name: "Emily Williams", account: "acc_024" },
        { id: "7", name: "Sarah Jones", account: "acc_004" },
        { id: "8", name: "Michael Brown", account: "acc_005" }
      ]

      const merchants = [
        { name: "Amazon", category: "online_retail" },
        { name: "Starbucks", category: "food_beverage" },
        { name: "Shell Gas Station", category: "gas_stations" },
        { name: "Target", category: "department_stores" },
        { name: "McDonald's", category: "fast_food" },
        { name: "Uber", category: "transportation" },
        { name: "Netflix", category: "entertainment" },
        { name: "Grocery Store", category: "groceries" },
        { name: "Crypto Exchange", category: "cryptocurrency" },
        { name: "Online Casino", category: "gambling" },
        { name: "Luxury Jewels", category: "jewelry" }
      ]

      const customer = customers[Math.floor(Math.random() * customers.length)]
      const merchant = merchants[Math.floor(Math.random() * merchants.length)]
      
      // Determine if this should be anomalous
      const isAnomalous = Math.random() < 0.15 // 15% chance
      
      let amount: number
      let anomaly: Anomaly | null = null
      
      if (isAnomalous) {
        // Generate suspicious amounts
        amount = Math.random() < 0.5 ? 
          Math.floor(Math.random() * 5000) + 2000 : // High amount
          Math.floor(Math.random() * 100) + 5000 // Very high amount
        
        const riskLevels: Anomaly["risk_level"][] = ["medium", "high", "critical"]
        const riskLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)]
        
        anomaly = {
          is_anomaly: true,
          confidence_score: 0.7 + Math.random() * 0.3,
          risk_level: riskLevel,
          anomaly_types: [
            ...(amount > 3000 ? ["high_value_transaction"] : []),
            ...(merchant.category === "cryptocurrency" || merchant.category === "gambling" ? ["suspicious_merchant"] : []),
            ...(Math.random() < 0.3 ? ["geographic_anomaly"] : []),
            ...(Math.random() < 0.2 ? ["velocity_spike"] : [])
          ],
          explanation: `Transaction flagged due to ${amount > 3000 ? 'unusually high amount' : 'suspicious merchant category'}`,
          recommendations: ["Verify with customer", "Monitor account activity"]
        }
      } else {
        // Normal transaction amounts
        amount = Math.floor(Math.random() * 200) + 10
      }

      return {
        type: "transaction",
        data: {
          transaction: {
            id: `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            account_id: customer.account,
            customer_id: customer.id,
            amount,
            type: "purchase",
            merchant_name: merchant.name,
            merchant_category: merchant.category,
            timestamp: new Date().toISOString(),
            description: `Purchase at ${merchant.name}`
          },
          anomaly
        },
        timestamp: new Date().toISOString()
      }
    }

    // Initial connection simulation
    const connectTimer = setTimeout(() => {
      setStatus("connected")
    }, 1500)

    // Generate transactions periodically
    const transactionTimer = setInterval(() => {
      if (status === "connected") {
        const transaction = generateMockTransaction()
        setEvents(prev => [transaction, ...prev].slice(0, 100))
        
        // If anomalous, potentially show notification
        if (transaction.data.anomaly && Math.random() < 0.3) {
          const customer = transaction.data.transaction
          const notification: NotificationPopup["data"] = {
            type: Math.random() < 0.5 ? "email_notification" : "voice_call",
            message: `Fraud alert: $${transaction.data.transaction.amount} at ${transaction.data.transaction.merchant_name}`,
            customer_id: customer.customer_id,
            customer_name: `Customer ${customer.customer_id}`,
            email: `customer${customer.customer_id}@example.com`,
            phone: `+1555${customer.customer_id.padStart(3, '0')}0000`,
            risk_level: transaction.data.anomaly.risk_level,
            timestamp: new Date().toISOString()
          }
          
          setNotifications(prev => [notification, ...prev].slice(0, 5))
          
          // Auto-remove after 8 seconds
          setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.timestamp !== notification.timestamp))
          }, 8000)
        }
      }
    }, 2000 + Math.random() * 3000) // Random interval between 2-5 seconds

    return () => {
      clearTimeout(connectTimer)
      clearInterval(transactionTimer)
    }
  }, [status])

  const removeNotification = (timestamp: string) => {
    setNotifications((prev) => prev.filter(n => n.timestamp !== timestamp))
  }

  return (
    <div className="space-y-8 relative">
      {/* Notification Popups */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map((notification, index) => (
          <div
            key={notification.timestamp}
            className={`notification-popup animate-slide-in bg-white border-l-4 ${
              notification.risk_level === 'critical' ? 'border-red-500 bg-red-50' :
              notification.risk_level === 'high' ? 'border-orange-500 bg-orange-50' :
              'border-blue-500 bg-blue-50'
            } rounded-lg shadow-lg p-4 min-w-80 max-w-96`}
            style={{ 
              animationDelay: `${index * 100}ms`,
              transform: `translateY(${index * -10}px)`
            }}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  {notification.type === 'email_notification' ? (
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900">
                    {notification.message}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {notification.email && `📧 ${notification.email}`}
                    {notification.phone && `📞 ${notification.phone}`}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(notification.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => removeNotification(notification.timestamp)}
                className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-extrabold text-white mb-2">Live Transaction Feed</h2>
          <p className="text-slate-300 text-lg">
            Real-time financial activity monitoring with AI-powered insights
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-3 px-4 py-2 rounded-full ${
            status === "connected"
              ? "bg-green-500/20 border border-green-500/30"
              : status === "connecting"
                ? "bg-yellow-500/20 border border-yellow-500/30"
                : "bg-red-500/20 border border-red-500/30"
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              status === "connected" 
                ? "bg-green-400 animate-pulse" 
                : status === "connecting" 
                  ? "bg-yellow-400 animate-pulse" 
                  : "bg-red-400"
            }`}></div>
            <span className={`text-sm font-semibold ${
              status === "connected" 
                ? "text-green-300" 
                : status === "connecting" 
                  ? "text-yellow-300" 
                  : "text-red-300"
            }`}>
              {status === "connected" ? "Live" : status === "connecting" ? "Connecting" : "Offline"}
            </span>
          </div>
        </div>
      </div>

      {/* Transaction Feed */}
      <div className="space-y-4 max-h-[600px] overflow-y-auto">
        {events.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-slate-700 to-slate-600 rounded-2xl flex items-center justify-center">
              <svg className="w-10 h-10 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <p className="text-slate-300 text-xl font-semibold mb-2">Waiting for transactions...</p>
            <p className="text-slate-400 text-base">Transactions will appear here in real-time as they are processed</p>
          </div>
        ) : null}

        {events.map((e, idx) => {
          const t = e.data.transaction
          const a = e.data.anomaly
          return (
            <div
              key={t.id + idx}
              className={`p-6 rounded-xl border transition-all duration-300 ${
                a 
                  ? "bg-red-900/20 border-red-600/40 shadow-lg" 
                  : "bg-slate-700/50 border-slate-600/50 hover:bg-slate-700/70"
              }`}
            >
              {/* Transaction Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                      {t.merchant_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="text-lg font-semibold text-white">{t.merchant_name}</div>
                      <div className="text-sm text-slate-400">
                        Customer {t.customer_id} • {t.merchant_category.replace("_", " ")}
                      </div>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">
                    ${Math.abs(t.amount).toFixed(2)}
                  </div>
                  <div className="text-sm text-slate-400">{new Date(t.timestamp).toLocaleTimeString()}</div>
                </div>
              </div>

              {/* Anomaly Detection */}
              {a && (
                <div className="border-t border-red-600/30 pt-4 mt-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <RiskBadge level={a.risk_level} />
                      <span className="text-sm font-bold text-red-300">Anomaly Detected</span>
                    </div>
                    <span className="text-sm font-bold text-red-200 bg-red-900/50 px-3 py-1 rounded-full border border-red-600/50">
                      {Math.round(a.confidence_score * 100)}% confidence
                    </span>
                  </div>

                  {a.explanation && (
                    <div className="mb-3">
                      <span className="text-sm font-semibold text-red-200">Analysis:</span>
                      <p className="text-sm text-slate-300 mt-1">{a.explanation}</p>
                    </div>
                  )}

                  {a.recommendations && a.recommendations.length > 0 && (
                    <div>
                      <span className="text-sm font-semibold text-red-200">Recommended Actions:</span>
                      <ul className="list-disc list-inside mt-2 space-y-1">
                        {a.recommendations.slice(0, 3).map((r, i) => (
                          <li key={i} className="text-sm text-slate-300">
                            {r}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Normal Transaction Indicator */}
              {!a && (
                <div className="flex items-center justify-center py-3 border-t border-green-600/30 mt-4">
                  <div className="flex items-center space-x-2 text-green-400">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span className="text-sm font-semibold">Normal Transaction</span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Footer Stats */}
      {events.length > 0 && (
        <div className="flex items-center justify-between text-sm text-slate-400 pt-6 border-t border-slate-600/50">
          <span className="font-medium">Showing {events.length} recent transactions</span>
          <span className="font-medium">Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      )}
    </div>
  )
}
