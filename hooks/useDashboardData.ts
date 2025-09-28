'use client'

import { useState, useEffect, useCallback } from 'react'

export interface DashboardStats {
  total_transactions: number
  anomalies_detected: number
  active_alerts: number
  average_confidence: number
  anomaly_rate: number
  next_anomaly_in: number
  notifications_sent: {
    email: number
    phone: number
    total: number
  }
  transaction_volume: Array<{
    hour: string
    transactions: number
    anomalies: number
  }>
  anomaly_breakdown: {
    unusual_amount: number
    unusual_location: number
    unusual_time: number
    velocity_spike: number
    unusual_merchant: number
  }
  risk_levels: {
    low: number
    medium: number
    high: number
    critical: number
  }
  recent_trends: {
    last_hour: {
      transactions: number
      anomalies: number
      notifications_sent: number
    }
    last_day: {
      transactions: number
      anomalies: number
      notifications_sent: number
    }
  }
  system_performance: {
    detection_accuracy: number
    false_positive_rate: number
    response_time_ms: number
  }
  timestamp: string
}

export interface NotificationStats {
  total_notifications: number
  notification_types: {
    email: number
    phone: number
  }
  status_breakdown: {
    successful: number
    failed: number
    success_rate: number
  }
  risk_breakdown: {
    critical: number
    high: number
    medium: number
    low: number
  }
  recent_activity: {
    last_24h: number
    emails_24h: number
    calls_24h: number
  }
  top_customers: Array<{
    customer_id: string
    notification_count: number
  }>
  timestamp: string
}

export const useDashboardData = () => {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null)
  const [notificationStats, setNotificationStats] = useState<NotificationStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardStats = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboard/stats')
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard stats')
      }
      const result = await response.json()
      if (result.success) {
        setDashboardStats(result.data)
      } else {
        throw new Error(result.message || 'Failed to fetch dashboard stats')
      }
    } catch (err) {
      console.error('Error fetching dashboard stats:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }, [])

  const fetchNotificationStats = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/notifications/dashboard-stats')
      if (!response.ok) {
        throw new Error('Failed to fetch notification stats')
      }
      const result = await response.json()
      if (result.success) {
        setNotificationStats(result.data)
      } else {
        throw new Error(result.message || 'Failed to fetch notification stats')
      }
    } catch (err) {
      console.error('Error fetching notification stats:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }, [])

  const fetchAllData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      await Promise.all([
        fetchDashboardStats(),
        fetchNotificationStats()
      ])
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [fetchDashboardStats, fetchNotificationStats])

  // Initial load
  useEffect(() => {
    fetchAllData()
  }, [fetchAllData])

  // Auto-refresh every 10 seconds
  useEffect(() => {
    const interval = setInterval(fetchAllData, 10000)
    return () => clearInterval(interval)
  }, [fetchAllData])

  // Calculate derived metrics
  const derivedMetrics = {
    anomalyRatePercent: dashboardStats ? (dashboardStats.anomaly_rate * 100).toFixed(2) : '0.00',
    confidencePercent: dashboardStats ? (dashboardStats.average_confidence * 100).toFixed(1) : '0.0',
    totalVolume: dashboardStats?.transaction_volume.reduce((sum, item) => sum + item.transactions, 0) || 0,
    totalVolumeAnomalies: dashboardStats?.transaction_volume.reduce((sum, item) => sum + item.anomalies, 0) || 0,
    notificationSuccessRate: notificationStats ? (notificationStats.status_breakdown.success_rate * 100).toFixed(1) : '0.0'
  }

  return {
    dashboardStats,
    notificationStats,
    loading,
    error,
    derivedMetrics,
    refresh: fetchAllData
  }
}