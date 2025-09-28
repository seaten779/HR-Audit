import LiveFeed from "@/components/LiveFeed"

export default function LiveFeedPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="mb-12 text-center">
          <div className="flex flex-col items-center gap-6">
            <div>
              <h1 className="text-6xl font-extrabold mb-6 bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent leading-tight text-center">
                Live Transaction Feed
              </h1>
              <p className="text-xl text-slate-300 max-w-3xl mx-auto text-center leading-relaxed">
                Real-time financial activity monitoring with AI-powered anomaly detection
              </p>
            </div>
            <div className="flex items-center space-x-6">
              <div className="inline-flex items-center gap-3 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 px-6 py-3 rounded-full font-semibold">
                <span className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></span>
                <span>Live Monitoring Active</span>
              </div>
            </div>
          </div>
        </header>

        {/* Live Feed Component */}
        <div className="bg-slate-800 border border-slate-700 rounded-3xl p-8 mb-16">
          <LiveFeed />
        </div>

        {/* Info Cards */}
        <section className="bg-slate-800 border border-slate-700 rounded-3xl p-10">
          <h2 className="text-3xl font-bold text-white mb-12 text-center tracking-tight">System Information</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="bg-slate-700 border border-slate-600 rounded-2xl p-6 hover:bg-slate-600 transition-all duration-300">
              <div className="mb-6">
                <h3 className="text-xl font-bold text-white text-center mb-4">How It Works</h3>
              </div>
              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">1</span>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    Transactions are processed in real-time through our streaming pipeline
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">2</span>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    AI models analyze patterns to detect anomalies and assess risk levels
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">3</span>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    Human-readable explanations are generated for each detected anomaly
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-slate-700 border border-slate-600 rounded-2xl p-6 hover:bg-slate-600 transition-all duration-300">
              <div className="mb-6">
                <h3 className="text-xl font-bold text-white text-center mb-4">Risk Levels</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center justify-between px-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    LOW
                  </span>
                  <span className="text-slate-300 text-sm">Suspicious but minor</span>
                </div>
                <div className="flex items-center justify-between px-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-500/20 text-yellow-400 border border-yellow-500/30">
                    MEDIUM
                  </span>
                  <span className="text-slate-300 text-sm">Requires monitoring</span>
                </div>
                <div className="flex items-center justify-between px-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30">
                    HIGH
                  </span>
                  <span className="text-slate-300 text-sm">Needs investigation</span>
                </div>
                <div className="flex items-center justify-between px-2">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-red-600/20 text-red-300 border border-red-600/30">
                    CRITICAL
                  </span>
                  <span className="text-slate-300 text-sm">Immediate action</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-700 border border-slate-600 rounded-2xl p-6 hover:bg-slate-600 transition-all duration-300">
              <div className="mb-6">
                <h3 className="text-xl font-bold text-white text-center mb-4">Detection Types</h3>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3 px-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full flex-shrink-0"></div>
                  <span className="text-slate-300 text-sm">Velocity Spikes</span>
                </div>
                <div className="flex items-center space-x-3 px-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full flex-shrink-0"></div>
                  <span className="text-slate-300 text-sm">High-Value Transactions</span>
                </div>
                <div className="flex items-center space-x-3 px-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full flex-shrink-0"></div>
                  <span className="text-slate-300 text-sm">Foreign Locations</span>
                </div>
                <div className="flex items-center space-x-3 px-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full flex-shrink-0"></div>
                  <span className="text-slate-300 text-sm">Unusual Merchant Categories</span>
                </div>
                <div className="flex items-center space-x-3 px-2">
                  <div className="w-3 h-3 bg-emerald-500 rounded-full flex-shrink-0"></div>
                  <span className="text-slate-300 text-sm">Time-Based Anomalies</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
