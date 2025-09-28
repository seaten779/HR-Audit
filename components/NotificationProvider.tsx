'use client'

import React from 'react'
import NotificationToast from './NotificationToast'
import { useNotifications } from '@/hooks/useNotifications'

interface NotificationProviderProps {
  children: React.ReactNode
}

const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const {
    notifications,
    dismissNotification,
    dismissAllNotifications
  } = useNotifications()

  return (
    <>
      {children}
      <NotificationToast
        notifications={notifications}
        onDismiss={dismissNotification}
        onDismissAll={dismissAllNotifications}
      />
    </>
  )
}

export default NotificationProvider