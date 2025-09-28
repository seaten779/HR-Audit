'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Phone, CheckCircle, XCircle, Clock, Search, Filter, RefreshCw, Download, Volume2, PhoneCall } from 'lucide-react'

interface CallRecord {
  id: string
  customer_id: string
  phone_number: string
  status: 'completed' | 'failed' | 'pending'
  call_duration?: number
  initiated_at: string | null
  completed_at?: string | null
  error_message?: string
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  transaction_id: string
  script_used: string
}

export default function CallManagementPage() {
  const [callRecords, setCallRecords] = useState<CallRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [riskFilter, setRiskFilter] = useState<string>('all')

  useEffect(() => {
    fetchCallRecords()
  }, [])

  const fetchCallRecords = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/notifications/history?limit=100')
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          const phoneNotifications = result.data.notifications
            .filter((n: any) => n.notification_type === 'phone')
            .map((n: any) => ({
              id: n.id,
              customer_id: n.customer_id,
              phone_number: n.recipient,
              status: n.status === 'sent' ? 'completed' : n.status,
              call_duration: Math.floor(Math.random() * 120) + 30, // Mock duration
              initiated_at: n.sent_at,
              completed_at: n.sent_at,
              error_message: n.error_message,
              risk_level: n.risk_level,
              transaction_id: n.transaction_id,
              script_used: 'Security Alert Script'
            }))
          setCallRecords(phoneNotifications)
        }
      }
    } catch (error) {
      console.error('Failed to fetch call records:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredRecords = callRecords.filter(record => {
    const matchesSearch = record.phone_number.includes(searchTerm) ||
                         record.customer_id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || record.status === statusFilter
    const matchesRisk = riskFilter === 'all' || record.risk_level === riskFilter
    return matchesSearch && matchesStatus && matchesRisk
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />
      case 'pending': return <Clock className="w-4 h-4 text-yellow-400" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getRiskBadge = (risk: string) => {
    const colors = {
      low: 'bg-green-500/20 text-green-400 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      critical: 'bg-red-500/20 text-red-400 border-red-500/30'
    }
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full border ${colors[risk as keyof typeof colors] || colors.medium}`}>
        {risk.toUpperCase()}
      </span>
    )
  }

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A'
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const exportCallData = () => {
    try {
      const headers = ['Timestamp', 'Customer ID', 'Phone Number', 'Status', 'Duration', 'Risk Level', 'Transaction ID']
      
      const csvRows = [
        headers.join(','),
        ...filteredRecords.map(record => [
          record.initiated_at ? `"${new Date(record.initiated_at).toLocaleString()}"` : 'N/A',
          `"${record.customer_id}"`,
          `"${record.phone_number}"`,
          `"${record.status}"`,
          `"${formatDuration(record.call_duration)}"`,
          `"${record.risk_level}"`,
          `"${record.transaction_id}"`
        ].join(','))
      ]
      
      const csvContent = csvRows.join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `call_records_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
      
      console.log(`CSV exported successfully: ${filteredRecords.length} records`)
    } catch (error) {
      console.error('Error exporting CSV:', error)
      alert('Failed to export CSV. Please try again.')
    }
  }

  const totalDuration = callRecords.reduce((sum, record) => sum + (record.call_duration || 0), 0)
  const avgDuration = callRecords.length > 0 ? Math.round(totalDuration / callRecords.length) : 0

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-12">
          <div className="flex items-center gap-4">
            <Link href="/admin" className="p-2 hover:bg-slate-800 rounded-lg transition-colors">
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">
                Call Management
              </h1>
              <p className="text-slate-300 mt-2">Monitor phone notifications, call logs, and voice settings</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchCallRecords}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={exportCallData}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Total Calls</p>
                <p className="text-2xl font-bold text-green-400">{callRecords.length}</p>
              </div>
              <PhoneCall className="w-8 h-8 text-green-400" />
            </div>
          </div>
          
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Successful Calls</p>
                <p className="text-2xl font-bold text-emerald-400">
                  {callRecords.filter(r => r.status === 'completed').length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-emerald-400" />
            </div>
          </div>
          
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Average Duration</p>
                <p className="text-2xl font-bold text-blue-400">{formatDuration(avgDuration)}</p>
              </div>
              <Clock className="w-8 h-8 text-blue-400" />
            </div>
          </div>
          
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Success Rate</p>
                <p className="text-2xl font-bold text-purple-400">
                  {callRecords.length > 0 
                    ? Math.round((callRecords.filter(r => r.status === 'completed').length / callRecords.length) * 100)
                    : 0}%
                </p>
              </div>
              <Volume2 className="w-8 h-8 text-purple-400" />
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 mb-8">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search calls..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-400"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="pending">Pending</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-green-400"
              >
                <option value="all">All Risk Levels</option>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
                <option value="critical">Critical Risk</option>
              </select>
            </div>
          </div>
        </div>

        {/* Call Records Table */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-slate-700">
            <h2 className="text-xl font-semibold text-white">Call Records ({filteredRecords.length})</h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-green-400" />
              <p className="text-slate-300">Loading call records...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Timestamp</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Customer</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Phone Number</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Duration</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Risk Level</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Status</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-700/50">
                      <td className="px-6 py-4 text-sm text-slate-200">
                        {record.initiated_at ? new Date(record.initiated_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-200">{record.customer_id}</td>
                      <td className="px-6 py-4 text-sm text-slate-200 font-mono">{record.phone_number}</td>
                      <td className="px-6 py-4 text-sm text-slate-200">{formatDuration(record.call_duration)}</td>
                      <td className="px-6 py-4 text-sm">{getRiskBadge(record.risk_level)}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(record.status)}
                          <span className="text-sm text-slate-200 capitalize">{record.status}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <button className="text-green-400 hover:text-green-300 text-sm">Play Recording</button>
                      </td>
                    </tr>
                  ))}
                  {filteredRecords.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-slate-400">
                        No call records found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Voice Settings */}
        <div className="mt-12 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Voice Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Voice Engine</label>
                <select className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white">
                  <option>System TTS (Fallback)</option>
                  <option>Azure Speech Services</option>
                  <option>Google Cloud TTS</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Voice Type</label>
                <select className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white">
                  <option>Professional Female</option>
                  <option>Professional Male</option>
                  <option>Neutral</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Speaking Rate</label>
                <input 
                  type="range" 
                  min="0.5" 
                  max="2" 
                  step="0.1" 
                  defaultValue="1.0"
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-slate-400 mt-1">
                  <span>Slow</span>
                  <span>Normal</span>
                  <span>Fast</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-6">Call Scripts</h2>
            <div className="space-y-4">
              <div className="p-4 bg-slate-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white">Security Alert Script</h3>
                  <span className="text-xs text-green-400">Active</span>
                </div>
                <p className="text-sm text-slate-300">Standard script for anomaly notifications</p>
              </div>
              
              <div className="p-4 bg-slate-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white">High Risk Alert</h3>
                  <span className="text-xs text-slate-400">Inactive</span>
                </div>
                <p className="text-sm text-slate-300">Enhanced script for critical risk transactions</p>
              </div>
              
              <div className="p-4 bg-slate-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-white">Verification Request</h3>
                  <span className="text-xs text-slate-400">Inactive</span>
                </div>
                <p className="text-sm text-slate-300">Customer verification for suspicious activity</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}