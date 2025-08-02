#!/usr/bin/env python3
"""
Setup script for Advanced AI-Powered UI Builder Features
Prepares the environment and installs dependencies for DeepSeek integration
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class AdvancedSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        
    def run_command(self, command: str, cwd: Path = None) -> bool:
        """Run shell command and return success status"""
        try:
            result = subprocess.run(
                command.split(),
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ {command}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running '{command}': {e.stderr}")
            return False
    
    def create_directory_structure(self):
        """Create necessary directory structure"""
        print("📁 Creating directory structure...")
        
        directories = [
            "backend/models",
            "backend/services",
            "backend/routes",
            "backend/config",
            "backend/schemas",
            "backend/migrations/versions",
            "frontend/src/components/advanced",
            "frontend/src/hooks",
            "frontend/src/utils",
            "docs",
            "tests/backend",
            "tests/frontend"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  📂 {directory}")
        
        print("✅ Directory structure created!")
    
    def setup_backend_dependencies(self):
        """Install backend dependencies"""
        print("🐍 Setting up backend dependencies...")
        
        # Create virtual environment if it doesn't exist
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            if not self.run_command("python -m venv venv", self.backend_dir):
                return False
        
        # Activate virtual environment and install dependencies
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
            python_path = venv_path / "Scripts" / "python"
        else:
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        # Install advanced requirements
        requirements_file = self.project_root / "requirements_advanced.txt"
        if requirements_file.exists():
            install_cmd = f"{pip_path} install -r {requirements_file}"
            if not self.run_command(install_cmd):
                return False
        
        print("✅ Backend dependencies installed!")
        return True
    
    def setup_frontend_dependencies(self):
        """Install frontend dependencies"""
        print("⚛️ Setting up frontend dependencies...")
        
        # Install additional frontend packages
        additional_packages = [
            "@testing-library/jest-dom",
            "@testing-library/react",
            "@testing-library/user-event",
            "react-syntax-highlighter",
            "react-hot-toast",
            "framer-motion",
            "lucide-react",
            "recharts",
            "react-hook-form",
            "zustand",
            "react-query",
            "socket.io-client"
        ]
        
        for package in additional_packages:
            if not self.run_command(f"npm install {package}", self.frontend_dir):
                print(f"⚠️ Warning: Failed to install {package}")
        
        print("✅ Frontend dependencies installed!")
        return True
    
    def create_environment_template(self):
        """Create environment variable templates"""
        print("🔧 Creating environment templates...")
        
        backend_env_template = """# Advanced AI-Powered UI Builder Environment Variables

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/ai_ui_builder
REDIS_URL=redis://localhost:6379/0

# AI Service Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=your_openai_api_key_here

# External Service APIs
FIGMA_TOKEN=your_figma_token_here
GITHUB_TOKEN=your_github_token_here
RENDER_API_KEY=your_render_api_key_here
VERCEL_TOKEN=your_vercel_token_here
NETLIFY_TOKEN=your_netlify_token_here

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Background Tasks
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Monitoring and Logging
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# Feature Flags
ENABLE_FIGMA_WATCHER=true
ENABLE_AUTO_DEPLOYMENT=true
ENABLE_CODE_VALIDATION=true
ENABLE_TEST_GENERATION=true
"""
        
        frontend_env_template = """# Frontend Environment Variables

VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENABLE_ANALYTICS=false
VITE_SENTRY_DSN=your_frontend_sentry_dsn_here
"""
        
        # Write backend .env template
        backend_env_path = self.backend_dir / ".env.template"
        with open(backend_env_path, 'w') as f:
            f.write(backend_env_template)
        
        # Write frontend .env template
        frontend_env_path = self.frontend_dir / ".env.template"
        with open(frontend_env_path, 'w') as f:
            f.write(frontend_env_template)
        
        print("✅ Environment templates created!")
        print("📝 Please copy .env.template to .env and fill in your API keys")
    
    def create_docker_configuration(self):
        """Create Docker configuration for advanced features"""
        print("🐳 Creating Docker configuration...")
        
        docker_compose_content = """version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_ui_builder
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Redis for caching and background tasks
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_ui_builder
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Celery Worker for background tasks
  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_ui_builder
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    command: celery -A background_tasks worker --loglevel=info

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
"""
        
        docker_compose_path = self.project_root / "docker-compose.advanced.yml"
        with open(docker_compose_path, 'w') as f:
            f.write(docker_compose_content)
        
        # Create backend Dockerfile
        backend_dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_advanced.txt .
RUN pip install --no-cache-dir -r requirements_advanced.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        backend_dockerfile_path = self.backend_dir / "Dockerfile"
        with open(backend_dockerfile_path, 'w') as f:
            f.write(backend_dockerfile)
        
        # Create frontend Dockerfile
        frontend_dockerfile = """FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""
        
        frontend_dockerfile_path = self.frontend_dir / "Dockerfile"
        with open(frontend_dockerfile_path, 'w') as f:
            f.write(frontend_dockerfile)
        
        print("✅ Docker configuration created!")
    
    def create_testing_configuration(self):
        """Create testing configuration files"""
        print("🧪 Creating testing configuration...")
        
        # Backend pytest configuration
        pytest_config = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=backend
    --cov-report=html
    --cov-report=term-missing
    --asyncio-mode=auto
asyncio_mode = auto
"""
        
        pytest_ini_path = self.project_root / "pytest.ini"
        with open(pytest_ini_path, 'w') as f:
            f.write(pytest_config)
        
        # Frontend Jest configuration
        jest_config = """{
  "testEnvironment": "jsdom",
  "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
  "moduleNameMapping": {
    "\\\\.(css|less|scss|sass)$": "identity-obj-proxy"
  },
  "collectCoverageFrom": [
    "src/**/*.{js,jsx}",
    "!src/index.js",
    "!src/reportWebVitals.js"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 70,
      "functions": 70,
      "lines": 70,
      "statements": 70
    }
  }
}"""
        
        jest_config_path = self.frontend_dir / "jest.config.json"
        with open(jest_config_path, 'w') as f:
            f.write(jest_config)
        
        print("✅ Testing configuration created!")
    
    def create_github_workflows(self):
        """Create GitHub Actions workflows"""
        print("🔄 Creating GitHub Actions workflows...")
        
        workflow_content = """name: Advanced AI UI Builder CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        python -m pip install --upgrade pip
        pip install -r requirements_advanced.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
        DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
      run: |
        cd backend
        pytest

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Build
      run: |
        cd frontend
        npm run build

  deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Add your deployment commands here
"""
        
        workflows_dir = self.project_root / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_path = workflows_dir / "advanced-features.yml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        print("✅ GitHub Actions workflows created!")
    
    def create_documentation(self):
        """Create documentation files"""
        print("📚 Creating documentation...")
        
        readme_content = """# Advanced AI-Powered UI Builder Features

## 🚀 New Features

### 🔁 Prompt Memory + Context Awareness
- Track and reuse previous prompts
- Context-aware UI generation
- Prompt history management

### 🧩 Component Library Detection
- Auto-detect common UI components
- Map to standardized code snippets
- Reusable component library

### 🌐 Multi-Deployment Options
- Deploy to Render, Vercel, Netlify, or Docker
- Environment-specific configurations
- Automated deployment pipelines

### 🤖 LLM-based UI Validator
- Code quality analysis using DeepSeek
- Accessibility compliance checking
- Performance optimization suggestions

### 🧪 Test Coverage Generator
- Auto-generate Jest test cases
- React Testing Library integration
- Comprehensive test coverage

### 📦 Export Modes
- Export as React App, Component Library, or JSON Schema
- Multiple output formats
- Customizable export configurations

### 🎨 Live Figma Design Feedback Loop
- Real-time Figma file monitoring
- Automatic code regeneration on design changes
- Seamless design-to-code workflow

## 🛠️ Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements_advanced.txt
   cd frontend && npm install
   ```

2. **Environment Configuration**
   ```bash
   cp backend/.env.template backend/.env
   cp frontend/.env.template frontend/.env
   # Fill in your API keys
   ```

3. **Database Setup**
   ```bash
   cd backend
   alembic upgrade head
   ```

4. **Start Services**
   ```bash
   # Using Docker
   docker-compose -f docker-compose.advanced.yml up

   # Or manually
   cd backend && uvicorn main:app --reload
   cd frontend && npm run dev
   ```

## 🔧 Configuration

### Required API Keys
- `DEEPSEEK_API_KEY`: For AI-powered features
- `FIGMA_TOKEN`: For Figma integration
- `GITHUB_TOKEN`: For repository management
- `RENDER_API_KEY`: For Render deployment
- `VERCEL_TOKEN`: For Vercel deployment
- `NETLIFY_TOKEN`: For Netlify deployment

### Optional Services
- PostgreSQL database
- Redis for caching and background tasks
- Celery for background job processing

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# Integration tests
python -m pytest tests/integration/
```

## 📖 API Documentation

Visit `/docs` when running the backend server for interactive API documentation.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.
"""
        
        readme_path = self.project_root / "README_ADVANCED.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print("✅ Documentation created!")
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Starting Advanced AI-Powered UI Builder Setup...")
        print("="*60)
        
        steps = [
            ("Creating directory structure", self.create_directory_structure),
            ("Setting up backend dependencies", self.setup_backend_dependencies),
            ("Setting up frontend dependencies", self.setup_frontend_dependencies),
            ("Creating environment templates", self.create_environment_template),
            ("Creating Docker configuration", self.create_docker_configuration),
            ("Creating testing configuration", self.create_testing_configuration),
            ("Creating GitHub workflows", self.create_github_workflows),
            ("Creating documentation", self.create_documentation),
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                step_func()
            except Exception as e:
                print(f"❌ Error in {step_name}: {str(e)}")
                continue
        
        print("\n" + "="*60)
        print("🎉 Advanced setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Copy .env.template files to .env and add your API keys")
        print("2. Run: python deepseek_agent_runner.py")
        print("3. Start the development servers")
        print("4. Begin using the advanced features!")
        print("\n💡 Tip: Check README_ADVANCED.md for detailed instructions")

if __name__ == "__main__":
    setup = AdvancedSetup()
    setup.run_setup()