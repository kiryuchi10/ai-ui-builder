#!/usr/bin/env python3
"""
Quick Start Script for Advanced AI-Powered UI Builder
Combines setup and implementation in one command
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    requirements = {
        "python": "python --version",
        "node": "node --version",
        "npm": "npm --version",
        "git": "git --version"
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            subprocess.run(command.split(), capture_output=True, check=True)
            print(f"  ✅ {tool}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {tool}")
            missing.append(tool)
    
    if missing:
        print(f"\n❌ Missing required tools: {', '.join(missing)}")
        print("Please install them before continuing.")
        return False
    
    return True

def check_api_keys():
    """Check if required API keys are set"""
    print("\n🔑 Checking API keys...")
    
    required_keys = [
        "DEEPSEEK_API_KEY",
        "FIGMA_TOKEN",
        "GITHUB_TOKEN",
        "RENDER_API_KEY"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
            print(f"  ❌ {key}")
        else:
            print(f"  ✅ {key}")
    
    if missing_keys:
        print(f"\n⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("You can still run the setup, but some features won't work.")
        print("Add them to your .env file after setup.")
        
        response = input("\nContinue anyway? (y/N): ").lower()
        return response == 'y'
    
    return True

def run_setup():
    """Run the setup script"""
    print("\n🛠️  Running setup...")
    try:
        subprocess.run([sys.executable, "setup_advanced_features.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        return False

async def run_implementation():
    """Run the DeepSeek agent implementation"""
    print("\n🤖 Running DeepSeek agent implementation...")
    
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ DEEPSEEK_API_KEY not found. Skipping implementation.")
        print("Set your API key and run: python deepseek_agent_runner.py")
        return False
    
    try:
        subprocess.run([sys.executable, "deepseek_agent_runner.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Implementation failed: {e}")
        return False

def start_development_servers():
    """Start the development servers"""
    print("\n🚀 Starting development servers...")
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        print("🐳 Docker detected. Starting with Docker Compose...")
        
        try:
            subprocess.run([
                "docker-compose", 
                "-f", "docker-compose.advanced.yml", 
                "up", "-d"
            ], check=True)
            print("✅ Services started with Docker!")
            print("🌐 Frontend: http://localhost:3000")
            print("🔧 Backend: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/docs")
            return True
        except subprocess.CalledProcessError:
            print("❌ Docker Compose failed. Trying manual start...")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("🔧 Docker not available. Starting manually...")
    
    # Manual start
    print("Starting backend...")
    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8000"
    ], cwd="backend")
    
    print("Starting frontend...")
    frontend_process = subprocess.Popen([
        "npm", "run", "dev"
    ], cwd="frontend")
    
    print("✅ Services started manually!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n⚠️  Press Ctrl+C to stop all services")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
    
    return True

def show_feature_overview():
    """Show overview of implemented features"""
    print("\n" + "="*60)
    print("🎉 ADVANCED AI-POWERED UI BUILDER FEATURES")
    print("="*60)
    
    features = [
        ("🔁", "Prompt Memory + Context Awareness", "Track and reuse previous prompts"),
        ("🧩", "Component Library Detection", "Auto-detect and map UI components"),
        ("🌐", "Multi-Deployment Options", "Deploy to Render, Vercel, Netlify, Docker"),
        ("🤖", "LLM-based UI Validator", "Code quality analysis with DeepSeek"),
        ("🧪", "Test Coverage Generator", "Auto-generate Jest test cases"),
        ("📦", "Export Modes", "Export as App, Component, or JSON Schema"),
        ("🎨", "Live Figma Feedback Loop", "Real-time design-to-code sync")
    ]
    
    for icon, name, description in features:
        print(f"{icon} {name}")
        print(f"   {description}")
        print()
    
    print("📖 For detailed documentation, see README_ADVANCED.md")
    print("🔧 For API documentation, visit http://localhost:8000/docs")

def main():
    """Main execution function"""
    print("🚀 ADVANCED AI-POWERED UI BUILDER - QUICK START")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check API keys
    if not check_api_keys():
        sys.exit(1)
    
    # Run setup
    if not run_setup():
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    
    # Ask about implementation
    print("\n🤖 Ready to run DeepSeek agent implementation?")
    print("This will generate all the advanced feature code automatically.")
    
    if os.getenv("DEEPSEEK_API_KEY"):
        response = input("Run implementation now? (Y/n): ").lower()
        if response != 'n':
            asyncio.run(run_implementation())
    else:
        print("⚠️  DEEPSEEK_API_KEY not set. Skipping implementation.")
        print("Set your API key and run: python deepseek_agent_runner.py")
    
    # Ask about starting servers
    print("\n🚀 Ready to start development servers?")
    response = input("Start servers now? (Y/n): ").lower()
    if response != 'n':
        start_development_servers()
    
    # Show feature overview
    show_feature_overview()
    
    print("\n🎉 Quick start completed!")
    print("\n📋 What's Next?")
    print("1. Open http://localhost:3000 to use the UI Builder")
    print("2. Check the new advanced features in the interface")
    print("3. Configure your API keys in the .env files")
    print("4. Read README_ADVANCED.md for detailed usage instructions")
    print("5. Start building amazing UIs with AI assistance!")

if __name__ == "__main__":
    main()