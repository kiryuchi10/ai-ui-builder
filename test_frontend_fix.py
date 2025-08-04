#!/usr/bin/env python3
"""
Quick test to verify the frontend fixes are working
"""

import os
import subprocess
import sys

def test_frontend_syntax():
    """Test if the frontend components have valid syntax"""
    
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("📦 Installing dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    # Try to build the project
    print("🔨 Testing build...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"], 
            cwd=frontend_dir, 
            capture_output=True, 
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Frontend build successful!")
            return True
        else:
            print("❌ Build failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Build timed out")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def check_component_files():
    """Check if all component files exist and are readable"""
    
    components = [
        "frontend/src/components/TestGenerator.jsx",
        "frontend/src/components/PromptMemory.jsx", 
        "frontend/src/components/ValidationDashboard.jsx",
        "frontend/src/components/ExportMenu.jsx",
        "frontend/src/App.jsx"
    ]
    
    print("📁 Checking component files...")
    all_exist = True
    
    for component in components:
        if os.path.exists(component):
            print(f"✅ {component}")
        else:
            print(f"❌ {component} - NOT FOUND")
            all_exist = False
    
    return all_exist

def main():
    """Main test function"""
    print("🚀 AI UI Builder - Frontend Fix Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("ai-ui-builder"):
        print("❌ Please run this from the parent directory of ai-ui-builder")
        return False
    
    os.chdir("ai-ui-builder")
    
    # Check component files
    if not check_component_files():
        print("❌ Some component files are missing")
        return False
    
    # Test frontend syntax
    if not test_frontend_syntax():
        print("❌ Frontend syntax test failed")
        return False
    
    print("\n🎉 All tests passed! Frontend is ready to go!")
    print("\n📋 Next steps:")
    print("1. cd ai-ui-builder/frontend")
    print("2. npm start")
    print("3. Open http://localhost:3000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)