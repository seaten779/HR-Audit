"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import { Container, Flex, Button } from "@/components/ui"
import { Menu, X, Activity, BarChart3, Zap, Settings, Info, Brain, Rocket } from "lucide-react"

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: BarChart3 },
  { name: "Live Feed", href: "/live-feed", icon: Activity },
  { name: "Scenarios", href: "/scenarios", icon: Zap },
  { name: "Admin", href: "/admin", icon: Settings },
  { name: "About", href: "/about", icon: Info },
]

export default function Navigation() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen)

  return (
    <nav className="bg-slate-900/95 backdrop-blur-sm border-b border-slate-700/50 shadow-xl sticky top-0 z-50">
      <Container size="xl" className="relative">
        {/* Main Navigation */}
        <Flex justify="between" align="center" className="h-16">
          {/* Brand Logo */}
          <Link href="/" className="flex items-center space-x-3 group">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-500 rounded-xl flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 shadow-lg">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
                {/* Subtle glow effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-xl blur-sm group-hover:blur-md transition-all duration-300" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold bg-gradient-to-r from-white via-blue-100 to-cyan-200 bg-clip-text text-transparent">
                HR Audit
              </span>
              <span className="text-xs text-slate-400 font-medium tracking-wide">
                AI-Powered Fraud Detection
              </span>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center space-x-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`group relative px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
                    isActive 
                      ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/25" 
                      : "text-slate-300 hover:text-white hover:bg-slate-800/70 hover:shadow-md"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.name}
                  
                  {/* Active indicator */}
                  {isActive && (
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-cyan-500/10 rounded-lg" />
                  )}
                  
                  {/* Hover glow */}
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 to-cyan-500/0 group-hover:from-blue-500/5 group-hover:to-cyan-500/5 rounded-lg transition-all duration-300" />
                </Link>
              )
            })}
          </div>

          {/* Status and Actions */}
          <Flex align="center" gap="md" className="hidden md:flex">
            {/* System Status */}
            <div className="flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-green-900/30 to-emerald-900/30 border border-green-600/30 rounded-full backdrop-blur-sm">
              <div className="relative">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                <div className="absolute inset-0 w-2 h-2 bg-green-400 rounded-full animate-ping opacity-75" />
              </div>
              <span className="text-sm font-medium text-green-300">Live System</span>
            </div>
          </Flex>

          {/* Mobile menu button */}
          <div className="lg:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleMobileMenu}
              className="text-slate-300 hover:text-white"
              aria-label="Toggle mobile menu"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </Button>
          </div>
        </Flex>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden absolute top-16 left-0 right-0 bg-slate-900/95 backdrop-blur-md border-b border-slate-700/50 shadow-2xl">
            <div className="p-4 space-y-2">
              {navItems.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive 
                        ? "bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg" 
                        : "text-slate-300 hover:text-white hover:bg-slate-800/70"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {item.name}
                  </Link>
                )
              })}
              
              {/* Mobile Status */}
              <div className="pt-4 mt-4 border-t border-slate-700/50">
                <div className="flex items-center gap-3 px-4 py-2 text-sm text-slate-300">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  System Status: Online
                </div>
              </div>
            </div>
          </div>
        )}
      </Container>
      
      {/* Subtle background pattern */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-900/5 via-transparent to-cyan-900/5 pointer-events-none" />
    </nav>
  )
}
