import type React from "react"
import type { Metadata, Viewport } from "next"
import { Inter, JetBrains_Mono } from "next/font/google"
import "./globals.css"
import Navigation from "@/components/Navigation"
import NotificationProvider from "@/components/NotificationProvider"

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
  weight: ["300", "400", "500", "600", "700", "800", "900"],
})

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600", "700", "800"],
})

export const metadata: Metadata = {
  title: "HR Audit - AI-Powered HR Analytics",
  description:
    "Advanced AI-powered HR audit and analytics system. Monitor employee data, analyze HR patterns, and get actionable insights for better workforce management.",
  keywords:
    "HR, human resources, audit, analytics, AI, machine learning, workforce management, employee monitoring, HR tech",
  authors: [{ name: "HR Audit Team" }],
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0ea5e9",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable} antialiased font-sans`}>
        <NotificationProvider>
          <Navigation />
          <main className="min-h-screen">{children}</main>
        </NotificationProvider>
      </body>
    </html>
  )
}
