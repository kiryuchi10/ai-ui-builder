#!/usr/bin/env python3
"""
Setup script for AI UI Builder Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def setup_backend():
    """Setup the AI UI Builder backend"""
    print("🚀 Setting up AI UI Builder Backend...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies")
    
    # Initialize database
    print("🔄 Initializing database...")
    try:
        from database import init_database
        init_database()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# AI UI Builder Backend Configuration
DATABASE_URL=sqlite:///./ai_ui_builder.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
FIGMA_ACCESS_TOKEN=your-figma-token
GITHUB_TOKEN=your-github-token
RENDER_API_KEY=your-render-api-key
REDIS_URL=redis://localhost:6379
DEBUG=True
"""
        env_file.write_text(env_content)
        print("✅ Created .env file with default configuration")
        print("⚠️  Please update the .env file with your actual API keys")
    
    print("\n🎉 Backend setup completed!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your API keys")
    print("2. Run the server with: python main.py")
    print("3. Visit http://localhost:8000/docs for API documentation")

def start_server():
    """Start the development server"""
    print("🚀 Starting AI UI Builder Backend...")
    
    # Check if dependencies are installed
    try:
        import fastapi
        import uvicorn
    except ImportError:
        print("❌ Dependencies not installed. Run setup first.")
        sys.exit(1)
    
    # Start the server
    run_command("uvicorn main:app --reload --host 0.0.0.0 --port 8000", "Starting server")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        start_server()
    else:
        setup_backend()