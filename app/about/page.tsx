import Link from "next/link"

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="text-center mb-20">
          <h1 className="text-6xl font-extrabold mb-6 bg-gradient-to-r from-blue-400 via-cyan-400 to-teal-400 bg-clip-text text-transparent leading-tight">
            About HR Audit
          </h1>
          <p className="text-xl text-slate-300 max-w-4xl mx-auto text-center leading-relaxed mb-8">
            Next-generation fraud detection with intelligent voice calling and real-time AI analysis
          </p>
        </header>

        {/* What Makes Us Different */}
        <section className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-600 rounded-3xl p-12 mb-16">
          <h2 className="text-4xl font-bold text-white mb-12 text-center tracking-tight">What Makes HR Audit Different</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-semibold text-cyan-300 mb-6">🎯 The Problem We Solve</h3>
              <div className="space-y-4">
                <p className="text-slate-300 leading-relaxed">
                  <strong className="text-red-400">$3.1 billion</strong> in fraud losses annually for US banks alone
                </p>
                <p className="text-slate-300 leading-relaxed">
                  Traditional fraud detection systems generate <strong className="text-yellow-400">95% false positives</strong>
                </p>
                <p className="text-slate-300 leading-relaxed">
                  Customer service teams spend <strong className="text-orange-400">hours manually calling</strong> customers about suspicious activity
                </p>
                <p className="text-slate-300 leading-relaxed">
                  Most systems can't explain <em className="text-purple-400">why</em> a transaction was flagged
                </p>
              </div>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-green-300 mb-6">✨ Our Innovative Solution</h3>
              <div className="space-y-4">
                <p className="text-slate-300 leading-relaxed">
                  <strong className="text-green-400">Intelligent Voice Calling:</strong> AI-generated personalized fraud alert calls with customer-specific scripts
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong className="text-blue-400">US Banking Compliance:</strong> Built-in CTR structuring detection, SAR triggering, and regulatory compliance
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong className="text-purple-400">Explainable AI:</strong> Every fraud detection comes with clear explanations and confidence scores
                </p>
                <p className="text-slate-300 leading-relaxed">
                  <strong className="text-cyan-400">Real Customer Data:</strong> Uses actual customer profiles and transaction patterns for realistic testing
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Our Mission */}
        <section className="bg-slate-800 border border-slate-700 rounded-3xl p-12 mb-16">
          <h2 className="text-4xl font-bold text-white mb-8 text-center tracking-tight">Our Mission</h2>
          <div className="max-w-4xl mx-auto text-center">
            <p className="text-2xl text-slate-300 leading-relaxed mb-8">
              <strong className="text-blue-400">"To revolutionize fraud prevention through intelligent automation"</strong>
            </p>
            <p className="text-lg text-slate-400 leading-relaxed mb-6">
              We're not just detecting fraud — we're creating the first comprehensive system that combines 
              <span className="text-cyan-300 font-semibold">advanced AI detection</span>, 
              <span className="text-green-300 font-semibold">intelligent voice communication</span>, and 
              <span className="text-purple-300 font-semibold">regulatory compliance</span> 
              in one seamless platform.
            </p>
            <p className="text-lg text-slate-400 leading-relaxed">
              Built by developers who understand both the technical challenges and the human impact of financial fraud.
            </p>
          </div>
        </section>

        {/* How It Works */}
        <section className="bg-slate-800 border border-slate-700 rounded-3xl p-12 mb-16">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-6 tracking-tight">How FinancePulse Works</h2>
          </div>

          <div className="space-y-12 max-w-5xl mx-auto">
            <div className="flex items-start space-x-8">
              <div className="w-20 h-20 bg-blue-500 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-lg">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-semibold text-white mb-4">Real-Time Data Ingestion</h3>
                <p className="text-slate-300 text-lg leading-relaxed">
                  Transaction data flows into our system through secure APIs and streaming pipelines. We process
                  hundreds of transactions per second with minimal latency.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-8">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-lg">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-semibold text-white mb-4">AI-Powered Analysis</h3>
                <p className="text-slate-300 text-lg leading-relaxed">
                  Multiple machine learning models analyze transaction patterns, considering factors like velocity,
                  amount, merchant category, location, and time. Our ensemble approach combines rule-based systems with
                  deep learning for optimal accuracy.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-8">
              <div className="w-20 h-20 bg-gradient-to-br from-green-500 to-green-600 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-lg">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-semibold text-white mb-4">Explainable Results</h3>
                <p className="text-slate-300 text-lg leading-relaxed">
                  When anomalies are detected, our system generates human-readable explanations detailing why the
                  transaction is suspicious and provides confidence scores for each prediction.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-8">
              <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-orange-600 rounded-3xl flex items-center justify-center flex-shrink-0 shadow-lg">
                <span className="text-2xl font-bold text-white">4</span>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-semibold text-white mb-4">Actionable Insights</h3>
                <p className="text-slate-300 text-lg leading-relaxed">
                  Alerts are prioritized by risk level and include recommended actions for analysts, enabling quick and
                  informed responses to potential threats.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="bg-slate-800 border border-slate-700 rounded-2xl p-8 mb-12">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white text-center">Advanced Technology Stack</h2>
            <p className="text-center text-slate-400 mt-4">Built with cutting-edge technologies for maximum performance and reliability</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-4">🌐 Frontend</h3>
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  Next.js 15
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  React 19
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  TypeScript
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  Tailwind CSS
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  Framer Motion
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  Lucide React
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  React Hooks
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  WebSocket
                </span>
              </div>
            </div>

            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-4">🤖 AI & Backend</h3>
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Python 3.11
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  FastAPI
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  OpenAI GPT
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Mastra Framework
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Scikit-learn
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Pandas
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  NumPy
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                  Pydantic
                </span>
              </div>
            </div>

            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-4">📞 Communication</h3>
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  Twilio Voice
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  TwiML Scripts
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  SMTP Email
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  Real-time Alerts
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  Webhooks
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  Notifications
                </span>
              </div>
            </div>

            <div className="text-center">
              <h3 className="text-xl font-semibold text-white mb-4">🔧 Development</h3>
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  Node.js
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  ESLint
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  Prettier
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  Git
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  VS Code
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  REST APIs
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30">
                  JSON
                </span>
              </div>
            </div>
          </div>
        </section>

        {/* Core Innovations */}
        <section className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-600 rounded-3xl p-12 mb-16">
          <div className="mb-12 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">Core Innovations</h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">Industry-first features that set HR Audit apart from traditional fraud detection systems</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📞</span>
                </div>
                <h3 className="text-2xl font-semibold text-white">Intelligent Voice Calling</h3>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">AI-generated personalized scripts</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Age-appropriate communication</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Automatic Twilio integration</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Risk-based urgency levels</span>
                </li>
              </ul>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🏦</span>
                </div>
                <h3 className="text-2xl font-semibold text-white">US Banking Compliance</h3>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">CTR structuring detection</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">SAR triggering criteria</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">High-risk MCC monitoring</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Velocity fraud patterns</span>
                </li>
              </ul>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🧠</span>
                </div>
                <h3 className="text-2xl font-semibold text-white">Explainable AI</h3>
              </div>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Clear fraud explanations</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Confidence scoring</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Risk factor breakdown</span>
                </li>
                <li className="flex items-start">
                  <div className="w-2 h-2 bg-purple-400 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                  <span className="text-slate-300">Human-readable insights</span>
                </li>
              </ul>
            </div>
          </div>
        </section>


        {/* Get Started */}
        <section className="bg-slate-800 border border-slate-700 rounded-3xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Explore?</h2>
          <p className="text-lg text-slate-300 mb-8">
            Try out the different features and see how AI-powered anomaly detection works in action.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link
              href="/live-feed"
              className="inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl justify-center"
            >
              View Live Feed
            </Link>
            <Link
              href="/scenarios"
              className="inline-flex items-center gap-3 bg-slate-700 hover:bg-slate-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl border border-slate-600 justify-center"
            >
              Try Scenarios
            </Link>
          </div>
        </section>

        {/* Contact/Attribution */}
        <footer className="text-center mt-16">
          <div className="bg-gradient-to-r from-slate-800 via-slate-700 to-slate-800 border border-slate-600 rounded-3xl p-12">
            <h2 className="text-3xl font-bold text-white mb-6">Ready to Experience the Future?</h2>
            <p className="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
              See how HR Audit revolutionizes fraud detection with intelligent voice calling, 
              explainable AI, and real-time analysis in action.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-8">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl justify-center"
              >
                📊 View Live Dashboard
              </Link>
              <Link
                href="/live-feed"
                className="inline-flex items-center gap-3 bg-slate-700 hover:bg-slate-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg transition-all duration-300 hover:scale-105 hover:shadow-xl border border-slate-600 justify-center"
              >
                ⚡ Watch Live Feed
              </Link>
            </div>
            
            <div className="border-t border-slate-600 pt-8 mt-8">
              <p className="text-slate-400 text-lg mb-6">
                Demonstrating the Future of AI in Financial Security
              </p>
              <div className="flex flex-wrap justify-center gap-4 mb-6">
                <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-green-500/20 text-green-400 border border-green-500/30">
                  📞 Intelligent Voice Calling
                </span>
                <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  🏦 US Banking Compliance
                </span>
                <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  🧠 Explainable AI
                </span>
                <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-bold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                  ⚡ Real-time Detection
                </span>
              </div>
              <p className="text-sm text-slate-500">
                Powered by OpenAI, Mastra, Twilio, and cutting-edge fraud detection algorithms
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
