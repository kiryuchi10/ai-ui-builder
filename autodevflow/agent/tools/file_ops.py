"""
File Operations Tool - Handle file system operations and project wiring
"""
import os
import shutil
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class FileOperations:
    """
    Handle file system operations for the AutoDevFlow orchestrator
    """
    
    def __init__(self):
        self.project_templates = self._load_project_templates()
    
    def _load_project_templates(self) -> Dict[str, str]:
        """Load project structure templates"""
        return {
            "react_package_json": {
                "name": "autodevflow-frontend",
                "version": "0.1.0",
                "private": True,
                "dependencies": {
                    "@testing-library/jest-dom": "^5.16.4",
                    "@testing-library/react": "^13.3.0",
                    "@testing-library/user-event": "^13.5.0",
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "react-scripts": "5.0.1",
                    "axios": "^1.4.0",
                    "web-vitals": "^2.1.4"
                },
                "devDependencies": {
                    "autoprefixer": "^10.4.7",
                    "postcss": "^8.4.14",
                    "tailwindcss": "^3.1.6"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build",
                    "test": "react-scripts test",
                    "eject": "react-scripts eject"
                }
            },
            
            "fastapi_requirements": [
                "fastapi==0.104.1",
                "uvicorn[standard]==0.24.0",
                "sqlalchemy==2.0.23",
                "pydantic[email]==2.5.0",
                "python-multipart==0.0.6",
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-dotenv==1.0.0",
                "sqlite3"
            ],
            
            "docker_compose": """version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
""",
            
            "frontend_dockerfile": """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
""",
            
            "backend_dockerfile": """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
            
            "gitignore": """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Build outputs
build/
dist/
*.egg-info/

# Testing
coverage/
.coverage
.pytest_cache/

# Temporary files
*.tmp
*.temp
"""
        }
    
    async def execute(self, operation: str = "wire", **kwargs) -> Dict[str, Any]:
        """
        Execute file operations
        
        Args:
            operation: Type of operation (wire, create_project, etc.)
            
        Returns:
            Dict with operation results
        """
        if operation == "wire":
            return self.wire_frontend_backend(**kwargs)
        elif operation == "create_project":
            return self.create_project_structure(**kwargs)
        elif operation == "copy_files":
            return self.copy_generated_files(**kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    def wire_frontend_backend(self, **kwargs) -> Dict[str, Any]:
        """
        Wire frontend and backend components together
        
        Returns:
            Dict with wiring results and generated integration files
        """
        try:
            # Get component information from previous steps
            ui_components = kwargs.get("components", [])
            api_endpoints = kwargs.get("endpoints", [])
            
            # Generate API service for frontend
            api_service = self._generate_api_service(api_endpoints)
            
            # Generate form handlers
            form_handlers = self._generate_form_handlers(ui_components, api_endpoints)
            
            # Generate environment configuration
            env_config = self._generate_env_config()
            
            # Generate CORS configuration
            cors_config = self._generate_cors_config()
            
            return {
                "api_service": api_service,
                "form_handlers": form_handlers,
                "env_config": env_config,
                "cors_config": cors_config,
                "integration_files": {
                    "frontend/src/services/api.js": api_service,
                    "frontend/src/hooks/useApi.js": self._generate_api_hooks(),
                    "frontend/.env": env_config["frontend"],
                    "backend/.env": env_config["backend"],
                    "backend/cors_config.py": cors_config
                }
            }
            
        except Exception as e:
            logger.error(f"Frontend-backend wiring failed: {e}")
            return {"error": str(e)}
    
    def create_project_structure(self, output_dir: str, **kwargs) -> Dict[str, Any]:
        """
        Create complete project structure
        
        Args:
            output_dir: Output directory for the project
            
        Returns:
            Dict with created files and directories
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            created_files = []
            created_dirs = []
            
            # Create frontend structure
            frontend_dir = output_path / "frontend"
            frontend_dir.mkdir(exist_ok=True)
            created_dirs.append(str(frontend_dir))
            
            # Frontend subdirectories
            for subdir in ["src", "src/components", "src/services", "src/hooks", "src/pages", "public"]:
                (frontend_dir / subdir).mkdir(exist_ok=True)
                created_dirs.append(str(frontend_dir / subdir))
            
            # Create backend structure
            backend_dir = output_path / "backend"
            backend_dir.mkdir(exist_ok=True)
            created_dirs.append(str(backend_dir))
            
            # Backend subdirectories
            for subdir in ["models", "routers", "services", "tests"]:
                (backend_dir / subdir).mkdir(exist_ok=True)
                created_dirs.append(str(backend_dir / subdir))
            
            # Create configuration files
            config_files = self._create_config_files(output_path)
            created_files.extend(config_files)
            
            return {
                "project_root": str(output_path),
                "created_directories": created_dirs,
                "created_files": created_files,
                "structure": self._get_project_structure(output_path)
            }
            
        except Exception as e:
            logger.error(f"Project structure creation failed: {e}")
            return {"error": str(e)}
    
    def copy_generated_files(self, source_files: Dict[str, str], output_dir: str) -> Dict[str, Any]:
        """
        Copy generated files to project structure
        
        Args:
            source_files: Dict of {relative_path: content}
            output_dir: Target directory
            
        Returns:
            Dict with copy results
        """
        try:
            output_path = Path(output_dir)
            copied_files = []
            
            for relative_path, content in source_files.items():
                target_path = output_path / relative_path
                
                # Create parent directories
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                if isinstance(content, dict):
                    # JSON content
                    with open(target_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=2)
                else:
                    # Text content
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                copied_files.append(str(target_path))
                logger.info(f"Created file: {target_path}")
            
            return {
                "copied_files": copied_files,
                "total_files": len(copied_files)
            }
            
        except Exception as e:
            logger.error(f"File copying failed: {e}")
            return {"error": str(e)}
    
    def _generate_api_service(self, api_endpoints: List[Dict]) -> str:
        """Generate frontend API service"""
        endpoints_code = []
        
        for endpoint in api_endpoints:
            method = endpoint.get("method", "GET").lower()
            path = endpoint.get("path", "/")
            name = endpoint.get("name", self._path_to_function_name(path))
            
            if method == "get":
                endpoints_code.append(f"""
export const {name} = async (params = {{}}) => {{
  const response = await api.get('{path}', {{ params }});
  return response.data;
}};""")
            elif method == "post":
                endpoints_code.append(f"""
export const {name} = async (data) => {{
  const response = await api.post('{path}', data);
  return response.data;
}};""")
            elif method == "put":
                endpoints_code.append(f"""
export const {name} = async (id, data) => {{
  const response = await api.put(`{path}/${{id}}`, data);
  return response.data;
}};""")
            elif method == "delete":
                endpoints_code.append(f"""
export const {name} = async (id) => {{
  const response = await api.delete(`{path}/${{id}}`);
  return response.data;
}};""")
        
        return f"""import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({{
  baseURL: API_BASE_URL,
  headers: {{
    'Content-Type': 'application/json',
  }},
}});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {{
    const token = localStorage.getItem('authToken');
    if (token) {{
      config.headers.Authorization = `Bearer ${{token}}`;
    }}
    return config;
  }},
  (error) => {{
    return Promise.reject(error);
  }}
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {{
    if (error.response?.status === 401) {{
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }}
    return Promise.reject(error);
  }}
);

// Authentication
export const login = async (email, password) => {{
  const response = await api.post('/api/auth/login', {{ email, password }});
  const {{ access_token }} = response.data;
  localStorage.setItem('authToken', access_token);
  return response.data;
}};

export const logout = () => {{
  localStorage.removeItem('authToken');
}};

export const register = async (userData) => {{
  const response = await api.post('/api/auth/register', userData);
  return response.data;
}};

// API endpoints
{chr(10).join(endpoints_code)}

export default api;
"""
    
    def _generate_form_handlers(self, ui_components: List[Dict], api_endpoints: List[Dict]) -> Dict[str, str]:
        """Generate form handlers based on UI components and API endpoints"""
        handlers = {}
        
        # Find form-related components
        form_components = [comp for comp in ui_components if comp.get("class_label") in ["input", "button"]]
        
        if form_components:
            # Generate contact form handler
            handlers["useContactForm.js"] = """
import { useState } from 'react';
import { submitContactForm } from '../services/api';

export const useContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await submitContactForm(formData);
      setSuccess(true);
      setFormData({ name: '', email: '', message: '' });
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return {
    formData,
    loading,
    error,
    success,
    handleChange,
    handleSubmit
  };
};
"""
        
        return handlers
    
    def _generate_api_hooks(self) -> str:
        """Generate React hooks for API interactions"""
        return """
import { useState, useEffect } from 'react';
import api from '../services/api';

// Generic API hook
export const useApi = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.get(endpoint, options);
        setData(response.data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return { data, loading, error };
};

// Authentication hook
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      // Verify token and get user info
      // This would typically call an API endpoint
      setUser({ token });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/auth/login', { email, password });
      const { access_token, user: userData } = response.data;
      localStorage.setItem('authToken', access_token);
      setUser({ token: access_token, ...userData });
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
  };

  return { user, loading, login, logout };
};

// Form submission hook
export const useFormSubmit = (submitFunction) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const submit = async (data) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await submitFunction(data);
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, success, submit };
};
"""
    
    def _generate_env_config(self) -> Dict[str, str]:
        """Generate environment configuration files"""
        return {
            "frontend": """# Frontend Environment Variables
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
""",
            "backend": """# Backend Environment Variables
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Email Settings (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
"""
        }
    
    def _generate_cors_config(self) -> str:
        """Generate CORS configuration for FastAPI"""
        return """
from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
    \"\"\"Setup CORS middleware for the FastAPI app\"\"\"
    
    # Get allowed origins from environment
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app
"""
    
    def _create_config_files(self, project_root: Path) -> List[str]:
        """Create configuration files for the project"""
        created_files = []
        
        # Frontend package.json
        frontend_package = project_root / "frontend" / "package.json"
        with open(frontend_package, 'w') as f:
            json.dump(self.project_templates["react_package_json"], f, indent=2)
        created_files.append(str(frontend_package))
        
        # Backend requirements.txt
        backend_requirements = project_root / "backend" / "requirements.txt"
        with open(backend_requirements, 'w') as f:
            f.write("\n".join(self.project_templates["fastapi_requirements"]))
        created_files.append(str(backend_requirements))
        
        # Docker Compose
        docker_compose = project_root / "docker-compose.yml"
        with open(docker_compose, 'w') as f:
            f.write(self.project_templates["docker_compose"])
        created_files.append(str(docker_compose))
        
        # Frontend Dockerfile
        frontend_dockerfile = project_root / "frontend" / "Dockerfile"
        with open(frontend_dockerfile, 'w') as f:
            f.write(self.project_templates["frontend_dockerfile"])
        created_files.append(str(frontend_dockerfile))
        
        # Backend Dockerfile
        backend_dockerfile = project_root / "backend" / "Dockerfile"
        with open(backend_dockerfile, 'w') as f:
            f.write(self.project_templates["backend_dockerfile"])
        created_files.append(str(backend_dockerfile))
        
        # .gitignore
        gitignore = project_root / ".gitignore"
        with open(gitignore, 'w') as f:
            f.write(self.project_templates["gitignore"])
        created_files.append(str(gitignore))
        
        # README.md
        readme = project_root / "README.md"
        with open(readme, 'w') as f:
            f.write(self._generate_project_readme())
        created_files.append(str(readme))
        
        return created_files
    
    def _generate_project_readme(self) -> str:
        """Generate project README"""
        return """# AutoDevFlow Generated Application

This full-stack application was generated by AutoDevFlow Orchestrator.

## Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI with SQLAlchemy
- **Database**: SQLite (development) / PostgreSQL (production)
- **Deployment**: Docker Compose

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Development

### Project Structure

```
├── frontend/          # React application
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── pages/
│   └── public/
├── backend/           # FastAPI application
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── tests/
└── docker-compose.yml
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend
cd backend
flake8 .
black .
mypy .

# Frontend
cd frontend
npm run lint
npm run format
```

## Deployment

### Production Docker

```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `CORS_ORIGINS`: Allowed frontend origins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
"""
    
    def _get_project_structure(self, project_root: Path) -> Dict[str, Any]:
        """Get project structure as a nested dict"""
        def build_tree(path: Path) -> Dict[str, Any]:
            tree = {"type": "directory", "children": {}}
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        tree["children"][item.name] = build_tree(item)
                    else:
                        tree["children"][item.name] = {"type": "file", "size": item.stat().st_size}
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(project_root)
    
    def _path_to_function_name(self, path: str) -> str:
        """Convert API path to function name"""
        # Remove path parameters and convert to camelCase
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        parts = clean_path.strip('/').split('/')
        
        # Filter out empty parts and convert to camelCase
        parts = [part for part in parts if part]
        if not parts:
            return "root"
        
        # Convert to camelCase
        function_name = parts[0].lower()
        for part in parts[1:]:
            function_name += part.capitalize()
        
        return function_name
    
    def backup_existing_files(self, target_dir: str) -> Dict[str, Any]:
        """Backup existing files before overwriting"""
        try:
            target_path = Path(target_dir)
            if not target_path.exists():
                return {"backed_up": [], "backup_dir": None}
            
            backup_dir = target_path.parent / f"{target_path.name}_backup"
            backup_dir.mkdir(exist_ok=True)
            
            backed_up_files = []
            for item in target_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(target_path)
                    backup_path = backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, backup_path)
                    backed_up_files.append(str(relative_path))
            
            return {
                "backed_up": backed_up_files,
                "backup_dir": str(backup_dir),
                "total_files": len(backed_up_files)
            }
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {"error": str(e)}
    
    def validate_project_structure(self, project_dir: str) -> Dict[str, Any]:
        """Validate that the project structure is correct"""
        try:
            project_path = Path(project_dir)
            issues = []
            
            # Check required directories
            required_dirs = [
                "frontend/src",
                "frontend/public",
                "backend",
                "backend/models",
                "backend/routers"
            ]
            
            for dir_path in required_dirs:
                if not (project_path / dir_path).exists():
                    issues.append(f"Missing directory: {dir_path}")
            
            # Check required files
            required_files = [
                "frontend/package.json",
                "backend/requirements.txt",
                "backend/main.py",
                "docker-compose.yml"
            ]
            
            for file_path in required_files:
                if not (project_path / file_path).exists():
                    issues.append(f"Missing file: {file_path}")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "total_issues": len(issues)
            }
            
        except Exception as e:
            logger.error(f"Project validation failed: {e}")
            return {"valid": False, "error": str(e)}
    
    def cleanup_temp_files(self, project_dir: str) -> Dict[str, Any]:
        """Clean up temporary files and directories"""
        try:
            project_path = Path(project_dir)
            cleaned_files = []
            
            # Patterns for temporary files
            temp_patterns = [
                "**/*.tmp",
                "**/*.temp",
                "**/__pycache__",
                "**/node_modules",
                "**/.pytest_cache",
                "**/coverage"
            ]
            
            for pattern in temp_patterns:
                for item in project_path.glob(pattern):
                    if item.is_file():
                        item.unlink()
                        cleaned_files.append(str(item))
                    elif item.is_dir():
                        shutil.rmtree(item)
                        cleaned_files.append(str(item))
            
            return {
                "cleaned_files": cleaned_files,
                "total_cleaned": len(cleaned_files)
            }
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {"error": str(e)}