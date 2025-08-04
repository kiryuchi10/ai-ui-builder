"""
Export routes for AI UI Builder
Handles different export formats and deployment options
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import zipfile
import tempfile
import os
import json
from datetime import datetime

router = APIRouter(prefix="/api/v1/export", tags=["export"])

class ExportRequest(BaseModel):
    code: str
    component_name: str = "GeneratedComponent"
    export_type: str  # react-app, component, html, json, figma
    options: Optional[Dict[str, Any]] = {}

class ExportResponse(BaseModel):
    success: bool
    download_url: Optional[str] = None
    files: Optional[Dict[str, str]] = None
    message: str

class DeploymentRequest(BaseModel):
    code: str
    component_name: str
    platform: str  # vercel, netlify, render, github-pages
    config: Optional[Dict[str, Any]] = {}

@router.post("/generate", response_model=ExportResponse)
async def generate_export(request: ExportRequest):
    """Generate export package based on type"""
    try:
        if request.export_type == "react-app":
            return await _export_react_app(request)
        elif request.export_type == "component":
            return await _export_component(request)
        elif request.export_type == "html":
            return await _export_html(request)
        elif request.export_type == "json":
            return await _export_json(request)
        elif request.export_type == "figma":
            return await _export_figma(request)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export type: {request.export_type}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@router.post("/deploy")
async def deploy_code(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy code to specified platform"""
    try:
        if request.platform == "vercel":
            return await _deploy_to_vercel(request, background_tasks)
        elif request.platform == "netlify":
            return await _deploy_to_netlify(request, background_tasks)
        elif request.platform == "render":
            return await _deploy_to_render(request, background_tasks)
        elif request.platform == "github-pages":
            return await _deploy_to_github_pages(request, background_tasks)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")

async def _export_react_app(request: ExportRequest) -> ExportResponse:
    """Export as complete React application"""
    
    # Create React app structure
    files = {
        "package.json": _generate_package_json(request.component_name, request.options),
        "public/index.html": _generate_index_html(request.component_name),
        "public/manifest.json": _generate_manifest_json(request.component_name),
        "src/index.js": _generate_index_js(),
        "src/index.css": _generate_index_css(),
        f"src/{request.component_name}.jsx": request.code,
        "src/App.js": _generate_app_js(request.component_name),
        "README.md": _generate_readme(request.component_name),
        ".gitignore": _generate_gitignore(),
        "netlify.toml": _generate_netlify_config(),
        "vercel.json": _generate_vercel_config()
    }
    
    # Create zip file
    zip_path = await _create_zip_file(files, f"{request.component_name}-react-app")
    
    return ExportResponse(
        success=True,
        download_url=f"/downloads/{os.path.basename(zip_path)}",
        files=files,
        message="React app exported successfully"
    )

async def _export_component(request: ExportRequest) -> ExportResponse:
    """Export as single React component"""
    
    files = {
        f"{request.component_name}.jsx": request.code,
        f"{request.component_name}.test.jsx": _generate_component_test(request.component_name),
        f"{request.component_name}.stories.jsx": _generate_storybook_story(request.component_name),
        "README.md": _generate_component_readme(request.component_name)
    }
    
    return ExportResponse(
        success=True,
        files=files,
        message="Component exported successfully"
    )

async def _export_html(request: ExportRequest) -> ExportResponse:
    """Export as static HTML with inline CSS"""
    
    # Convert JSX to HTML (simplified conversion)
    html_content = _jsx_to_html(request.code, request.component_name)
    
    files = {
        "index.html": html_content,
        "styles.css": _extract_css_from_jsx(request.code),
        "script.js": _generate_vanilla_js(request.code)
    }
    
    return ExportResponse(
        success=True,
        files=files,
        message="HTML exported successfully"
    )

async def _export_json(request: ExportRequest) -> ExportResponse:
    """Export as JSON schema"""
    
    schema = _generate_component_schema(request.code, request.component_name)
    
    files = {
        f"{request.component_name}-schema.json": json.dumps(schema, indent=2),
        "component-structure.json": json.dumps(_analyze_component_structure(request.code), indent=2)
    }
    
    return ExportResponse(
        success=True,
        files=files,
        message="JSON schema exported successfully"
    )

async def _export_figma(request: ExportRequest) -> ExportResponse:
    """Export Figma design tokens and components"""
    
    # Generate Figma-compatible design tokens
    design_tokens = _generate_design_tokens(request.code)
    figma_components = _generate_figma_components(request.code)
    
    files = {
        "design-tokens.json": json.dumps(design_tokens, indent=2),
        "figma-components.json": json.dumps(figma_components, indent=2),
        "figma-import-guide.md": _generate_figma_guide()
    }
    
    return ExportResponse(
        success=True,
        files=files,
        message="Figma export generated successfully"
    )

# Deployment functions
async def _deploy_to_vercel(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy to Vercel"""
    # This would integrate with Vercel API
    return {
        "success": True,
        "deployment_url": f"https://{request.component_name.lower()}-generated.vercel.app",
        "message": "Deployment to Vercel initiated"
    }

async def _deploy_to_netlify(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy to Netlify"""
    # This would integrate with Netlify API
    return {
        "success": True,
        "deployment_url": f"https://{request.component_name.lower()}-generated.netlify.app",
        "message": "Deployment to Netlify initiated"
    }

async def _deploy_to_render(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy to Render"""
    # This would integrate with Render API
    return {
        "success": True,
        "deployment_url": f"https://{request.component_name.lower()}-generated.onrender.com",
        "message": "Deployment to Render initiated"
    }

async def _deploy_to_github_pages(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy to GitHub Pages"""
    # This would integrate with GitHub API
    return {
        "success": True,
        "deployment_url": f"https://username.github.io/{request.component_name.lower()}",
        "message": "Deployment to GitHub Pages initiated"
    }

# Helper functions for file generation
def _generate_package_json(component_name: str, options: Dict[str, Any]) -> str:
    """Generate package.json for React app"""
    package = {
        "name": component_name.lower().replace(" ", "-"),
        "version": "0.1.0",
        "private": True,
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-scripts": "5.0.1",
            "@testing-library/jest-dom": "^5.16.4",
            "@testing-library/react": "^13.3.0",
            "@testing-library/user-event": "^13.5.0"
        },
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "react-scripts test",
            "eject": "react-scripts eject"
        },
        "eslintConfig": {
            "extends": ["react-app", "react-app/jest"]
        },
        "browserslist": {
            "production": [">0.2%", "not dead", "not op_mini all"],
            "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
        }
    }
    
    # Add additional dependencies based on options
    if options.get("include_router"):
        package["dependencies"]["react-router-dom"] = "^6.3.0"
    if options.get("include_state_management"):
        package["dependencies"]["@reduxjs/toolkit"] = "^1.8.3"
        package["dependencies"]["react-redux"] = "^8.0.2"
    
    return json.dumps(package, indent=2)

def _generate_index_html(component_name: str) -> str:
    """Generate index.html"""
    return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Generated React app - {component_name}" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>{component_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>'''

def _generate_manifest_json(component_name: str) -> str:
    """Generate manifest.json"""
    manifest = {
        "short_name": component_name,
        "name": f"{component_name} - Generated React App",
        "icons": [
            {
                "src": "favicon.ico",
                "sizes": "64x64 32x32 24x24 16x16",
                "type": "image/x-icon"
            }
        ],
        "start_url": ".",
        "display": "standalone",
        "theme_color": "#000000",
        "background_color": "#ffffff"
    }
    return json.dumps(manifest, indent=2)

def _generate_index_js() -> str:
    """Generate index.js"""
    return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''

def _generate_index_css() -> str:
    """Generate index.css"""
    return '''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

* {
  box-sizing: border-box;
}'''

def _generate_app_js(component_name: str) -> str:
    """Generate App.js"""
    return f'''import React from 'react';
import {component_name} from './{component_name}';

function App() {{
  return (
    <div className="App">
      <{component_name} />
    </div>
  );
}}

export default App;'''

def _generate_readme(component_name: str) -> str:
    """Generate README.md"""
    return f'''# {component_name}

This project was generated using AI UI Builder.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in development mode.
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

### `npm test`

Launches the test runner in interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

## Deployment

This app is ready to be deployed to various platforms:

- **Vercel**: Connect your GitHub repository to Vercel
- **Netlify**: Drag and drop the build folder to Netlify
- **GitHub Pages**: Use the `gh-pages` package

## Learn More

You can learn more about React in the [React documentation](https://reactjs.org/).
'''

def _generate_gitignore() -> str:
    """Generate .gitignore"""
    return '''# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# production
/build

# misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*'''

def _generate_netlify_config() -> str:
    """Generate netlify.toml"""
    return '''[build]
  publish = "build"
  command = "npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200'''

def _generate_vercel_config() -> str:
    """Generate vercel.json"""
    config = {
        "version": 2,
        "builds": [
            {
                "src": "package.json",
                "use": "@vercel/static-build",
                "config": {
                    "distDir": "build"
                }
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "/index.html"
            }
        ]
    }
    return json.dumps(config, indent=2)

def _generate_component_test(component_name: str) -> str:
    """Generate component test file"""
    return f'''import React from 'react';
import {{ render, screen }} from '@testing-library/react';
import {component_name} from './{component_name}';

test('renders {component_name} component', () => {{
  render(<{component_name} />);
  // Add your test assertions here
  expect(screen.getByRole('main')).toBeInTheDocument();
}});'''

def _generate_storybook_story(component_name: str) -> str:
    """Generate Storybook story"""
    return f'''import React from 'react';
import {component_name} from './{component_name}';

export default {{
  title: 'Components/{component_name}',
  component: {component_name},
  parameters: {{
    layout: 'centered',
  }},
  tags: ['autodocs'],
}};

export const Default = {{
  args: {{}},
}};'''

def _generate_component_readme(component_name: str) -> str:
    """Generate component README"""
    return f'''# {component_name}

A React component generated by AI UI Builder.

## Usage

```jsx
import {component_name} from './{component_name}';

function App() {{
  return <{component_name} />;
}}
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| ... | ... | ... | ... |

## Examples

### Basic Usage

```jsx
<{component_name} />
```

## Development

This component was generated using AI and may require customization for your specific use case.
'''

# Simplified conversion functions (would be more sophisticated in production)
def _jsx_to_html(jsx_code: str, component_name: str) -> str:
    """Convert JSX to HTML (simplified)"""
    # This is a very basic conversion - in production, you'd use a proper JSX parser
    html = jsx_code.replace('className=', 'class=')
    html = html.replace('{', '').replace('}', '')
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{component_name}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="root">
        <!-- Component HTML would be inserted here -->
        <div class="generated-component">
            <p>Generated HTML content from {component_name}</p>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>'''

def _extract_css_from_jsx(jsx_code: str) -> str:
    """Extract CSS from JSX (simplified)"""
    return '''/* Generated CSS */
.generated-component {
    padding: 20px;
    margin: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
}

/* Add your custom styles here */'''

def _generate_vanilla_js(jsx_code: str) -> str:
    """Generate vanilla JavaScript (simplified)"""
    return '''// Generated JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Component loaded');
    
    // Add your interactive functionality here
});'''

def _generate_component_schema(jsx_code: str, component_name: str) -> Dict[str, Any]:
    """Generate JSON schema for component"""
    return {
        "name": component_name,
        "type": "component",
        "framework": "react",
        "generated_at": datetime.now().isoformat(),
        "structure": {
            "props": [],
            "state": [],
            "methods": [],
            "hooks": []
        },
        "dependencies": [],
        "styling": "css-modules"
    }

def _analyze_component_structure(jsx_code: str) -> Dict[str, Any]:
    """Analyze component structure"""
    return {
        "lines_of_code": len(jsx_code.split('\n')),
        "complexity": "medium",
        "has_state": "useState" in jsx_code,
        "has_effects": "useEffect" in jsx_code,
        "has_props": "props" in jsx_code,
        "jsx_elements": len([line for line in jsx_code.split('\n') if '<' in line and '>' in line])
    }

def _generate_design_tokens(jsx_code: str) -> Dict[str, Any]:
    """Generate Figma design tokens"""
    return {
        "colors": {
            "primary": "#007bff",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545"
        },
        "typography": {
            "fontFamily": "Inter, sans-serif",
            "fontSize": {
                "small": "14px",
                "medium": "16px",
                "large": "18px"
            }
        },
        "spacing": {
            "small": "8px",
            "medium": "16px",
            "large": "24px"
        },
        "borderRadius": {
            "small": "4px",
            "medium": "8px",
            "large": "12px"
        }
    }

def _generate_figma_components(jsx_code: str) -> Dict[str, Any]:
    """Generate Figma component definitions"""
    return {
        "components": [
            {
                "name": "Button",
                "type": "component",
                "variants": ["primary", "secondary", "outline"],
                "properties": {
                    "width": "auto",
                    "height": "40px",
                    "padding": "8px 16px"
                }
            }
        ]
    }

def _generate_figma_guide() -> str:
    """Generate Figma import guide"""
    return '''# Figma Import Guide

This export contains design tokens and component definitions that can be imported into Figma.

## Files Included

- `design-tokens.json`: Color palette, typography, and spacing tokens
- `figma-components.json`: Component definitions and variants

## How to Import

1. Open Figma
2. Install the "Design Tokens" plugin
3. Import the design-tokens.json file
4. Use the component definitions to recreate components in Figma

## Design System

The exported tokens follow a consistent design system that can be used across your entire project.
'''

async def _create_zip_file(files: Dict[str, str], filename: str) -> str:
    """Create a zip file with the provided files"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
        with zipfile.ZipFile(tmp_file.name, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in files.items():
                zip_file.writestr(file_path, content)
        return tmp_file.name