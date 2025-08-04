# 🚀 Advanced AI-Powered UI Builder - Usage Guide

## Quick Start

### Option 1: One-Command Setup (Recommended)
```bash
cd ai-ui-builder
python quick_start_advanced.py
```

### Option 2: Manual Setup
```bash
# 1. Run setup
python setup_advanced_features.py

# 2. Configure environment
cp backend/.env.template backend/.env
cp frontend/.env.template frontend/.env
# Edit .env files with your API keys

# 3. Run DeepSeek implementation
python deepseek_agent_runner.py

# 4. Start services
docker-compose -f docker-compose.advanced.yml up
```

---

## 🔑 Required API Keys

### Essential Keys
- **DEEPSEEK_API_KEY**: Get from [DeepSeek Platform](https://platform.deepseek.com)
- **FIGMA_TOKEN**: Generate from [Figma Settings](https://www.figma.com/developers/api#access-tokens)
- **GITHUB_TOKEN**: Create from [GitHub Settings](https://github.com/settings/tokens)

### Deployment Keys (Optional)
- **RENDER_API_KEY**: From [Render Dashboard](https://dashboard.render.com/account/api-keys)
- **VERCEL_TOKEN**: From [Vercel Settings](https://vercel.com/account/tokens)
- **NETLIFY_TOKEN**: From [Netlify Settings](https://app.netlify.com/user/applications#personal-access-tokens)

---

## 🎯 Feature Usage Guide

### 🔁 1. Prompt Memory + Context Awareness

**What it does**: Tracks your previous prompts and allows you to reuse and iterate on them.

**How to use**:
1. Open the UI Builder interface
2. Look for the "History" dropdown in the top navigation
3. Previous prompts are automatically saved after each generation
4. Click on any previous prompt to reuse it
5. Edit and modify prompts for iterative improvements

**Example workflow**:
```
1. Generate: "Create a landing page with hero section"
2. Refine: "Add pricing section to the previous landing page"
3. Iterate: "Make the pricing section more modern with cards"
```

### 🧩 2. Component Library Detection

**What it does**: Automatically detects common UI patterns and maps them to reusable components.

**How to use**:
1. When describing your UI, use common component names
2. The system automatically detects: buttons, cards, modals, forms, navigation
3. Generated code uses pre-built, optimized components
4. View available components in the "Component Library" panel

**Example prompts**:
```
✅ Good: "Create a card with title, description, and action button"
✅ Good: "Add a modal dialog for user settings"
✅ Good: "Include a navigation bar with logo and menu items"
```

### 🌐 3. Multi-Deployment Options

**What it does**: Deploy your generated UI to different platforms with one click.

**How to use**:
1. After generating your UI, scroll to the "Deployment" section
2. Choose your target platform:
   - **Render**: Best for full-stack apps
   - **Vercel**: Optimized for React/Next.js
   - **Netlify**: Great for static sites
   - **Docker**: For containerized deployment
3. Configure environment variables if needed
4. Click "Deploy" and get your live URL

**Platform recommendations**:
- **Static landing pages**: Netlify
- **React applications**: Vercel
- **Full-stack apps**: Render
- **Enterprise/custom hosting**: Docker

### 🤖 4. LLM-based UI Validator

**What it does**: Uses DeepSeek AI to analyze your generated code for quality, accessibility, and performance.

**How to use**:
1. After code generation, click "Validate Code" in the review panel
2. Review the scores for:
   - Responsive Design (0-10)
   - Accessibility (0-10)
   - Code Quality (0-10)
   - Performance (0-10)
   - User Experience (0-10)
3. Read detailed feedback and suggestions
4. Click "Apply Improvements" to automatically fix issues

**What it checks**:
- WCAG accessibility compliance
- Mobile responsiveness
- Code structure and maintainability
- Performance optimizations
- User experience best practices

### 🧪 5. Test Coverage Generator

**What it does**: Automatically generates comprehensive Jest test cases for your React components.

**How to use**:
1. After generating a component, click "Generate Tests"
2. Review the generated test cases
3. Download the test file or copy the code
4. Tests include:
   - Component rendering
   - Props validation
   - User interactions
   - Accessibility testing
   - Error states

**Generated test types**:
```javascript
// Rendering tests
test('renders component correctly', () => {});

// Interaction tests
test('handles button click', () => {});

// Accessibility tests
test('has proper ARIA labels', () => {});

// Props tests
test('displays correct content with props', () => {});
```

### 📦 6. Export Modes

**What it does**: Export your generated UI in different formats for various use cases.

**Export options**:

#### React App Export
- Complete application with routing
- Package.json with dependencies
- Build configuration
- README with setup instructions

#### Component Library Export
- Individual reusable components
- TypeScript definitions
- Storybook stories
- Documentation

#### JSON Schema Export
- Structured UI definition
- Design system tokens
- Component specifications
- API for programmatic use

**How to use**:
1. Click "Export Options" after generation
2. Choose your export format
3. Configure export settings
4. Download the generated files

### 🎨 7. Live Figma Design Feedback Loop

**What it does**: Monitors your Figma files for changes and automatically regenerates code.

**Setup**:
1. Connect your Figma account with the token
2. Generate a UI from a Figma file
3. Enable "Live Sync" in the interface
4. Make changes to your Figma design
5. Code automatically updates within minutes

**How it works**:
- Polls Figma API every 30 seconds
- Detects changes in design files
- Regenerates affected components
- Notifies you of updates
- Maintains your custom code modifications

---

## 🛠️ Advanced Configuration

### Environment Variables

#### Backend (.env)
```bash
# Core Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_ui_builder
REDIS_URL=redis://localhost:6379/0

# AI Services
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# External APIs
FIGMA_TOKEN=your_figma_token
GITHUB_TOKEN=your_github_token
RENDER_API_KEY=your_render_key
VERCEL_TOKEN=your_vercel_token
NETLIFY_TOKEN=your_netlify_token

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Features
ENABLE_FIGMA_WATCHER=true
ENABLE_AUTO_DEPLOYMENT=true
ENABLE_CODE_VALIDATION=true
```

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENABLE_ANALYTICS=false
```

### Component Mapping Customization

Edit `backend/config/component_mapping.json` to add custom components:

```json
{
  "custom-card": {
    "template": "components/ui/CustomCard.jsx",
    "props": ["title", "content", "variant"],
    "tailwind_classes": "bg-gradient-to-r from-blue-500 to-purple-600",
    "description": "Custom gradient card component"
  }
}
```

### Database Schema

The system creates these tables:
- `prompt_history`: Stores user prompts and results
- `deployment_logs`: Tracks deployment history
- `component_library`: Custom component definitions
- `users`: User accounts and preferences

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: Invalid API key for DeepSeek
```
**Solution**: Check your `DEEPSEEK_API_KEY` in the .env file

#### 2. Database Connection Issues
```
Error: Could not connect to database
```
**Solution**: 
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in .env
- Run `docker-compose up postgres` if using Docker

#### 3. Figma Integration Issues
```
Error: Figma file not accessible
```
**Solution**:
- Verify your `FIGMA_TOKEN` has correct permissions
- Ensure the Figma file is accessible to your account
- Check if the file ID is correct

#### 4. Deployment Failures
```
Error: Deployment failed to Vercel
```
**Solution**:
- Check your deployment platform API keys
- Verify project settings and permissions
- Review deployment logs in the platform dashboard

### Performance Optimization

#### 1. Database Performance
```sql
-- Add indexes for better query performance
CREATE INDEX idx_prompt_history_user_id ON prompt_history(user_id);
CREATE INDEX idx_prompt_history_created_at ON prompt_history(created_at);
```

#### 2. Redis Configuration
```bash
# Increase Redis memory limit
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. Background Tasks
```python
# Optimize Celery worker settings
celery -A background_tasks worker --concurrency=4 --loglevel=info
```

---

## 📊 Monitoring and Analytics

### Health Checks
- Backend: `http://localhost:8000/health`
- Database: `http://localhost:8000/health/db`
- Redis: `http://localhost:8000/health/redis`

### Metrics Endpoints
- API usage: `http://localhost:8000/metrics/api`
- Generation stats: `http://localhost:8000/metrics/generation`
- Deployment stats: `http://localhost:8000/metrics/deployment`

### Logging
Logs are structured and include:
- Request/response details
- Generation performance metrics
- Error tracking with stack traces
- User activity patterns

---

## 🚀 Production Deployment

### Docker Production Setup
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d

# Scale workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

### Environment-Specific Configurations

#### Development
- Debug mode enabled
- Hot reloading
- Detailed error messages
- Local database

#### Staging
- Production-like environment
- Limited debug information
- Staging database
- Performance monitoring

#### Production
- Optimized builds
- Error tracking with Sentry
- Production database with backups
- Load balancing and scaling

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests: `pytest tests/`
5. Run linting: `black . && flake8`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Create a Pull Request

### Code Standards
- Python: Follow PEP 8, use Black formatter
- JavaScript: Use ESLint and Prettier
- Tests: Maintain >80% coverage
- Documentation: Update README and docstrings

---

## 📞 Support

### Getting Help
1. Check this usage guide
2. Review the [GitHub Issues](https://github.com/your-repo/ai-ui-builder/issues)
3. Join our [Discord Community](https://discord.gg/your-invite)
4. Email support: support@your-domain.com

### Reporting Issues
When reporting issues, include:
- Error messages and stack traces
- Steps to reproduce
- Environment details (OS, Python version, etc.)
- Configuration files (without sensitive data)

---

## 🎉 What's Next?

After mastering these features, explore:
- Custom AI model integration
- Advanced component libraries
- Team collaboration features
- Enterprise deployment options
- Custom deployment targets
- Advanced analytics and insights

Happy building! 🚀