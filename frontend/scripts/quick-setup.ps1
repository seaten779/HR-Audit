# 🚀 Quick Setup Script for Ultimate Mastra System
# Run this in PowerShell to set up your local environment

Write-Host "🚀 Setting up Ultimate Mastra Multi-Agent System..." -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if .env.local exists
if (Test-Path ".env.local") {
    Write-Host "✅ .env.local already exists" -ForegroundColor Yellow
} else {
    Write-Host "📝 Creating .env.local from template..." -ForegroundColor Blue
    Copy-Item ".env.local.example" ".env.local"
    Write-Host "⚠️  Please edit .env.local with your API keys!" -ForegroundColor Red
}

# Install any missing dependencies
Write-Host "📦 Checking dependencies..." -ForegroundColor Blue
$dependencies = @(
    "@sendgrid/mail",
    "@mastra/rag", 
    "@mastra/memory"
)

foreach ($dep in $dependencies) {
    Write-Host "Checking $dep..." -ForegroundColor Gray
    $installed = npm list $dep 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing $dep..." -ForegroundColor Yellow
        npm install $dep
    } else {
        Write-Host "✅ $dep already installed" -ForegroundColor Green
    }
}

# Create demo data directory
Write-Host "📁 Setting up demo data directory..." -ForegroundColor Blue
if (!(Test-Path "data")) {
    New-Item -ItemType Directory -Path "data"
    Write-Host "✅ Created data directory" -ForegroundColor Green
}

# Check Node.js version
Write-Host "🔍 Checking Node.js version..." -ForegroundColor Blue
$nodeVersion = node --version
Write-Host "Node.js version: $nodeVersion" -ForegroundColor Gray

# Setup complete
Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "==================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env.local with your API keys" -ForegroundColor White
Write-Host "2. Run: npm run dev" -ForegroundColor White
Write-Host "3. Run: npm run demo:ultimate" -ForegroundColor White
Write-Host ""
Write-Host "🏆 Ready to dominate the Mastra challenge!" -ForegroundColor Magenta