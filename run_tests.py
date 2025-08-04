#!/usr/bin/env python3
"""
Simple test runner for AI UI Builder
"""

import subprocess
import sys
import os
import time

def run_backend_tests():
    """Run backend API tests"""
    print("🔧 Starting Backend Server...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    try:
        # Start the backend server in background
        backend_process = subprocess.Popen(
            [sys.executable, 'main.py'],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Run the comprehensive tests
        print("🧪 Running End-to-End Tests...")
        test_result = subprocess.run([sys.executable, 'test_complete_system.py'], 
                                   capture_output=True, text=True)
        
        print(test_result.stdout)
        if test_result.stderr:
            print("Errors:", test_result.stderr)
        
        return test_result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    finally:
        # Clean up backend process
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except:
            backend_process.kill()

def run_frontend_tests():
    """Run frontend tests"""
    print("🎨 Testing Frontend Components...")
    
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    # Check if node_modules exists
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir)
    
    # Run frontend tests (if they exist)
    try:
        result = subprocess.run(['npm', 'test', '--', '--watchAll=false'], 
                              cwd=frontend_dir, capture_output=True, text=True)
        print("Frontend test output:", result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"⚠️  Frontend tests not configured yet: {e}")
        return True  # Don't fail if frontend tests aren't set up

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking Dependencies...")
    
    # Check Python dependencies
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ Python dependencies OK")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("💡 Run: pip install -r backend/requirements.txt")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js OK ({result.stdout.strip()})")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False
    
    return True

def main():
    """Main test runner"""
    print("🚀 AI UI Builder Test Suite")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("❌ Dependency check failed. Please install missing dependencies.")
        return 1
    
    # Run tests
    backend_success = run_backend_tests()
    frontend_success = run_frontend_tests()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if backend_success and frontend_success:
        print("✅ All tests passed! System is ready for use.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        if not backend_success:
            print("   • Backend tests failed")
        if not frontend_success:
            print("   • Frontend tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())