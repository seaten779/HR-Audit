'use client'

import { useState, useCallback } from 'react'

export interface NotificationData {
  id: string
  type: 'email' | 'phone' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  duration?: number // milliseconds, 0 for persistent
  autoRemove?: boolean
}

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<NotificationData[]>([])

  const addNotification = useCallback((notification: Omit<NotificationData, 'id' | 'timestamp'>) => {
    const newNotification: NotificationData = {
      ...notification,
      id: `notification_${Date.now()}_${Math.random().toString(36).substring(7)}`,
      timestamp: new Date(),
      autoRemove: notification.autoRemove ?? true
    }

    setNotifications(prev => [...prev, newNotification])

    // Auto-remove after duration (default 10 seconds for non-persistent)
    if (newNotification.autoRemove && (newNotification.duration ?? 10000) > 0) {
      setTimeout(() => {
        dismissNotification(newNotification.id)
      }, newNotification.duration ?? 10000)
    }

    return newNotification.id
  }, [])

  const dismissNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id))
  }, [])

  const dismissAllNotifications = useCallback(() => {
    setNotifications([])
  }, [])

  const addEmailNotification = useCallback((customerName: string, email: string) => {
    return addNotification({
      type: 'email',
      title: 'Security Alert Email Sent',
      message: `Anomaly notification sent to ${customerName}`,
      duration: 8000
    })
  }, [addNotification])

  const addPhoneNotification = useCallback((customerName: string, phone: string) => {
    return addNotification({
      type: 'phone',
      title: 'Security Call Initiated',
      message: `Automated call placed to ${customerName}`,
      duration: 8000
    })
  }, [addNotification])

  const addSuccessNotification = useCallback((message: string) => {
    return addNotification({
      type: 'success',
      title: 'Success',
      message,
      duration: 5000
    })
  }, [addNotification])

  const addWarningNotification = useCallback((message: string) => {
    return addNotification({
      type: 'warning',
      title: 'Warning',
      message,
      duration: 8000
    })
  }, [addNotification])

  const addErrorNotification = useCallback((message: string) => {
    return addNotification({
      type: 'error',
      title: 'Error',
      message,
      duration: 10000
    })
  }, [addNotification])

  // Note: Real-time notifications would be handled via WebSocket or Server-Sent Events
  // For now, notifications are triggered manually via the notification methods

  return {
    notifications,
    addNotification,
    addEmailNotification,
    addPhoneNotification,
    addSuccessNotification,
    addWarningNotification,
    addErrorNotification,
    dismissNotification,
    dismissAllNotifications
  }
}