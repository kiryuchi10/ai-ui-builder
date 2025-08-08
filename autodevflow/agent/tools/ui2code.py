"""
UI2Code Tool - pix2code-style React/Tailwind generation
Based on: pix2code paper and modern web development practices
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class UI2CodeGenerator:
    """
    Generate React components with Tailwind CSS from UI layout graphs
    Based on pix2code approach with modern web development practices
    """
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.component_templates = self._load_component_templates()
        self.tailwind_classes = self._load_tailwind_mappings()
    
    def _load_component_templates(self) -> Dict[str, str]:
        """Load React component templates for different UI elements"""
        return {
            "button": """
<button 
  className="{classes}"
  onClick={{handleClick}}
  {props}
>
  {text}
</button>""",
            
            "input": """
<input
  type="{input_type}"
  className="{classes}"
  placeholder="{placeholder}"
  value={{value}}
  onChange={{handleChange}}
  {props}
/>""",
            
            "card": """
<div className="{classes}">
  {children}
</div>""",
            
            "navbar": """
<nav className="{classes}">
  <div className="container mx-auto px-4">
    {children}
  </div>
</nav>""",
            
            "form": """
<form className="{classes}" onSubmit={{handleSubmit}}>
  {children}
</form>""",
            
            "text": """
<{tag} className="{classes}">
  {text}
</{tag}>""",
            
            "image": """
<img
  src="{src}"
  alt="{alt}"
  className="{classes}"
  {props}
/>""",
            
            "list": """
<ul className="{classes}">
  {items}
</ul>""",
            
            "modal": """
<div className="{overlay_classes}">
  <div className="{modal_classes}">
    {children}
  </div>
</div>"""
        }
    
    def _load_tailwind_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load Tailwind CSS class mappings for different component types"""
        return {
            "button": {
                "primary": "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded",
                "secondary": "bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded",
                "outline": "bg-transparent hover:bg-blue-500 text-blue-700 font-semibold hover:text-white py-2 px-4 border border-blue-500 hover:border-transparent rounded",
                "small": "bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-sm",
                "large": "bg-blue-500 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded text-lg"
            },
            "input": {
                "default": "shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                "error": "shadow appearance-none border border-red-500 rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline",
                "large": "shadow appearance-none border rounded w-full py-3 px-4 text-gray-700 text-lg leading-tight focus:outline-none focus:shadow-outline"
            },
            "card": {
                "default": "bg-white shadow-md rounded-lg p-6",
                "hover": "bg-white shadow-md rounded-lg p-6 hover:shadow-lg transition-shadow duration-300",
                "bordered": "bg-white border border-gray-200 rounded-lg p-6"
            },
            "navbar": {
                "default": "bg-white shadow-lg",
                "dark": "bg-gray-800 shadow-lg",
                "transparent": "bg-transparent"
            },
            "text": {
                "heading": "text-2xl font-bold text-gray-900",
                "subheading": "text-xl font-semibold text-gray-800",
                "body": "text-base text-gray-700",
                "caption": "text-sm text-gray-500"
            }
        }
    
    async def execute(self, layout_graph: Optional[Dict] = None, style_prefs: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute UI code generation from layout graph
        
        Args:
            layout_graph: Hierarchical layout from vision detection + OCR
            style_prefs: Style preferences (theme, framework, etc.)
            
        Returns:
            Dict with generated React components and metadata
        """
        # If no layout_graph provided, try to build from kwargs
        if not layout_graph and "components" in kwargs:
            layout_graph = self.build_layout_graph(kwargs["components"], kwargs.get("text_regions", []))
        
        return self.generate_react_components(layout_graph, style_prefs or {})
    
    def build_layout_graph(self, components: List[Dict], text_regions: List[Dict]) -> Dict[str, Any]:
        """
        Build hierarchical layout graph from detected components and text
        
        Args:
            components: List of detected UI components
            text_regions: List of detected text regions
            
        Returns:
            Hierarchical layout graph
        """
        try:
            # Merge text with components
            enriched_components = self._merge_text_with_components(components, text_regions)
            
            # Build hierarchy based on spatial relationships
            hierarchy = self._build_spatial_hierarchy(enriched_components)
            
            # Infer layout patterns
            layout_patterns = self._infer_layout_patterns(hierarchy)
            
            return {
                "components": enriched_components,
                "hierarchy": hierarchy,
                "layout_patterns": layout_patterns,
                "metadata": {
                    "total_components": len(enriched_components),
                    "layout_type": self._classify_layout_type(hierarchy)
                }
            }
            
        except Exception as e:
            logger.error(f"Layout graph building failed: {e}")
            return {"components": [], "hierarchy": {}, "layout_patterns": {}}
    
    def generate_react_components(self, layout_graph: Dict, style_prefs: Dict) -> Dict[str, Any]:
        """
        Generate React components from layout graph
        
        Returns:
            {
                "components": {
                    "App.jsx": "...",
                    "components/Button.jsx": "...",
                    "components/Form.jsx": "..."
                },
                "styles": {
                    "index.css": "...",
                    "tailwind.config.js": "..."
                },
                "package_json": {...},
                "metadata": {...}
            }
        """
        try:
            # Generate main App component
            app_component = self._generate_app_component(layout_graph, style_prefs)
            
            # Generate individual components
            individual_components = self._generate_individual_components(layout_graph, style_prefs)
            
            # Generate styles
            styles = self._generate_styles(style_prefs)
            
            # Generate package.json
            package_json = self._generate_package_json()
            
            # Generate additional files
            additional_files = self._generate_additional_files()
            
            return {
                "components": {
                    "src/App.jsx": app_component,
                    **individual_components
                },
                "styles": styles,
                "package.json": package_json,
                "additional_files": additional_files,
                "metadata": {
                    "framework": "React",
                    "styling": "Tailwind CSS",
                    "components_count": len(individual_components) + 1,
                    "features": self._extract_features(layout_graph)
                }
            }
            
        except Exception as e:
            logger.error(f"React component generation failed: {e}")
            return {
                "components": {"src/App.jsx": self._generate_fallback_app()},
                "styles": {},
                "package.json": {},
                "error": str(e)
            }
    
    def _merge_text_with_components(self, components: List[Dict], text_regions: List[Dict]) -> List[Dict]:
        """Merge detected text with UI components"""
        enriched = []
        
        for component in components:
            comp_bbox = component["bbox"]
            component_text = []
            
            # Find text regions that overlap with this component
            for text_region in text_regions:
                text_bbox = text_region["bbox"]
                
                if self._bbox_contains(comp_bbox, text_bbox) or self._bbox_overlap(comp_bbox, text_bbox) > 0.5:
                    component_text.append(text_region)
            
            # Enrich component with text information
            enriched_component = component.copy()
            enriched_component["text_content"] = component_text
            enriched_component["primary_text"] = self._get_primary_text(component_text)
            enriched_component["inferred_purpose"] = self._infer_component_purpose(component, component_text)
            
            enriched.append(enriched_component)
        
        return enriched
    
    def _build_spatial_hierarchy(self, components: List[Dict]) -> Dict[str, Any]:
        """Build spatial hierarchy of components"""
        # Sort components by area (largest first for containers)
        sorted_components = sorted(components, key=lambda c: c["bbox"][2] * c["bbox"][3], reverse=True)
        
        hierarchy = {"root": {"children": [], "component": None}}
        
        for component in sorted_components:
            # Find parent container
            parent = self._find_parent_container(component, sorted_components)
            
            if parent:
                if "children" not in parent:
                    parent["children"] = []
                parent["children"].append(component)
            else:
                hierarchy["root"]["children"].append(component)
        
        return hierarchy
    
    def _generate_app_component(self, layout_graph: Dict, style_prefs: Dict) -> str:
        """Generate main App.jsx component"""
        theme = style_prefs.get("theme", "light")
        
        # Determine layout structure
        layout_type = layout_graph.get("metadata", {}).get("layout_type", "simple")
        
        if layout_type == "dashboard":
            return self._generate_dashboard_app(layout_graph, theme)
        elif layout_type == "form":
            return self._generate_form_app(layout_graph, theme)
        elif layout_type == "landing":
            return self._generate_landing_app(layout_graph, theme)
        else:
            return self._generate_simple_app(layout_graph, theme)
    
    def _generate_simple_app(self, layout_graph: Dict, theme: str) -> str:
        """Generate simple App component"""
        components = layout_graph.get("components", [])
        
        # Generate JSX for each component
        jsx_elements = []
        for component in components:
            jsx = self._component_to_jsx(component, theme)
            jsx_elements.append(jsx)
        
        app_template = f"""import React, {{ useState }} from 'react';
import './App.css';

function App() {{
  const [formData, setFormData] = useState({{}});
  
  const handleInputChange = (e) => {{
    setFormData({{
      ...formData,
      [e.target.name]: e.target.value
    }});
  }};
  
  const handleSubmit = (e) => {{
    e.preventDefault();
    console.log('Form submitted:', formData);
  }};
  
  const handleClick = (action) => {{
    console.log('Button clicked:', action);
  }};

  return (
    <div className="{"min-h-screen bg-gray-50" if theme == "light" else "min-h-screen bg-gray-900"}">
      <div className="container mx-auto px-4 py-8">
        {chr(10).join(jsx_elements)}
      </div>
    </div>
  );
}}

export default App;"""
        
        return app_template
    
    def _component_to_jsx(self, component: Dict, theme: str) -> str:
        """Convert component dict to JSX string"""
        comp_type = component.get("class_label", "div")
        primary_text = component.get("primary_text", "")
        bbox = component.get("bbox", [0, 0, 100, 50])
        
        # Get appropriate template
        template = self.component_templates.get(comp_type, self.component_templates["card"])
        
        # Get Tailwind classes
        classes = self._get_tailwind_classes(comp_type, component, theme)
        
        # Fill template
        if comp_type == "button":
            return template.format(
                classes=classes,
                text=primary_text or "Button",
                props='onClick={() => handleClick("' + (primary_text or "button") + '")}'
            )
        elif comp_type == "input":
            input_type = self._infer_input_type(primary_text)
            return template.format(
                input_type=input_type,
                classes=classes,
                placeholder=primary_text or "Enter text",
                props='name="' + (primary_text.lower().replace(" ", "_") if primary_text else "input") + '"'
            )
        elif comp_type == "text":
            tag = self._infer_text_tag(component)
            return template.format(
                tag=tag,
                classes=classes,
                text=primary_text or "Text content"
            )
        else:
            return f'<div className="{classes}">{primary_text or "Content"}</div>'
    
    def _get_tailwind_classes(self, comp_type: str, component: Dict, theme: str) -> str:
        """Get appropriate Tailwind classes for component"""
        base_classes = self.tailwind_classes.get(comp_type, {})
        
        # Determine variant based on component properties
        if comp_type == "button":
            if "primary" in component.get("primary_text", "").lower():
                return base_classes.get("primary", base_classes.get("default", ""))
            else:
                return base_classes.get("secondary", base_classes.get("default", ""))
        
        elif comp_type == "input":
            return base_classes.get("default", "")
        
        elif comp_type == "card":
            return base_classes.get("hover", base_classes.get("default", ""))
        
        elif comp_type == "text":
            text_content = component.get("primary_text", "")
            if len(text_content) > 50:
                return base_classes.get("body", "")
            elif len(text_content) > 20:
                return base_classes.get("subheading", "")
            else:
                return base_classes.get("heading", "")
        
        # Default classes
        return "p-4 m-2"
    
    def _generate_individual_components(self, layout_graph: Dict, style_prefs: Dict) -> Dict[str, str]:
        """Generate individual reusable components"""
        components = {}
        
        # Generate common components based on detected patterns
        if self._has_form_components(layout_graph):
            components["src/components/ContactForm.jsx"] = self._generate_form_component(layout_graph, style_prefs)
        
        if self._has_navigation(layout_graph):
            components["src/components/Navigation.jsx"] = self._generate_navigation_component(layout_graph, style_prefs)
        
        if self._has_cards(layout_graph):
            components["src/components/Card.jsx"] = self._generate_card_component(style_prefs)
        
        return components
    
    def _generate_form_component(self, layout_graph: Dict, style_prefs: Dict) -> str:
        """Generate a form component"""
        form_fields = self._extract_form_fields(layout_graph)
        
        fields_jsx = []
        for field in form_fields:
            field_jsx = f"""
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2">
            {field['label']}
          </label>
          <input
            type="{field['type']}"
            name="{field['name']}"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="{field['placeholder']}"
            value={{formData.{field['name']} || ''}}
            onChange={{handleInputChange}}
          />
        </div>"""
            fields_jsx.append(field_jsx)
        
        return f"""import React from 'react';

const ContactForm = ({{ formData, handleInputChange, handleSubmit }}) => {{
  return (
    <form className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4" onSubmit={{handleSubmit}}>
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Contact Form</h2>
      {chr(10).join(fields_jsx)}
      <div className="flex items-center justify-between">
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Submit
        </button>
      </div>
    </form>
  );
}};

export default ContactForm;"""
    
    def _generate_styles(self, style_prefs: Dict) -> Dict[str, str]:
        """Generate CSS and Tailwind config"""
        return {
            "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
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
}""",
            
            "tailwind.config.js": """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""
        }
    
    def _generate_package_json(self) -> Dict[str, Any]:
        """Generate package.json for React app"""
        return {
            "name": "autodevflow-generated-app",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "^5.16.4",
                "@testing-library/react": "^13.3.0",
                "@testing-library/user-event": "^13.5.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
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
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
    
    def _generate_additional_files(self) -> Dict[str, str]:
        """Generate additional project files"""
        return {
            "public/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Generated by AutoDevFlow" />
    <title>AutoDevFlow Generated App</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>""",
            
            "src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",
            
            "README.md": """# AutoDevFlow Generated App

This React application was automatically generated from a UI screenshot using AutoDevFlow.

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner

## Features

- React 18 with functional components
- Tailwind CSS for styling
- Responsive design
- Form handling
- Modern JavaScript (ES6+)

## Getting Started

1. Install dependencies: `npm install`
2. Start development server: `npm start`
3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser

## Customization

The generated code is fully customizable. You can:
- Modify components in the `src/components/` directory
- Update styles in `src/index.css` or component files
- Add new features and functionality
- Configure Tailwind CSS in `tailwind.config.js`
"""
        }
    
    # Helper methods
    def _bbox_contains(self, container_bbox: List[int], inner_bbox: List[int]) -> bool:
        """Check if container bbox contains inner bbox"""
        cx, cy, cw, ch = container_bbox
        ix, iy, iw, ih = inner_bbox
        
        return (cx <= ix and cy <= iy and 
                cx + cw >= ix + iw and cy + ch >= iy + ih)
    
    def _bbox_overlap(self, bbox1: List[int], bbox2: List[int]) -> float:
        """Calculate overlap ratio between bboxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _get_primary_text(self, text_content: List[Dict]) -> str:
        """Get primary text from text regions"""
        if not text_content:
            return ""
        
        # Sort by confidence and length
        sorted_text = sorted(text_content, 
                           key=lambda t: (t.get("confidence", 0), len(t.get("text", ""))), 
                           reverse=True)
        
        return sorted_text[0].get("text", "") if sorted_text else ""
    
    def _infer_component_purpose(self, component: Dict, text_content: List[Dict]) -> str:
        """Infer component purpose from visual and text cues"""
        comp_type = component.get("class_label", "")
        primary_text = self._get_primary_text(text_content).lower()
        
        if comp_type == "button":
            if any(word in primary_text for word in ["submit", "send", "save"]):
                return "form_submit"
            elif any(word in primary_text for word in ["login", "sign in"]):
                return "auth_login"
            elif any(word in primary_text for word in ["register", "sign up"]):
                return "auth_register"
            else:
                return "action_button"
        
        elif comp_type == "input":
            if any(word in primary_text for word in ["email", "mail"]):
                return "email_input"
            elif any(word in primary_text for word in ["password", "pass"]):
                return "password_input"
            elif any(word in primary_text for word in ["name", "username"]):
                return "name_input"
            else:
                return "text_input"
        
        return "general"
    
    def _classify_layout_type(self, hierarchy: Dict) -> str:
        """Classify overall layout type"""
        components = hierarchy.get("root", {}).get("children", [])
        
        # Count component types
        type_counts = {}
        for comp in components:
            comp_type = comp.get("class_label", "unknown")
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1
        
        # Classify based on component distribution
        if type_counts.get("input", 0) >= 2 and type_counts.get("button", 0) >= 1:
            return "form"
        elif type_counts.get("navbar", 0) >= 1 and type_counts.get("card", 0) >= 2:
            return "dashboard"
        elif type_counts.get("card", 0) >= 3:
            return "landing"
        else:
            return "simple"
    
    def _generate_fallback_app(self) -> str:
        """Generate fallback App component when generation fails"""
        return """import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Generated App
        </h1>
        <p className="text-lg text-gray-600">
          This app was generated by AutoDevFlow
        </p>
      </div>
    </div>
  );
}

export default App;"""
    
    # Additional helper methods for component generation
    def _has_form_components(self, layout_graph: Dict) -> bool:
        """Check if layout has form components"""
        components = layout_graph.get("components", [])
        return any(comp.get("class_label") in ["input", "button"] for comp in components)
    
    def _has_navigation(self, layout_graph: Dict) -> bool:
        """Check if layout has navigation"""
        components = layout_graph.get("components", [])
        return any(comp.get("class_label") == "navbar" for comp in components)
    
    def _has_cards(self, layout_graph: Dict) -> bool:
        """Check if layout has card components"""
        components = layout_graph.get("components", [])
        return any(comp.get("class_label") == "card" for comp in components)
    
    def _extract_form_fields(self, layout_graph: Dict) -> List[Dict]:
        """Extract form fields from layout"""
        components = layout_graph.get("components", [])
        fields = []
        
        for comp in components:
            if comp.get("class_label") == "input":
                primary_text = comp.get("primary_text", "")
                field_name = primary_text.lower().replace(" ", "_") if primary_text else f"field_{len(fields)}"
                
                fields.append({
                    "name": field_name,
                    "label": primary_text or "Field",
                    "type": self._infer_input_type(primary_text),
                    "placeholder": f"Enter {primary_text.lower()}" if primary_text else "Enter value"
                })
        
        return fields
    
    def _infer_input_type(self, text: str) -> str:
        """Infer HTML input type from text"""
        text_lower = text.lower()
        
        if "email" in text_lower or "mail" in text_lower:
            return "email"
        elif "password" in text_lower or "pass" in text_lower:
            return "password"
        elif "phone" in text_lower or "tel" in text_lower:
            return "tel"
        elif "date" in text_lower:
            return "date"
        elif "number" in text_lower or "age" in text_lower:
            return "number"
        else:
            return "text"
    
    def _infer_text_tag(self, component: Dict) -> str:
        """Infer appropriate HTML tag for text component"""
        text = component.get("primary_text", "")
        bbox = component.get("bbox", [0, 0, 100, 20])
        
        # Large text likely heading
        if bbox[3] > 30 or len(text) < 50:
            return "h2"
        # Medium text likely subheading
        elif bbox[3] > 20:
            return "h3"
        # Small text likely paragraph
        else:
            return "p"
    
    def _extract_features(self, layout_graph: Dict) -> List[str]:
        """Extract features from layout graph"""
        features = []
        components = layout_graph.get("components", [])
        
        component_types = set(comp.get("class_label") for comp in components)
        
        if "input" in component_types and "button" in component_types:
            features.append("forms")
        if "navbar" in component_types:
            features.append("navigation")
        if "card" in component_types:
            features.append("cards")
        if "image" in component_types:
            features.append("images")
        if "list" in component_types:
            features.append("lists")
        
        return features