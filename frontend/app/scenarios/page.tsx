"use client"

import { useState } from "react"
import Link from "next/link"

type ScenarioType = "velocity" | "high_value" | "foreign" | "unusual_merchant" | "night_activity"

interface Scenario {
  id: ScenarioType
  title: string
  description: string
  icon: string
  examples: string[]
  riskLevel: "medium" | "high" | "critical"
}

const scenarios: Scenario[] = [
  {
    id: "velocity",
    title: "Velocity Spike",
    description: "Simulate multiple rapid transactions in a short time period",
    icon: "⚡",
    examples: ["5 transactions in 2 minutes", "Rapid card swipes", "ATM velocity spike"],
    riskLevel: "high",
  },
  {
    id: "high_value",
    title: "High-Value Purchase",
    description: "Trigger a transaction significantly above normal spending patterns",
    icon: "💳",
    examples: ["$5,000 electronics purchase", "Luxury item transaction", "Cash advance"],
    riskLevel: "medium",
  },
  {
    id: "foreign",
    title: "Foreign Location",
    description: "Simulate transactions from unusual geographic locations",
    icon: "🌍",
    examples: ["Purchase from foreign country", "Currency exchange", "International ATM"],
    riskLevel: "medium",
  },
  {
    id: "unusual_merchant",
    title: "Unusual Merchant Category",
    description: "Transaction with a merchant type outside normal patterns",
    icon: "🏪",
    examples: ["Gambling establishment", "Adult entertainment", "Cryptocurrency exchange"],
    riskLevel: "high",
  },
  {
    id: "night_activity",
    title: "Off-Hours Activity",
    description: "Simulate transactions during unusual times",
    icon: "🌙",
    examples: ["3 AM purchases", "Weekend bank transfers", "Holiday transactions"],
    riskLevel: "critical",
  },
]

export default function ScenariosPage() {
  const [loading, setLoading] = useState<ScenarioType | null>(null)
  const [lastTriggered, setLastTriggered] = useState<string | null>(null)

  const triggerScenario = async (scenario: Scenario) => {
    setLoading(scenario.id)

    try {
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000"
      const response = await fetch(`${backendUrl}/api/v1/scenarios/trigger?scenario=${scenario.id}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log("Scenario triggered successfully:", result)

      setLastTriggered(scenario.title)

      // Show success notification
      setTimeout(() => setLastTriggered(null), 5000)
    } catch (error) {
      console.error("Error triggering scenario:", error)
      // Still show some feedback to user even if API fails
      setLastTriggered(`${scenario.title} (Demo Mode)`)
      setTimeout(() => setLastTriggered(null), 3000)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-white mb-4">Test Scenarios</h1>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Simulate suspicious activities to test anomaly detection and generate demo data
          </p>
        </header>

        {/* Success Message */}
        {lastTriggered && (
          <div className="mb-12 p-6 bg-green-900/30 border border-green-700 rounded-2xl">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center mr-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-green-300 mb-1">
                  Scenario "{lastTriggered}" triggered successfully!
                </p>
                <p className="text-green-400">
                  Check the{" "}
                  <Link
                    href="/live-feed"
                    className="font-medium text-blue-400 hover:text-blue-300 transition-colors underline"
                  >
                    Live Feed
                  </Link>{" "}
                  to see the generated anomalies.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Scenarios Grid */}
        <section className="mb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {scenarios.map((scenario) => (
              <div
                key={scenario.id}
                className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-6 hover:bg-slate-800/70 transition-all duration-300 text-center"
              >
                <div className="flex items-start justify-between mb-6">
                  <div className="text-4xl">{scenario.icon}</div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${
                      scenario.riskLevel === "medium"
                        ? "bg-yellow-900/50 text-yellow-300 border border-yellow-700"
                        : scenario.riskLevel === "high"
                          ? "bg-orange-900/50 text-orange-300 border border-orange-700"
                          : "bg-red-900/50 text-red-300 border border-red-700"
                    }`}
                  >
                    {scenario.riskLevel.toUpperCase()}
                  </span>
                </div>

                <h3 className="text-xl font-semibold text-white mb-3">{scenario.title}</h3>
                <p className="text-slate-300 mb-6 leading-relaxed">{scenario.description}</p>

                <div className="mb-6">
                  <h4 className="text-sm font-semibold text-white mb-3">Examples:</h4>
                  <ul className="space-y-2">
                    {scenario.examples.map((example, idx) => (
                      <li key={idx} className="flex items-start text-center justify-center">
                        <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 mt-2 flex-shrink-0"></div>
                        <span className="text-sm text-slate-400">{example}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => triggerScenario(scenario)}
                  disabled={loading !== null}
                  className={`w-full py-3 px-4 rounded-xl font-semibold transition-all duration-200 ${
                    loading === scenario.id
                      ? "bg-slate-600 text-slate-400 cursor-not-allowed"
                      : "bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl"
                  }`}
                >
                  {loading === scenario.id ? (
                    <div className="flex items-center justify-center">
                      <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin mr-2"></div>
                      Triggering...
                    </div>
                  ) : (
                    `Trigger ${scenario.title}`
                  )}
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Information Cards */}
        <section className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-2xl p-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">Understanding the scenario testing process</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-700/50 border border-slate-600 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6 text-center">Process Flow</h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">1</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">
                    Click a scenario button to generate synthetic transaction data
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">2</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">The backend creates realistic anomalous transactions</p>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">3</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">
                    AI models process the data and flag anomalies in real-time
                  </p>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-bold text-white">4</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed">Results appear in the Live Feed with explanations</p>
                </div>
              </div>
            </div>

            <div className="bg-slate-700/50 border border-slate-600 rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6 text-center">Demo Guidelines</h3>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-300">Scenarios generate 1-3 related transactions</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-300">Each scenario has different risk patterns</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-300">Perfect for demonstrating detection capabilities</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-300">All generated data is clearly marked as simulated</p>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-slate-300">Use multiple scenarios to show various threat types</p>
                </div>
              </div>

              <div className="mt-6">
                <Link
                  href="/live-feed"
                  className="block w-full py-3 px-4 bg-slate-600 hover:bg-slate-500 text-white text-center rounded-xl font-semibold transition-colors"
                >
                  View Live Feed →
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
