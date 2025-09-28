'use client';

import React, { useState, useEffect } from 'react';
import { RefreshCw, AlertTriangle, BarChart3, TrendingUp } from 'lucide-react';

export default function SimpleDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/dashboard/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data.data);
      } else {
        setError('Failed to fetch dashboard stats');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-cyan-400" />
          <p className="text-lg text-slate-300">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center bg-slate-800 p-8 rounded-lg">
          <AlertTriangle className="w-8 h-8 mx-auto mb-4 text-red-400" />
          <p className="text-lg text-red-400 mb-4">Error: {error}</p>
          <button 
            onClick={fetchStats}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            <RefreshCw className="w-4 h-4 inline mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">
            FinancePulse Dashboard
          </h1>
          <p className="text-slate-400">
            Real-time financial monitoring and anomaly detection
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800 p-6 rounded-lg">
            <div className="flex items-center">
              <BarChart3 className="w-8 h-8 text-blue-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Total Transactions</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.total_transactions?.toLocaleString() || '0'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-red-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Anomalies Detected</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.anomalies_detected || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-green-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Active Alerts</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.active_alerts || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <div className="flex items-center">
              <RefreshCw className="w-8 h-8 text-cyan-400 mr-3" />
              <div>
                <p className="text-slate-400 text-sm">Confidence</p>
                <p className="text-2xl font-bold text-white">
                  {stats?.average_confidence ? 
                    `${(stats.average_confidence * 100).toFixed(1)}%` : 
                    '0%'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-slate-800 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a 
              href="/cedar-dashboard"
              className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              🤖 AI Command Center
            </a>
            <a 
              href="/cedar-demo"
              className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              🚀 Cedar-OS Demo
            </a>
            <a 
              href="/live-feed"
              className="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg text-center transition-colors"
            >
              📡 Live Feed
            </a>
          </div>
        </div>

        {/* Recent Activity */}
        {stats?.transaction_volume && (
          <div className="bg-slate-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
            <div className="space-y-4">
              {stats.transaction_volume.slice(0, 5).map((item: any, index: number) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-slate-300">{item.hour}</span>
                  <span className="text-blue-400">{item.transactions} transactions</span>
                  <span className="text-red-400">{item.anomalies} anomalies</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}