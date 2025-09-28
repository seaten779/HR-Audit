'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeft, Mail, Send, CheckCircle, XCircle, Clock, Search, Filter, RefreshCw, Download, Settings } from 'lucide-react'

interface EmailRecord {
  id: string
  customer_id: string
  recipient: string
  subject: string
  content: string
  status: 'sent' | 'failed' | 'pending'
  sent_at: string | null
  error_message?: string
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  transaction_id: string
}

export default function EmailManagementPage() {
  const [emailRecords, setEmailRecords] = useState<EmailRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [riskFilter, setRiskFilter] = useState<string>('all')

  useEffect(() => {
    fetchEmailRecords()
  }, [])

  const fetchEmailRecords = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/v1/notifications/history?limit=100')
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          const emailNotifications = result.data.notifications
            .filter((n: any) => n.notification_type === 'email')
            .map((n: any) => ({
              id: n.id,
              customer_id: n.customer_id,
              recipient: n.recipient,
              subject: `Security Alert for ${n.customer_id}`,
              content: n.content,
              status: n.status,
              sent_at: n.sent_at,
              error_message: n.error_message,
              risk_level: n.risk_level,
              transaction_id: n.transaction_id
            }))
          setEmailRecords(emailNotifications)
        }
      }
    } catch (error) {
      console.error('Failed to fetch email records:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredRecords = emailRecords.filter(record => {
    const matchesSearch = record.recipient.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         record.customer_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         record.subject.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || record.status === statusFilter
    const matchesRisk = riskFilter === 'all' || record.risk_level === riskFilter
    return matchesSearch && matchesStatus && matchesRisk
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent': return <CheckCircle className="w-4 h-4 text-green-400" />
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

  const exportEmailData = () => {
    try {
      const headers = ['Timestamp', 'Customer ID', 'Recipient', 'Subject', 'Status', 'Risk Level', 'Transaction ID']
      
      const csvRows = [
        headers.join(','),
        ...filteredRecords.map(record => [
          record.sent_at ? `"${new Date(record.sent_at).toLocaleString()}"` : 'N/A',
          `"${record.customer_id}"`,
          `"${record.recipient}"`,
          `"${record.subject.replace(/"/g, '""')}"`,
          `"${record.status}"`,
          `"${record.risk_level}"`,
          `"${record.transaction_id}"`
        ].join(','))
      ]
      
      const csvContent = csvRows.join('\n')
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `email_records_${new Date().toISOString().split('T')[0]}.csv`
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
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">
                Email Management
              </h1>
              <p className="text-slate-300 mt-2">Track sent emails, manage SMTP settings, and monitor delivery rates</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={fetchEmailRecords}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={exportEmailData}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
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
                <p className="text-slate-300 text-sm">Total Emails</p>
                <p className="text-2xl font-bold text-blue-400">{emailRecords.length}</p>
              </div>
              <Mail className="w-8 h-8 text-blue-400" />
            </div>
          </div>
          
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Successfully Sent</p>
                <p className="text-2xl font-bold text-green-400">
                  {emailRecords.filter(r => r.status === 'sent').length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
          </div>
          
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Failed</p>
                <p className="text-2xl font-bold text-red-400">
                  {emailRecords.filter(r => r.status === 'failed').length}
                </p>
              </div>
              <XCircle className="w-8 h-8 text-red-400" />
            </div>
          </div>
          
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-300 text-sm">Delivery Rate</p>
                <p className="text-2xl font-bold text-purple-400">
                  {emailRecords.length > 0 
                    ? Math.round((emailRecords.filter(r => r.status === 'sent').length / emailRecords.length) * 100)
                    : 0}%
                </p>
              </div>
              <Send className="w-8 h-8 text-purple-400" />
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
                placeholder="Search emails..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
              >
                <option value="all">All Status</option>
                <option value="sent">Sent</option>
                <option value="failed">Failed</option>
                <option value="pending">Pending</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <select
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-400"
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

        {/* Email Records Table */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
          <div className="p-6 border-b border-slate-700">
            <h2 className="text-xl font-semibold text-white">Email Records ({filteredRecords.length})</h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center">
              <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-400" />
              <p className="text-slate-300">Loading email records...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Timestamp</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Customer</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Recipient</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Subject</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Risk Level</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Status</th>
                    <th className="px-6 py-4 text-left text-xs font-medium text-slate-300 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {filteredRecords.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-700/50">
                      <td className="px-6 py-4 text-sm text-slate-200">
                        {record.sent_at ? new Date(record.sent_at).toLocaleString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-200">{record.customer_id}</td>
                      <td className="px-6 py-4 text-sm text-slate-200">{record.recipient}</td>
                      <td className="px-6 py-4 text-sm text-slate-200 max-w-xs truncate">{record.subject}</td>
                      <td className="px-6 py-4 text-sm">{getRiskBadge(record.risk_level)}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(record.status)}
                          <span className="text-sm text-slate-200 capitalize">{record.status}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <button className="text-blue-400 hover:text-blue-300 text-sm">View Details</button>
                      </td>
                    </tr>
                  ))}
                  {filteredRecords.length === 0 && (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-slate-400">
                        No email records found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* SMTP Settings */}
        <div className="mt-12 bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-white">SMTP Configuration</h2>
            <button className="flex items-center gap-2 px-4 py-2 bg-slate-600 hover:bg-slate-500 rounded-lg transition-colors">
              <Settings className="w-4 h-4" />
              Configure
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">SMTP Server</label>
              <input
                type="text"
                value="smtp.gmail.com"
                readOnly
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Port</label>
              <input
                type="text"
                value="587"
                readOnly
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
              <input
                type="text"
                value="smptpchecking@gmail.com"
                readOnly
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Status</label>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-green-400 text-sm">Connected</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}