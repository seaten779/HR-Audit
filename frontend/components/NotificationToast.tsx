'use client'

import React, { useState, useEffect } from 'react'
import { X, AlertCircle, CheckCircle, Mail, Phone, AlertTriangle } from 'lucide-react'

interface NotificationData {
  id: string
  type: 'email' | 'phone' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  duration?: number // milliseconds, 0 for persistent
}

interface NotificationToastProps {
  notifications: NotificationData[]
  onDismiss: (id: string) => void
  onDismissAll?: () => void
}

const NotificationToast: React.FC<NotificationToastProps> = ({
  notifications,
  onDismiss,
  onDismissAll
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState<NotificationData[]>([])

  useEffect(() => {
    setVisibleNotifications(notifications)
  }, [notifications])

  const getIcon = (type: NotificationData['type']) => {
    switch (type) {
      case 'email':
        return <Mail className="w-5 h-5" />
      case 'phone':
        return <Phone className="w-5 h-5" />
      case 'success':
        return <CheckCircle className="w-5 h-5" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />
      case 'error':
        return <AlertCircle className="w-5 h-5" />
      default:
        return <AlertCircle className="w-5 h-5" />
    }
  }

  const getStyles = (type: NotificationData['type']) => {
    switch (type) {
      case 'email':
        return {
          bg: 'bg-blue-900/95 border-blue-600/50',
          text: 'text-blue-100',
          icon: 'text-blue-400',
          accent: 'bg-blue-500'
        }
      case 'phone':
        return {
          bg: 'bg-green-900/95 border-green-600/50',
          text: 'text-green-100',
          icon: 'text-green-400',
          accent: 'bg-green-500'
        }
      case 'success':
        return {
          bg: 'bg-emerald-900/95 border-emerald-600/50',
          text: 'text-emerald-100',
          icon: 'text-emerald-400',
          accent: 'bg-emerald-500'
        }
      case 'warning':
        return {
          bg: 'bg-yellow-900/95 border-yellow-600/50',
          text: 'text-yellow-100',
          icon: 'text-yellow-400',
          accent: 'bg-yellow-500'
        }
      case 'error':
        return {
          bg: 'bg-red-900/95 border-red-600/50',
          text: 'text-red-100',
          icon: 'text-red-400',
          accent: 'bg-red-500'
        }
      default:
        return {
          bg: 'bg-slate-900/95 border-slate-600/50',
          text: 'text-slate-100',
          icon: 'text-slate-400',
          accent: 'bg-slate-500'
        }
    }
  }

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  if (visibleNotifications.length === 0) {
    return null
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-3 max-w-sm w-full">
      {/* Dismiss All Button */}
      {visibleNotifications.length > 1 && onDismissAll && (
        <div className="flex justify-end">
          <button
            onClick={onDismissAll}
            className="text-xs text-slate-400 hover:text-white bg-slate-800/90 hover:bg-slate-700/90 px-3 py-1 rounded-full border border-slate-600/50 transition-all duration-200"
          >
            Clear All ({visibleNotifications.length})
          </button>
        </div>
      )}

      {/* Notification Stack */}
      <div className="space-y-3">
        {visibleNotifications.slice(-5).map((notification, index) => {
          const styles = getStyles(notification.type)
          const isOldest = index === 0 && visibleNotifications.length > 5
          
          return (
            <div
              key={notification.id}
              className={`
                ${styles.bg} ${styles.text}
                backdrop-blur-sm border rounded-lg shadow-2xl
                transform transition-all duration-300 ease-out
                hover:scale-[1.02] hover:shadow-3xl
                animate-slide-in-right
                ${isOldest ? 'opacity-75 scale-95' : ''}
              `}
              style={{
                animationDelay: `${index * 100}ms`
              }}
            >
              {/* Accent Bar */}
              <div className={`h-1 ${styles.accent} rounded-t-lg`} />
              
              <div className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    {/* Icon */}
                    <div className={`${styles.icon} mt-0.5 flex-shrink-0`}>
                      {getIcon(notification.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className="font-semibold text-sm leading-tight">
                          {notification.title}
                        </h4>
                        <span className="text-xs opacity-75 flex-shrink-0">
                          {formatTime(notification.timestamp)}
                        </span>
                      </div>
                      
                      <p className="text-sm opacity-90 leading-relaxed break-words">
                        {notification.message}
                      </p>
                    </div>
                  </div>

                  {/* Close Button */}
                  <button
                    onClick={() => onDismiss(notification.id)}
                    className="text-white/60 hover:text-white/90 hover:bg-white/10 p-1 rounded transition-all duration-200 flex-shrink-0 ml-2"
                    aria-label="Dismiss notification"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Overflow Indicator */}
      {visibleNotifications.length > 5 && (
        <div className="text-center">
          <span className="text-xs text-slate-400 bg-slate-800/90 px-3 py-1 rounded-full border border-slate-600/50">
            +{visibleNotifications.length - 5} more notifications
          </span>
        </div>
      )}

      <style jsx>{`
        @keyframes slide-in-right {
          from {
            opacity: 0;
            transform: translateX(100%);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .animate-slide-in-right {
          animation: slide-in-right 0.3s ease-out forwards;
        }
      `}</style>
    </div>
  )
}

export default NotificationToast