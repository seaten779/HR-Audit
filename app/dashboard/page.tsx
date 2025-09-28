"use client";

import React, { useState } from "react";
import { useDashboardData } from "@/hooks/useDashboardData";
import { RefreshCw, Download, TrendingUp, TrendingDown, BarChart3, AlertTriangle, PieChart, CheckCircle } from "lucide-react";
import { 
  Container, 
  PageHeader, 
  PageContent, 
  Grid, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent,
  MetricCard,
  Button, 
  Select,
  Flex,
  Divider
} from "@/components/ui";

type TimeRange = "1h" | "24h" | "7d" | "30d";
type ViewType = "transactions" | "anomalies";

interface ChartPoint {
  x: number;
  y: number;
  value: number;
  label: string;
}

export default function DashboardPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>("24h");
  const [selectedView, setSelectedView] = useState<ViewType>("transactions");
  
  const { dashboardStats, notificationStats, loading, error, derivedMetrics, refresh } = useDashboardData();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Card className="text-center p-8">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-cyan-400" />
          <p className="text-lg text-slate-300">Loading dashboard data...</p>
        </Card>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <Card className="text-center p-8 max-w-md">
          <AlertTriangle className="w-8 h-8 mx-auto mb-4 text-red-400" />
          <p className="text-lg text-red-400 mb-4">Error loading dashboard: {error}</p>
          <Button onClick={refresh} variant="primary">
            <RefreshCw className="w-4 h-4" />
            Retry
          </Button>
        </Card>
      </div>
    );
  }
  
  // Generate chart points from real data
  const generateChartPoints = (): ChartPoint[] => {
    if (!dashboardStats?.transaction_volume) return [];
    
    const maxValue = Math.max(...dashboardStats.transaction_volume.map(d => 
      selectedView === 'transactions' ? d.transactions : d.anomalies
    ));
    
    return dashboardStats.transaction_volume.map((data, index) => {
      const value = selectedView === 'transactions' ? data.transactions : data.anomalies;
      const x = 50 + (index * 35); // Spread points evenly
      const y = 200 - (value / maxValue) * 140; // Scale to chart height
      return {
        x,
        y: Math.max(50, y), // Ensure points don't go above chart
        value,
        label: data.hour
      };
    });
  };
  
  const chartPoints = generateChartPoints();

  return (
    <div className="min-h-screen bg-slate-900">
      <Container>
        <PageHeader 
          title="Dashboard Analytics"
          description="Real-time insights and trends in your financial data with AI-powered anomaly detection"
          action={
            <Flex gap="sm">
              <Button 
                variant="outline" 
                onClick={refresh}
                leftIcon={<RefreshCw className="w-4 h-4" />}
              >
                Refresh
              </Button>
              <Button 
                variant="success"
                leftIcon={<Download className="w-4 h-4" />}
              >
                Export PDF
              </Button>
            </Flex>
          }
        />

        <PageContent>
          {/* Controls */}
          <Card variant="glass">
            <CardContent className="p-6">
              <Flex justify="between" align="center" wrap className="gap-6">
                <Flex align="center" gap="lg" wrap>
                  <Select
                    label="Time Range"
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value as TimeRange)}
                  >
                    <option value="1h">Last Hour</option>
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="30d">Last 30 Days</option>
                  </Select>
                  
                  <Select
                    label="View Type"
                    value={selectedView}
                    onChange={(e) => setSelectedView(e.target.value as ViewType)}
                  >
                    <option value="transactions">Transactions</option>
                    <option value="anomalies">Anomalies</option>
                  </Select>
                </Flex>
              </Flex>
            </CardContent>
          </Card>

          {/* Summary Stats */}
          <Grid cols={4} gap="lg">
            <MetricCard
              title="Total Transactions"
              value={dashboardStats?.total_transactions?.toLocaleString() || '0'}
              description="total processed"
              color="blue"
              icon={<BarChart3 className="w-8 h-8" />}
              trend={dashboardStats?.recent_trends?.last_hour?.transactions ? {
                direction: dashboardStats.recent_trends.last_hour.transactions > 0 ? 'up' : 'down',
                value: Math.abs(dashboardStats.recent_trends.last_hour.transactions).toString(),
                label: dashboardStats?.next_anomaly_in ? `Next anomaly in ~${dashboardStats.next_anomaly_in} transactions` : undefined
              } : undefined}
            />
            
            <MetricCard
              title="Total Anomalies"
              value={dashboardStats?.anomalies_detected || 0}
              description="flagged transactions"
              color="red"
              icon={<AlertTriangle className="w-8 h-8" />}
              trend={{
                direction: 'neutral' as const,
                value: dashboardStats?.active_alerts?.toString() || '0',
                label: dashboardStats?.active_alerts ? `${dashboardStats.active_alerts} active alerts` : undefined
              }}
            />
            
            <MetricCard
              title="Anomaly Rate"
              value={`${derivedMetrics.anomalyRatePercent}%`}
              description="of all transactions"
              color="yellow"
              icon={<PieChart className="w-8 h-8" />}
              trend={{
                direction: 'neutral' as const,
                value: `${dashboardStats?.system_performance?.detection_accuracy ? 
                  (dashboardStats.system_performance.detection_accuracy * 100).toFixed(1) : '94.0'}%`,
                label: 'detection accuracy'
              }}
            />
            
            <MetricCard
              title="System Performance"
              value={`${derivedMetrics.confidencePercent}%`}
              description="avg confidence"
              color="green"
              icon={<CheckCircle className="w-8 h-8" />}
              trend={{
                direction: 'up' as const,
                value: `${dashboardStats?.system_performance?.response_time_ms || 45}ms`,
                label: 'response time'
              }}
            />
          </Grid>

          {/* Charts */}
          <Grid cols={2} gap="lg">
            {/* Transaction Volume Chart */}
            <Card variant="gradient" size="lg">
              <CardHeader>
                <CardTitle>Transaction Volume Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 w-full">
                  <svg className="w-full h-full" viewBox="0 0 500 250">
                    {/* Grid lines */}
                    {Array.from({ length: 5 }, (_, i) => (
                      <line
                        key={i}
                        x1="50"
                        y1={50 + i * 40}
                        x2="450"
                        y2={50 + i * 40}
                        stroke="#475569"
                        strokeWidth="1"
                        opacity="0.3"
                      />
                    ))}
                    
                    {/* Chart line */}
                    <polyline
                      points={chartPoints.map(p => `${p.x},${p.y}`).join(' ')}
                      fill="none"
                      stroke="url(#gradient)"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                    
                    {/* Gradient definition */}
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#06b6d4" />
                      </linearGradient>
                    </defs>
                    
                    {/* Data points */}
                    {chartPoints.map((point, i) => (
                      <circle
                        key={i}
                        cx={point.x}
                        cy={point.y}
                        r="4"
                        fill="#3b82f6"
                        className="drop-shadow-sm"
                      />
                    ))}
                    
                    {/* X-axis labels */}
                    <text x={80} y={235} textAnchor="middle" fontSize="11" fill="#94a3b8">10:57 AM</text>
                    <text x={140} y={235} textAnchor="middle" fontSize="11" fill="#94a3b8">02:57 PM</text>
                    <text x={200} y={235} textAnchor="middle" fontSize="11" fill="#94a3b8">06:57 PM</text>
                    <text x={260} y={235} textAnchor="middle" fontSize="11" fill="#94a3b8">10:57 PM</text>
                    <text x={320} y={235} textAnchor="middle" fontSize="11" fill="#94a3b8">02:57 AM</text>
                    <text x={380} y={235} textAnchor="middle" fontSize="11" fill="#94a3b8">06:57 AM</text>
                  </svg>
                </div>
              </CardContent>
            </Card>

            {/* Anomaly Types Breakdown */}
            <Card variant="gradient" size="lg">
              <CardHeader>
                <CardTitle>Anomaly Types Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dashboardStats?.anomaly_breakdown && Object.entries(dashboardStats.anomaly_breakdown).map(([type, count], index) => {
                    const colors = [
                      { bg: 'bg-red-500/10', border: 'border-red-500/20', dot: 'bg-red-500', text: 'text-red-400' },
                      { bg: 'bg-orange-500/10', border: 'border-orange-500/20', dot: 'bg-orange-500', text: 'text-orange-400' },
                      { bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', dot: 'bg-yellow-500', text: 'text-yellow-400' },
                      { bg: 'bg-purple-500/10', border: 'border-purple-500/20', dot: 'bg-purple-500', text: 'text-purple-400' },
                      { bg: 'bg-blue-500/10', border: 'border-blue-500/20', dot: 'bg-blue-500', text: 'text-blue-400' }
                    ];
                    const colorScheme = colors[index % colors.length];
                    const totalAnomalies = dashboardStats?.anomalies_detected || 1;
                    const percentage = totalAnomalies > 0 ? Math.round((count / totalAnomalies) * 100) : 0;
                    const displayName = type.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                    
                    return (
                      <div 
                        key={type} 
                        className={`flex items-center justify-between p-4 ${colorScheme.bg} border ${colorScheme.border} rounded-xl backdrop-blur-sm transition-all hover:scale-105`}
                      >
                        <Flex align="center" gap="sm">
                          <div className={`w-3 h-3 ${colorScheme.dot} rounded-full shadow-sm`} />
                          <span className="text-sm font-medium text-white">{displayName}</span>
                        </Flex>
                        <Flex align="center" gap="sm" className="text-right">
                          <span className={`text-sm font-bold ${colorScheme.text}`}>{count}</span>
                          <span className="text-xs text-slate-400">({percentage}%)</span>
                        </Flex>
                      </div>
                    );
                  })}
                  
                  {(!dashboardStats?.anomaly_breakdown || Object.keys(dashboardStats.anomaly_breakdown).length === 0) && (
                    <div className="text-center py-12 text-slate-400">
                      <AlertTriangle className="w-8 h-8 mx-auto mb-3 opacity-50" />
                      <p>No anomaly data available</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </Grid>

          {/* Detailed Data Table */}
          <Card variant="elevated" size="lg">
            <CardHeader>
              <Flex justify="between" align="center">
                <CardTitle>Transaction Volume Detail</CardTitle>
                {dashboardStats?.timestamp && (
                  <p className="text-sm text-slate-400">
                    Last updated: {new Date(dashboardStats.timestamp).toLocaleTimeString()}
                  </p>
                )}
              </Flex>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto rounded-xl border border-slate-700/50">
                <table className="min-w-full divide-y divide-slate-700">
                  <thead>
                    <tr className="bg-slate-800/50">
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Time Period
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Transactions
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Anomalies
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Anomaly Rate
                      </th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Trend
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {dashboardStats?.transaction_volume?.map((row, i) => {
                      const rate = row.transactions > 0 ? (row.anomalies / row.transactions * 100).toFixed(2) : '0.00';
                      const isHighRate = parseFloat(rate) > (dashboardStats.anomaly_rate * 100);
                      return (
                        <tr key={i} className="hover:bg-slate-800/50 transition-colors duration-200">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200 font-medium">
                            {row.hour}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">
                            <span className="text-blue-400 font-semibold">{row.transactions.toLocaleString()}</span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">
                            <span className={`font-semibold ${
                              row.anomalies > 0 ? (isHighRate ? 'text-red-400' : 'text-yellow-400') : 'text-green-400'
                            }`}>
                              {row.anomalies}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">
                            <span className={`font-semibold ${
                              isHighRate ? 'text-red-400' : parseFloat(rate) > 0 ? 'text-yellow-400' : 'text-green-400'
                            }`}>
                              {rate}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-200">
                            {i > 0 && dashboardStats.transaction_volume[i-1] && (
                              row.transactions > dashboardStats.transaction_volume[i-1].transactions ? (
                                <TrendingUp className="w-4 h-4 text-green-400" />
                              ) : row.transactions < dashboardStats.transaction_volume[i-1].transactions ? (
                                <TrendingDown className="w-4 h-4 text-red-400" />
                              ) : (
                                <span className="w-4 h-4 text-slate-500">—</span>
                              )
                            )}
                          </td>
                        </tr>
                      );
                    })}
                    {(!dashboardStats?.transaction_volume || dashboardStats.transaction_volume.length === 0) && (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center">
                          <div className="text-slate-400">
                            <BarChart3 className="w-8 h-8 mx-auto mb-3 opacity-50" />
                            <p className="mb-2">No transaction volume data available</p>
                            <Button 
                              variant="ghost"
                              size="sm"
                              onClick={refresh}
                              className="text-cyan-400 hover:text-cyan-300"
                            >
                              Refresh Data
                            </Button>
                          </div>
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              
              <Divider className="my-6" />
              
              {/* Summary Cards */}
              {dashboardStats && (
                <Grid cols={3} gap="md">
                  <Card variant="glass" className="text-center p-6">
                    <h4 className="text-slate-300 text-sm mb-2">Total Volume (12h)</h4>
                    <p className="text-2xl font-bold text-blue-400">{derivedMetrics.totalVolume.toLocaleString()}</p>
                  </Card>
                  
                  <Card variant="glass" className="text-center p-6">
                    <h4 className="text-slate-300 text-sm mb-2">Total Anomalies (12h)</h4>
                    <p className="text-2xl font-bold text-red-400">{derivedMetrics.totalVolumeAnomalies}</p>
                  </Card>
                  
                  <Card variant="glass" className="text-center p-6">
                    <h4 className="text-slate-300 text-sm mb-2">Notifications Sent</h4>
                    <p className="text-2xl font-bold text-green-400">
                      {dashboardStats.notifications_sent?.total || 0}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {dashboardStats.notifications_sent?.email || 0} emails, {dashboardStats.notifications_sent?.phone || 0} calls
                    </p>
                  </Card>
                </Grid>
              )}
            </CardContent>
          </Card>
        </PageContent>
      </Container>
    </div>
  );
}