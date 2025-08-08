#!/usr/bin/env python3
"""
AutoDevFlow Orchestrator Setup Script
Integrates AI UI Builder with Backend Automation Paper2Code
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDevFlowSetup:
    """Setup and configuration for AutoDevFlow Orchestrator"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.ai_ui_builder_dir = self.root_dir
        self.backend_automation_dir = self.root_dir.parent / "backend-automation-paper2code"
        self.autodevflow_dir = self.root_dir / "autodevflow"
        
    def run_setup(self):
        """Run complete setup process"""
        logger.info("🚀 Starting AutoDevFlow Orchestrator Setup")
        
        try:
            # Step 1: Verify prerequisites
            self.verify_prerequisites()
            
            # Step 2: Setup Python environment
            self.setup_python_environment()
            
            # Step 3: Install dependencies
            self.install_dependencies()
            
            # Step 4: Setup integration
            self.setup_integration()
            
            # Step 5: Initialize models and data
            self.initialize_models()
            
            # Step 6: Create configuration
            self.create_configuration()
            
            # Step 7: Run tests
            self.run_tests()
            
            logger.info("✅ AutoDevFlow Orchestrator setup completed successfully!")
            self.print_usage_instructions()
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            sys.exit(1)
    
    def verify_prerequisites(self):
        """Verify system prerequisites"""
        logger.info("🔍 Verifying prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 or higher is required")
        
        # Check if backend-automation-paper2code exists
        if not self.backend_automation_dir.exists():
            logger.warning(f"Backend automation directory not found: {self.backend_automation_dir}")
            logger.info("AutoDevFlow will work with limited backend integration")
        
        # Check for required system tools
        required_tools = ["git", "npm"]
        for tool in required_tools:
            if not shutil.which(tool):
                logger.warning(f"{tool} not found - some features may be limited")
        
        logger.info("✅ Prerequisites verified")
    
    def setup_python_environment(self):
        """Setup Python virtual environment"""
        logger.info("🐍 Setting up Python environment...")
        
        venv_dir = self.root_dir / ".venv"
        
        if not venv_dir.exists():
            logger.info("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        
        # Activate virtual environment
        if os.name == 'nt':  # Windows
            activate_script = venv_dir / "Scripts" / "activate.bat"
            pip_path = venv_dir / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            activate_script = venv_dir / "bin" / "activate"
            pip_path = venv_dir / "bin" / "pip"
        
        if not pip_path.exists():
            raise RuntimeError("Failed to create virtual environment")
        
        logger.info("✅ Python environment ready")
    
    def install_dependencies(self):
        """Install Python dependencies"""
        logger.info("📦 Installing dependencies...")
        
        # Create requirements file
        requirements = self.create_requirements_file()
        
        # Install requirements
        venv_dir = self.root_dir / ".venv"
        pip_path = venv_dir / ("Scripts/pip.exe" if os.name == 'nt' else "bin/pip")
        
        subprocess.run([
            str(pip_path), "install", "-r", str(requirements)
        ], check=True)
        
        # Install optional dependencies
        self.install_optional_dependencies(pip_path)
        
        logger.info("✅ Dependencies installed")
    
    def create_requirements_file(self) -> Path:
        """Create requirements.txt file"""
        requirements_content = """
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic[email]==2.5.0
python-multipart==0.0.6

# Computer Vision
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.0.1

# Machine Learning
torch>=2.0.0
torchvision>=0.15.0

# OCR
pytesseract==0.3.10

# Code Quality
flake8==6.1.0
black==23.9.1
mypy==1.6.1
pylint==3.0.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
requests==2.31.0
aiofiles==23.2.1

# Database
sqlalchemy==2.0.23
alembic==1.12.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Development
jupyter==1.0.0
ipython==8.16.1
""".strip()
        
        requirements_path = self.root_dir / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)
        
        return requirements_path
    
    def install_optional_dependencies(self, pip_path: Path):
        """Install optional dependencies"""
        optional_packages = [
            "paddleocr",  # Better OCR
            "transformers",  # For CodeT5+
            "datasets",  # For training data
        ]
        
        for package in optional_packages:
            try:
                logger.info(f"Installing optional package: {package}")
                subprocess.run([str(pip_path), "install", package], 
                             check=False, capture_output=True)
            except Exception as e:
                logger.warning(f"Failed to install {package}: {e}")
    
    def setup_integration(self):
        """Setup integration with backend-automation-paper2code"""
        logger.info("🔗 Setting up integration...")
        
        # Create integration configuration
        integration_config = {
            "backend_automation_path": str(self.backend_automation_dir),
            "papers_path": str(self.backend_automation_dir / "Papers" / "mypapers" / "frontend"),
            "integration_enabled": self.backend_automation_dir.exists()
        }
        
        config_path = self.autodevflow_dir / "integration_config.json"
        with open(config_path, 'w') as f:
            json.dump(integration_config, f, indent=2)
        
        # Setup Python path for integration
        if self.backend_automation_dir.exists():
            self.setup_python_path_integration()
        
        logger.info("✅ Integration setup complete")
    
    def setup_python_path_integration(self):
        """Setup Python path for backend automation integration"""
        # Create __init__.py files for proper imports
        init_files = [
            self.backend_automation_dir / "__init__.py",
            self.backend_automation_dir / "backend" / "__init__.py",
            self.backend_automation_dir / "backend" / "app" / "__init__.py",
            self.backend_automation_dir / "backend" / "app" / "services" / "__init__.py",
        ]
        
        for init_file in init_files:
            if init_file.parent.exists() and not init_file.exists():
                init_file.touch()
    
    def initialize_models(self):
        """Initialize models and datasets"""
        logger.info("🤖 Initializing models...")
        
        # Create model directories
        models_dir = self.autodevflow_dir / "models"
        models_dir.mkdir(exist_ok=True)
        
        for model_type in ["maskrcnn", "pix2code", "codet5"]:
            (models_dir / model_type).mkdir(exist_ok=True)
        
        # Create datasets directory
        datasets_dir = self.autodevflow_dir / "datasets"
        datasets_dir.mkdir(exist_ok=True)
        
        for dataset_type in ["rico", "ui_annotations"]:
            (datasets_dir / dataset_type).mkdir(exist_ok=True)
        
        # Create placeholder model files
        self.create_model_placeholders(models_dir)
        
        logger.info("✅ Models initialized")
    
    def create_model_placeholders(self, models_dir: Path):
        """Create placeholder model files"""
        
        # Mask R-CNN placeholder
        maskrcnn_config = {
            "model_type": "maskrcnn",
            "classes": ["button", "input", "checkbox", "radio", "select", 
                       "icon", "image", "text", "navbar", "list", "table", "card"],
            "input_size": [800, 800],
            "confidence_threshold": 0.7,
            "nms_threshold": 0.5
        }
        
        with open(models_dir / "maskrcnn" / "config.json", 'w') as f:
            json.dump(maskrcnn_config, f, indent=2)
        
        # pix2code placeholder
        pix2code_config = {
            "model_type": "pix2code",
            "encoder": "cnn",
            "decoder": "lstm",
            "vocab_size": 1000,
            "max_sequence_length": 512,
            "embedding_dim": 256
        }
        
        with open(models_dir / "pix2code" / "config.json", 'w') as f:
            json.dump(pix2code_config, f, indent=2)
        
        # CodeT5+ placeholder
        codet5_config = {
            "model_type": "codet5",
            "model_name": "Salesforce/codet5p-770m",
            "max_input_length": 512,
            "max_output_length": 512,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        with open(models_dir / "codet5" / "config.json", 'w') as f:
            json.dump(codet5_config, f, indent=2)
    
    def create_configuration(self):
        """Create main configuration file"""
        logger.info("⚙️ Creating configuration...")
        
        config = {
            "version": "1.0.0",
            "models": {
                "maskrcnn_path": "autodevflow/models/maskrcnn/",
                "pix2code_path": "autodevflow/models/pix2code/",
                "codet5_path": "autodevflow/models/codet5/"
            },
            "output_dirs": {
                "frontend": "services/frontend/",
                "backend": "services/backend/"
            },
            "quality_thresholds": {
                "min_score": 0.7,
                "max_lint_errors": 5,
                "max_complexity": 10
            },
            "integration": {
                "backend_automation_enabled": self.backend_automation_dir.exists(),
                "papers_path": str(self.backend_automation_dir / "Papers" / "mypapers" / "frontend") if self.backend_automation_dir.exists() else None
            },
            "logging": {
                "level": "INFO",
                "file": "autodevflow.log"
            }
        }
        
        config_path = self.autodevflow_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("✅ Configuration created")
    
    def run_tests(self):
        """Run basic tests to verify setup"""
        logger.info("🧪 Running tests...")
        
        try:
            # Test imports
            sys.path.insert(0, str(self.root_dir))
            
            from autodevflow.agent.planner import AutoDevFlowPlanner
            from autodevflow.agent.tools.vision_detect import VisionDetector
            from autodevflow.agent.tools.ocr import OCRProcessor
            
            logger.info("✅ Import tests passed")
            
            # Test basic functionality
            planner = AutoDevFlowPlanner(str(self.autodevflow_dir / "config.json"))
            logger.info("✅ Planner initialization test passed")
            
        except Exception as e:
            logger.warning(f"Some tests failed: {e}")
            logger.info("Setup completed with warnings - some features may be limited")
    
    def print_usage_instructions(self):
        """Print usage instructions"""
        print("\n" + "="*60)
        print("🎉 AutoDevFlow Orchestrator Setup Complete!")
        print("="*60)
        print("\n📋 Usage Instructions:")
        print("\n1. Activate the virtual environment:")
        if os.name == 'nt':
            print(f"   .venv\\Scripts\\activate")
        else:
            print(f"   source .venv/bin/activate")
        
        print("\n2. Generate an application from UI screenshot:")
        print("   python -m autodevflow.agent.planner --input screenshot.png --spec \"Create login system\"")
        
        print("\n3. Generate from natural language only:")
        print("   python -m autodevflow.agent.planner --spec \"Create a REST API for user management\"")
        
        print("\n4. Use with custom configuration:")
        print("   python -m autodevflow.agent.planner --config custom_config.json --input ui.png")
        
        print("\n📁 Project Structure:")
        print("   autodevflow/")
        print("   ├── agent/           # Main orchestrator")
        print("   ├── models/          # AI models")
        print("   ├── datasets/        # Training data")
        print("   └── services/        # Generated outputs")
        
        print("\n🔧 Configuration:")
        print(f"   Config file: {self.autodevflow_dir / 'config.json'}")
        print(f"   Integration: {'✅ Enabled' if self.backend_automation_dir.exists() else '❌ Limited'}")
        
        print("\n📚 Documentation:")
        print("   See autodevflow/README.md for detailed usage")
        print("\n" + "="*60)

def main():
    """Main setup function"""
    setup = AutoDevFlowSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()