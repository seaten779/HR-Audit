#!/usr/bin/env python3
"""
Cedar OS Voice Integration Setup Script
Helps users configure and test the Twilio-Cedar OS integration
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("🌲" + "="*60 + "🌲")
    print(" " * 15 + "Cedar OS Voice Integration Setup")
    print("🌲" + "="*60 + "🌲")
    print()

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print("✅ Python version:", f"{version.major}.{version.minor}.{version.micro}")
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install Python dependencies:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found. Please ensure you're in the correct directory.")
        return False

def install_node_dependencies():
    """Install Node.js dependencies"""
    print("\n📦 Installing Node.js dependencies...")
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        
        # Install dependencies
        result = subprocess.run(["npm", "install"], capture_output=True, text=True, check=True)
        print("✅ Node.js dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install Node.js dependencies:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js first.")
        return False

def check_env_file():
    """Check and guide user through .env configuration"""
    print("\n⚙️  Checking environment configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    # Read .env file and check for placeholder values
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    placeholders = [
        "your_twilio_account_sid_here",
        "your_twilio_auth_token_here",
        "your_google_cloud_project_id",
        "your_cedar_os_api_key_here",
        "https://your-domain.ngrok.io"
    ]
    
    needs_config = []
    for placeholder in placeholders:
        if placeholder in env_content:
            needs_config.append(placeholder)
    
    if needs_config:
        print("⚠️  The following values in .env need to be configured:")
        for placeholder in needs_config:
            print(f"   • {placeholder}")
        print("\n📝 Please edit the .env file with your actual API keys and endpoints.")
        return False
    
    print("✅ Environment file appears to be configured")
    return True

def test_api_connectivity():
    """Test basic API connectivity"""
    print("\n🔗 Testing API connectivity...")
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is responding")
            print(f"   • Twilio configured: {'✅' if data.get('twilio_configured') else '❌'}")
            print(f"   • Google Speech configured: {'✅' if data.get('google_speech_configured') else '❌'}")
            print(f"   • Google TTS configured: {'✅' if data.get('google_tts_configured') else '❌'}")
            return True
        else:
            print("❌ Server responded with error:", response.status_code)
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server is not running. You'll need to start it manually.")
        return False
    except Exception as e:
        print("❌ Error testing connectivity:", e)
        return False

def create_launch_scripts():
    """Create convenient launch scripts"""
    print("\n📝 Creating launch scripts...")
    
    # Python server launch script
    server_script = """#!/bin/bash
echo "🌲 Starting Cedar OS Voice Integration Server..."
python call-ai.py
"""
    
    with open("start-server.sh", "w") as f:
        f.write(server_script)
    os.chmod("start-server.sh", 0o755)
    
    # React frontend launch script
    frontend_script = """#!/bin/bash
echo "🌲 Starting Cedar OS Voice Integration Frontend..."
npm start
"""
    
    with open("start-frontend.sh", "w") as f:
        f.write(frontend_script)
    os.chmod("start-frontend.sh", 0o755)
    
    # Windows batch files
    server_bat = """@echo off
echo 🌲 Starting Cedar OS Voice Integration Server...
python call-ai.py
pause
"""
    
    with open("start-server.bat", "w") as f:
        f.write(server_bat)
    
    frontend_bat = """@echo off
echo 🌲 Starting Cedar OS Voice Integration Frontend...
npm start
pause
"""
    
    with open("start-frontend.bat", "w") as f:
        f.write(frontend_bat)
    
    print("✅ Launch scripts created:")
    print("   • start-server.sh / start-server.bat")
    print("   • start-frontend.sh / start-frontend.bat")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup Complete! Next Steps:")
    print()
    print("1. Configure your .env file with actual API keys:")
    print("   • Twilio Account SID and Auth Token")
    print("   • Google Cloud credentials and project ID")
    print("   • Cedar OS API endpoint and key")
    print("   • Public webhook URLs (use ngrok for local development)")
    print()
    print("2. Start the Python backend server:")
    print("   • Run: python call-ai.py")
    print("   • Or use: ./start-server.sh (Linux/Mac) or start-server.bat (Windows)")
    print()
    print("3. Start the React frontend (in a new terminal):")
    print("   • Run: npm start")
    print("   • Or use: ./start-frontend.sh (Linux/Mac) or start-frontend.bat (Windows)")
    print()
    print("4. Set up ngrok for webhook URLs:")
    print("   • Install ngrok: https://ngrok.com/")
    print("   • Run: ngrok http 5000")
    print("   • Update PUBLIC_BASE_URL in .env with your ngrok URL")
    print()
    print("5. Test the integration:")
    print("   • Open http://localhost:3000 in your browser")
    print("   • Check system status in the dashboard")
    print("   • Try making a test call")
    print()
    print("📚 Documentation:")
    print("   • API endpoints: http://localhost:5000/health")
    print("   • Frontend dashboard: http://localhost:3000")
    print()
    print("🆘 Need help? Check the logs and configuration files!")

def main():
    """Main setup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    success = True
    success &= install_python_dependencies()
    success &= install_node_dependencies()
    
    if not success:
        print("\n❌ Dependency installation failed. Please fix the errors above.")
        sys.exit(1)
    
    # Check configuration
    env_configured = check_env_file()
    
    # Test connectivity (if server is running)
    test_api_connectivity()
    
    # Create launch scripts
    create_launch_scripts()
    
    # Print next steps
    print_next_steps()
    
    if not env_configured:
        print("\n⚠️  Don't forget to configure your .env file before starting the server!")

if __name__ == "__main__":
    main()