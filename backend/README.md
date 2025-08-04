# AI UI Builder Backend

A powerful FastAPI backend for the AI UI Builder with advanced features including prompt history, UI validation, and comprehensive API endpoints.

## 🚀 Features

### ✅ Implemented (High Priority)
- **Prompt History & Context Awareness**
  - SQLAlchemy database models for prompt storage
  - Full CRUD API for prompt history
  - Prompt similarity detection
  - Usage statistics and analytics
  - Template system for common prompts

- **LLM-based UI Validator**
  - Accessibility compliance checking
  - Performance optimization suggestions
  - Code quality analysis
  - Automatic fix generation
  - Comprehensive scoring system

- **Enhanced API Architecture**
  - Modular route structure
  - Comprehensive error handling
  - Database integration
  - Background task processing

### 🔄 Core Generation Pipeline
- AI orchestration for UI generation
- Figma integration for wireframes
- GitHub repository creation
- Render deployment automation
- Real-time status tracking

## 📁 Project Structure

```
backend/
├── models/
│   ├── __init__.py
│   └── prompt_model.py          # Database models
├── routes/
│   ├── __init__.py
│   ├── history.py               # Prompt history endpoints
│   └── validation.py            # UI validation endpoints
├── services/
│   ├── ai_orchestrator.py       # Main AI coordination
│   ├── history_service.py       # History management
│   ├── ui_validator.py          # Code validation
│   ├── figma_tool.py            # Figma integration
│   ├── github_tool.py           # GitHub operations
│   └── render_tool.py           # Deployment service
├── database.py                  # Database configuration
├── main.py                      # FastAPI application
├── requirements.txt             # Dependencies
├── setup.py                     # Setup script
└── README.md                    # This file
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Git

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd ai-ui-builder/backend

# Run the setup script
python setup.py

# Start the development server
python setup.py start
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from database import init_database; init_database()"

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=sqlite:///./ai_ui_builder.db

# Security
SECRET_KEY=your-secret-key-here

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Integrations
FIGMA_ACCESS_TOKEN=your-figma-token
GITHUB_TOKEN=your-github-token
RENDER_API_KEY=your-render-api-key

# Cache
REDIS_URL=redis://localhost:6379

# Development
DEBUG=True
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Prompt History
- `GET /api/v1/history/` - Get prompt history with filtering
- `POST /api/v1/history/` - Save new prompt
- `GET /api/v1/history/{id}` - Get specific prompt
- `PUT /api/v1/history/{id}` - Update prompt
- `DELETE /api/v1/history/{id}` - Delete prompt
- `GET /api/v1/history/stats/overview` - Get usage statistics

#### UI Validation
- `POST /api/v1/validation/validate` - Validate UI code
- `POST /api/v1/validation/fix` - Apply automatic fixes
- `GET /api/v1/validation/rules` - Get validation rules

#### Core Generation
- `POST /generate` - Start UI generation
- `GET /status/{job_id}` - Get generation status
- `DELETE /jobs/{job_id}` - Cancel generation job

## 🗄️ Database Schema

### PromptHistory Table
```sql
CREATE TABLE prompt_history (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255),
    prompt TEXT NOT NULL,
    project_name VARCHAR(255),
    generated_code TEXT,
    figma_url VARCHAR(500),
    github_repo VARCHAR(255),
    deploy_url VARCHAR(500),
    status VARCHAR(50) DEFAULT 'pending',
    job_id VARCHAR(255),
    generation_time INTEGER,
    ai_model_used VARCHAR(100),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    metadata JSON,
    tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

### PromptTemplate Table
```sql
CREATE TABLE prompt_templates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template TEXT NOT NULL,
    category VARCHAR(100),
    usage_count INTEGER DEFAULT 0,
    success_rate INTEGER DEFAULT 0,
    tags JSON,
    variables JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Manual Testing
```bash
# Test history endpoint
curl -X GET "http://localhost:8000/api/v1/history/" \
     -H "accept: application/json"

# Test validation endpoint
curl -X POST "http://localhost:8000/api/v1/validation/validate" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"code": "function App() { return <div>Hello</div>; }", "code_type": "react"}'
```

## 🔍 UI Validation Features

### Accessibility Checks
- Missing alt text on images
- Buttons without descriptive text
- Missing ARIA labels
- Semantic HTML usage
- Color contrast validation

### Performance Analysis
- Inline styles detection
- Image optimization suggestions
- Lazy loading recommendations
- React memoization opportunities

### Code Quality
- Unused imports detection
- Console log removal
- Hardcoded values identification
- Component structure validation

### Scoring System
- **Overall Score**: 0-10 weighted average
- **Accessibility Score**: 40% weight
- **Performance Score**: 30% weight
- **Code Quality Score**: 30% weight

## 🚀 Deployment

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Using Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t ai-ui-builder-backend .
docker run -p 8000:8000 ai-ui-builder-backend
```

### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:password@localhost/ai_ui_builder
REDIS_URL=redis://localhost:6379
DEBUG=False
SECRET_KEY=your-production-secret-key
```

## 📈 Monitoring & Logging

### Health Check
```bash
curl http://localhost:8000/
```

### Metrics Endpoints
- `/api/v1/history/stats/overview` - Usage statistics
- `/status/{job_id}` - Generation job status

### Logging
Logs are written to:
- Console (development)
- File: `logs/app.log` (production)
- External services (configurable)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 style guide
- Add type hints
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Create an issue in the repository
4. Contact the development team

## 🔮 Roadmap

### Phase 2 Features (Coming Soon)
- Component library detection
- Multi-deployment options
- Advanced AI model integration
- Real-time collaboration
- Performance monitoring dashboard

### Phase 3 Features (Future)
- Enterprise SSO integration
- Advanced security features
- Multi-language support
- Plugin system
- Advanced analytics