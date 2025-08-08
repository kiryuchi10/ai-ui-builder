"""
Documentation Generation Tool - API spec to natural language docs
Based on: Natural Language Sentence Generation from API Spec paper
"""
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import re

logger = logging.getLogger(__name__)

class DocumentationGenerator:
    """
    Generate natural language documentation from API specifications
    """
    
    def __init__(self):
        self.doc_templates = self._load_doc_templates()
        self.example_generators = self._load_example_generators()
    
    def _load_doc_templates(self) -> Dict[str, str]:
        """Load documentation templates"""
        return {
            "api_overview": """# {title}

{description}

## Base URL
```
{base_url}
```

## Authentication
{auth_description}

## Endpoints

{endpoints_summary}

## Models

{models_summary}
""",
            
            "endpoint_detail": """### {method} {path}

{description}

**Parameters:**
{parameters}

**Request Body:**
{request_body}

**Response:**
{response_schema}

**Example:**
{example}

---
""",
            
            "model_detail": """### {model_name}

{description}

**Properties:**
{properties}

**Example:**
```json
{example}
```

---
""",
            
            "getting_started": """# Getting Started

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Visit the interactive API docs:
```
http://localhost:8000/docs
```

## Authentication

{auth_guide}

## Basic Usage

{usage_examples}
""",
            
            "readme": """# {project_name}

{description}

## Features

{features}

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

## API Documentation

The API provides the following endpoints:

{endpoints_list}

For detailed API documentation, visit `/docs` when the server is running.

## Usage Examples

{usage_examples}

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
flake8 .
black .
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License.
"""
        }
    
    def _load_example_generators(self) -> Dict[str, Any]:
        """Load example generators for different data types"""
        return {
            "string": lambda: "example string",
            "integer": lambda: 42,
            "number": lambda: 3.14,
            "boolean": lambda: True,
            "array": lambda item_type: [self._generate_example_value(item_type)],
            "object": lambda properties: {
                key: self._generate_example_value(prop.get("type", "string"))
                for key, prop in properties.items()
            }
        }
    
    async def execute(self, openapi_spec: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Execute documentation generation
        
        Args:
            openapi_spec: OpenAPI specification dict
            
        Returns:
            Dict with generated documentation files
        """
        if not openapi_spec:
            # Try to find OpenAPI spec in kwargs or generate from code
            openapi_spec = kwargs.get("openapi_spec") or self._extract_openapi_from_code(kwargs)
        
        return self.generate_documentation(openapi_spec)
    
    def generate_documentation(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive documentation from OpenAPI spec
        
        Returns:
            {
                "README.md": "...",
                "API_DOCS.md": "...",
                "GETTING_STARTED.md": "...",
                "examples/": {...},
                "postman_collection.json": {...}
            }
        """
        try:
            if not openapi_spec:
                return self._generate_fallback_docs()
            
            # Generate main documentation files
            docs = {}
            
            # README.md
            docs["README.md"] = self._generate_readme(openapi_spec)
            
            # API Documentation
            docs["API_DOCS.md"] = self._generate_api_docs(openapi_spec)
            
            # Getting Started Guide
            docs["GETTING_STARTED.md"] = self._generate_getting_started(openapi_spec)
            
            # Code examples
            examples = self._generate_code_examples(openapi_spec)
            for filename, content in examples.items():
                docs[f"examples/{filename}"] = content
            
            # Postman collection
            docs["postman_collection.json"] = self._generate_postman_collection(openapi_spec)
            
            # OpenAPI spec file
            docs["openapi.json"] = json.dumps(openapi_spec, indent=2)
            docs["openapi.yaml"] = yaml.dump(openapi_spec, default_flow_style=False)
            
            return {
                **docs,
                "metadata": {
                    "generator": "AutoDevFlow Documentation Generator",
                    "endpoints_count": len(openapi_spec.get("paths", {})),
                    "models_count": len(openapi_spec.get("components", {}).get("schemas", {}))
                }
            }
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return {
                "README.md": self._generate_fallback_readme(),
                "error": str(e)
            }
    
    def _generate_readme(self, spec: Dict[str, Any]) -> str:
        """Generate README.md"""
        info = spec.get("info", {})
        paths = spec.get("paths", {})
        
        # Extract features
        features = self._extract_features(spec)
        
        # Generate endpoints list
        endpoints_list = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    summary = details.get("summary", f"{method.upper()} {path}")
                    endpoints_list.append(f"- `{method.upper()} {path}` - {summary}")
        
        # Generate usage examples
        usage_examples = self._generate_usage_examples(spec)
        
        return self.doc_templates["readme"].format(
            project_name=info.get("title", "Generated API"),
            description=info.get("description", "API generated by AutoDevFlow"),
            features="\n".join(f"- {feature}" for feature in features),
            endpoints_list="\n".join(endpoints_list),
            usage_examples=usage_examples
        )
    
    def _generate_api_docs(self, spec: Dict[str, Any]) -> str:
        """Generate detailed API documentation"""
        info = spec.get("info", {})
        servers = spec.get("servers", [{"url": "http://localhost:8000"}])
        paths = spec.get("paths", {})
        components = spec.get("components", {})
        
        # Generate endpoints documentation
        endpoints_docs = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint_doc = self._generate_endpoint_doc(method, path, details, components)
                    endpoints_docs.append(endpoint_doc)
        
        # Generate models documentation
        models_docs = []
        schemas = components.get("schemas", {})
        for model_name, schema in schemas.items():
            model_doc = self._generate_model_doc(model_name, schema)
            models_docs.append(model_doc)
        
        # Generate authentication documentation
        auth_description = self._generate_auth_description(spec)
        
        return self.doc_templates["api_overview"].format(
            title=info.get("title", "API Documentation"),
            description=info.get("description", "Generated API documentation"),
            base_url=servers[0]["url"],
            auth_description=auth_description,
            endpoints_summary="\n".join(endpoints_docs),
            models_summary="\n".join(models_docs)
        )
    
    def _generate_endpoint_doc(self, method: str, path: str, details: Dict, components: Dict) -> str:
        """Generate documentation for a single endpoint"""
        # Parameters
        parameters = details.get("parameters", [])
        params_doc = self._format_parameters(parameters)
        
        # Request body
        request_body = details.get("requestBody", {})
        request_doc = self._format_request_body(request_body, components)
        
        # Response
        responses = details.get("responses", {})
        response_doc = self._format_responses(responses, components)
        
        # Example
        example = self._generate_endpoint_example(method, path, details, components)
        
        return self.doc_templates["endpoint_detail"].format(
            method=method.upper(),
            path=path,
            description=details.get("summary", "") or details.get("description", ""),
            parameters=params_doc,
            request_body=request_doc,
            response_schema=response_doc,
            example=example
        )
    
    def _format_parameters(self, parameters: List[Dict]) -> str:
        """Format parameters documentation"""
        if not parameters:
            return "None"
        
        param_docs = []
        for param in parameters:
            param_type = param.get("schema", {}).get("type", "string")
            required = " (required)" if param.get("required", False) else " (optional)"
            description = param.get("description", "")
            
            param_docs.append(f"- `{param['name']}` ({param_type}){required}: {description}")
        
        return "\n".join(param_docs)
    
    def _format_request_body(self, request_body: Dict, components: Dict) -> str:
        """Format request body documentation"""
        if not request_body:
            return "None"
        
        content = request_body.get("content", {})
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return self._format_schema(schema, components)
        
        return "Request body required"
    
    def _format_responses(self, responses: Dict, components: Dict) -> str:
        """Format responses documentation"""
        if not responses:
            return "No response schema defined"
        
        response_docs = []
        for status_code, response in responses.items():
            description = response.get("description", "")
            content = response.get("content", {})
            
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
                schema_doc = self._format_schema(schema, components)
                response_docs.append(f"**{status_code}**: {description}\n{schema_doc}")
            else:
                response_docs.append(f"**{status_code}**: {description}")
        
        return "\n\n".join(response_docs)
    
    def _format_schema(self, schema: Dict, components: Dict) -> str:
        """Format schema documentation"""
        if "$ref" in schema:
            ref_name = schema["$ref"].split("/")[-1]
            return f"See model: {ref_name}"
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            properties = schema.get("properties", {})
            if properties:
                prop_docs = []
                for prop_name, prop_schema in properties.items():
                    prop_type = prop_schema.get("type", "string")
                    prop_desc = prop_schema.get("description", "")
                    prop_docs.append(f"  - `{prop_name}` ({prop_type}): {prop_desc}")
                return "```json\n{\n" + "\n".join(prop_docs) + "\n}\n```"
        
        return f"Type: {schema_type}"
    
    def _generate_model_doc(self, model_name: str, schema: Dict) -> str:
        """Generate documentation for a data model"""
        description = schema.get("description", f"{model_name} model")
        properties = schema.get("properties", {})
        
        # Format properties
        props_doc = []
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "string")
            prop_desc = prop_schema.get("description", "")
            required = " (required)" if prop_name in schema.get("required", []) else ""
            
            props_doc.append(f"- `{prop_name}` ({prop_type}){required}: {prop_desc}")
        
        # Generate example
        example = self._generate_model_example(schema)
        
        return self.doc_templates["model_detail"].format(
            model_name=model_name,
            description=description,
            properties="\n".join(props_doc) if props_doc else "No properties defined",
            example=json.dumps(example, indent=2)
        )
    
    def _generate_getting_started(self, spec: Dict[str, Any]) -> str:
        """Generate getting started guide"""
        # Generate authentication guide
        auth_guide = self._generate_auth_guide(spec)
        
        # Generate usage examples
        usage_examples = self._generate_usage_examples(spec)
        
        return self.doc_templates["getting_started"].format(
            auth_guide=auth_guide,
            usage_examples=usage_examples
        )
    
    def _generate_auth_description(self, spec: Dict[str, Any]) -> str:
        """Generate authentication description"""
        components = spec.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        
        if not security_schemes:
            return "No authentication required"
        
        auth_docs = []
        for scheme_name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")
            
            if scheme_type == "http" and scheme.get("scheme") == "bearer":
                auth_docs.append("**Bearer Token**: Include `Authorization: Bearer <token>` header")
            elif scheme_type == "apiKey":
                location = scheme.get("in", "header")
                name = scheme.get("name", "api_key")
                auth_docs.append(f"**API Key**: Include `{name}` in {location}")
            else:
                auth_docs.append(f"**{scheme_name}**: {scheme_type} authentication")
        
        return "\n".join(auth_docs)
    
    def _generate_auth_guide(self, spec: Dict[str, Any]) -> str:
        """Generate detailed authentication guide"""
        components = spec.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        
        if not security_schemes:
            return "This API does not require authentication."
        
        guides = []
        for scheme_name, scheme in security_schemes.items():
            if scheme.get("type") == "http" and scheme.get("scheme") == "bearer":
                guides.append("""
### Bearer Token Authentication

1. Obtain a token by calling the login endpoint:
```bash
curl -X POST http://localhost:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "password"}'
```

2. Include the token in subsequent requests:
```bash
curl -H "Authorization: Bearer <your-token>" \\
  http://localhost:8000/api/protected-endpoint
```
""")
        
        return "\n".join(guides) if guides else "Authentication details not available."
    
    def _generate_usage_examples(self, spec: Dict[str, Any]) -> str:
        """Generate usage examples"""
        paths = spec.get("paths", {})
        examples = []
        
        # Find a few representative endpoints
        example_endpoints = list(paths.items())[:3]
        
        for path, methods in example_endpoints:
            for method, details in methods.items():
                if method.upper() in ["GET", "POST"]:
                    example = self._generate_curl_example(method, path, details)
                    examples.append(example)
                    break  # One example per path
        
        return "\n\n".join(examples) if examples else "No examples available."
    
    def _generate_curl_example(self, method: str, path: str, details: Dict) -> str:
        """Generate curl example for an endpoint"""
        method_upper = method.upper()
        summary = details.get("summary", f"{method_upper} {path}")
        
        curl_parts = [f"curl -X {method_upper}"]
        
        # Add headers
        if details.get("requestBody"):
            curl_parts.append('-H "Content-Type: application/json"')
        
        # Add auth header if needed
        if details.get("security"):
            curl_parts.append('-H "Authorization: Bearer <your-token>"')
        
        # Add request body for POST/PUT
        if method_upper in ["POST", "PUT"] and details.get("requestBody"):
            example_body = self._generate_request_body_example(details["requestBody"])
            curl_parts.append(f"-d '{json.dumps(example_body)}'")
        
        # Add URL
        curl_parts.append(f"http://localhost:8000{path}")
        
        curl_command = " \\\n  ".join(curl_parts)
        
        return f"### {summary}\n\n```bash\n{curl_command}\n```"
    
    def _generate_code_examples(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate code examples in different languages"""
        examples = {}
        
        # Python example
        examples["python_client.py"] = self._generate_python_client(spec)
        
        # JavaScript example
        examples["javascript_client.js"] = self._generate_javascript_client(spec)
        
        # Postman collection
        examples["test_requests.http"] = self._generate_http_file(spec)
        
        return examples
    
    def _generate_python_client(self, spec: Dict[str, Any]) -> str:
        """Generate Python client example"""
        info = spec.get("info", {})
        paths = spec.get("paths", {})
        
        # Find auth endpoint
        auth_endpoint = None
        for path, methods in paths.items():
            if "login" in path.lower() and "post" in methods:
                auth_endpoint = path
                break
        
        client_code = f'''"""
Python client for {info.get("title", "Generated API")}
Generated by AutoDevFlow
"""

import requests
import json

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def login(self, email, password):
        """Authenticate and store token"""
        response = self.session.post(
            f"{{self.base_url}}{auth_endpoint or "/api/auth/login"}",
            json={{"email": email, "password": password}}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.session.headers.update({{"Authorization": f"Bearer {{self.token}}"}})
            return True
        return False
'''
        
        # Add method examples for main endpoints
        for path, methods in list(paths.items())[:3]:
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE"]:
                    method_name = self._path_to_method_name(method, path)
                    client_code += f'''
    def {method_name}(self, **kwargs):
        """
        {details.get("summary", f"{method.upper()} {path}")}
        """
        response = self.session.{method}(
            f"{{self.base_url}}{path}",
            json=kwargs if kwargs else None
        )
        return response.json() if response.status_code < 400 else None
'''
        
        client_code += '''

# Example usage
if __name__ == "__main__":
    client = APIClient()
    
    # Login
    if client.login("user@example.com", "password"):
        print("Login successful")
        
        # Make API calls
        # result = client.some_method()
        # print(result)
    else:
        print("Login failed")
'''
        
        return client_code
    
    def _generate_javascript_client(self, spec: Dict[str, Any]) -> str:
        """Generate JavaScript client example"""
        info = spec.get("info", {})
        
        return f'''/**
 * JavaScript client for {info.get("title", "Generated API")}
 * Generated by AutoDevFlow
 */

class APIClient {{
    constructor(baseURL = 'http://localhost:8000') {{
        this.baseURL = baseURL;
        this.token = null;
    }}

    async login(email, password) {{
        try {{
            const response = await fetch(`${{this.baseURL}}/api/auth/login`, {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                }},
                body: JSON.stringify({{ email, password }})
            }});

            if (response.ok) {{
                const data = await response.json();
                this.token = data.access_token;
                return true;
            }}
            return false;
        }} catch (error) {{
            console.error('Login error:', error);
            return false;
        }}
    }}

    async request(endpoint, options = {{}}) {{
        const url = `${{this.baseURL}}${{endpoint}}`;
        const headers = {{
            'Content-Type': 'application/json',
            ...options.headers
        }};

        if (this.token) {{
            headers.Authorization = `Bearer ${{this.token}}`;
        }}

        try {{
            const response = await fetch(url, {{
                ...options,
                headers
            }});

            if (response.ok) {{
                return await response.json();
            }} else {{
                throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
            }}
        }} catch (error) {{
            console.error('API request error:', error);
            throw error;
        }}
    }}
}}

// Example usage
const client = new APIClient();

async function example() {{
    try {{
        // Login
        const loginSuccess = await client.login('user@example.com', 'password');
        
        if (loginSuccess) {{
            console.log('Login successful');
            
            // Make API calls
            // const result = await client.request('/api/some-endpoint');
            // console.log(result);
        }} else {{
            console.log('Login failed');
        }}
    }} catch (error) {{
        console.error('Error:', error);
    }}
}}

// Uncomment to run example
// example();
'''
    
    def _generate_postman_collection(self, spec: Dict[str, Any]) -> str:
        """Generate Postman collection"""
        info = spec.get("info", {})
        paths = spec.get("paths", {})
        
        collection = {
            "info": {
                "name": info.get("title", "Generated API"),
                "description": info.get("description", "Generated by AutoDevFlow"),
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    item = {
                        "name": details.get("summary", f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "header": [
                                {
                                    "key": "Content-Type",
                                    "value": "application/json"
                                }
                            ],
                            "url": {
                                "raw": f"{{{{base_url}}}}{path}",
                                "host": ["{{base_url}}"],
                                "path": path.strip("/").split("/")
                            }
                        }
                    }
                    
                    # Add auth header if needed
                    if details.get("security"):
                        item["request"]["header"].append({
                            "key": "Authorization",
                            "value": "Bearer {{token}}"
                        })
                    
                    # Add request body for POST/PUT
                    if method.upper() in ["POST", "PUT"] and details.get("requestBody"):
                        example_body = self._generate_request_body_example(details["requestBody"])
                        item["request"]["body"] = {
                            "mode": "raw",
                            "raw": json.dumps(example_body, indent=2)
                        }
                    
                    collection["item"].append(item)
        
        # Add variables
        collection["variable"] = [
            {
                "key": "base_url",
                "value": "http://localhost:8000"
            },
            {
                "key": "token",
                "value": "your-auth-token-here"
            }
        ]
        
        return json.dumps(collection, indent=2)
    
    def _generate_http_file(self, spec: Dict[str, Any]) -> str:
        """Generate .http file for VS Code REST Client"""
        paths = spec.get("paths", {})
        http_requests = []
        
        http_requests.append("### Variables")
        http_requests.append("@baseUrl = http://localhost:8000")
        http_requests.append("@token = your-auth-token-here")
        http_requests.append("")
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE"]:
                    summary = details.get("summary", f"{method.upper()} {path}")
                    
                    http_requests.append(f"### {summary}")
                    http_requests.append(f"{method.upper()} {{{{baseUrl}}}}{path}")
                    
                    if details.get("security"):
                        http_requests.append("Authorization: Bearer {{token}}")
                    
                    if method.upper() in ["POST", "PUT"] and details.get("requestBody"):
                        http_requests.append("Content-Type: application/json")
                        http_requests.append("")
                        example_body = self._generate_request_body_example(details["requestBody"])
                        http_requests.append(json.dumps(example_body, indent=2))
                    
                    http_requests.append("")
        
        return "\n".join(http_requests)
    
    # Helper methods
    def _extract_features(self, spec: Dict[str, Any]) -> List[str]:
        """Extract features from OpenAPI spec"""
        features = []
        paths = spec.get("paths", {})
        components = spec.get("components", {})
        
        # Check for authentication
        if components.get("securitySchemes"):
            features.append("Authentication & Authorization")
        
        # Check for CRUD operations
        methods = set()
        for path_methods in paths.values():
            methods.update(path_methods.keys())
        
        if "post" in methods:
            features.append("Create operations")
        if "get" in methods:
            features.append("Read operations")
        if "put" in methods or "patch" in methods:
            features.append("Update operations")
        if "delete" in methods:
            features.append("Delete operations")
        
        # Check for file uploads
        for path_methods in paths.values():
            for method_details in path_methods.values():
                if isinstance(method_details, dict):
                    request_body = method_details.get("requestBody", {})
                    content = request_body.get("content", {})
                    if "multipart/form-data" in content:
                        features.append("File upload support")
                        break
        
        # Check for WebSocket
        if any("websocket" in str(path).lower() for path in paths.keys()):
            features.append("WebSocket support")
        
        return features
    
    def _generate_example_value(self, schema_type: str) -> Any:
        """Generate example value for schema type"""
        generators = {
            "string": lambda: "example string",
            "integer": lambda: 42,
            "number": lambda: 3.14,
            "boolean": lambda: True,
            "array": lambda: ["item1", "item2"],
            "object": lambda: {"key": "value"}
        }
        
        return generators.get(schema_type, lambda: "example")()
    
    def _generate_model_example(self, schema: Dict) -> Dict[str, Any]:
        """Generate example for a model schema"""
        if schema.get("type") != "object":
            return self._generate_example_value(schema.get("type", "string"))
        
        properties = schema.get("properties", {})
        example = {}
        
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get("type", "string")
            
            if prop_type == "array":
                items = prop_schema.get("items", {})
                item_type = items.get("type", "string")
                example[prop_name] = [self._generate_example_value(item_type)]
            elif prop_type == "object":
                example[prop_name] = self._generate_model_example(prop_schema)
            else:
                example[prop_name] = self._generate_example_value(prop_type)
        
        return example
    
    def _generate_request_body_example(self, request_body: Dict) -> Dict[str, Any]:
        """Generate example request body"""
        content = request_body.get("content", {})
        
        if "application/json" in content:
            schema = content["application/json"].get("schema", {})
            return self._generate_model_example(schema)
        
        return {"example": "data"}
    
    def _generate_endpoint_example(self, method: str, path: str, details: Dict, components: Dict) -> str:
        """Generate complete endpoint example"""
        curl_parts = [f"curl -X {method.upper()}"]
        
        # Add headers
        if details.get("requestBody"):
            curl_parts.append('-H "Content-Type: application/json"')
        
        if details.get("security"):
            curl_parts.append('-H "Authorization: Bearer <your-token>"')
        
        # Add request body
        if method.upper() in ["POST", "PUT"] and details.get("requestBody"):
            example_body = self._generate_request_body_example(details["requestBody"])
            curl_parts.append(f"-d '{json.dumps(example_body)}'")
        
        # Add URL
        curl_parts.append(f"http://localhost:8000{path}")
        
        return "```bash\n" + " \\\n  ".join(curl_parts) + "\n```"
    
    def _path_to_method_name(self, method: str, path: str) -> str:
        """Convert path to method name"""
        # Remove path parameters and convert to snake_case
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        clean_path = clean_path.strip('/').replace('/', '_').replace('-', '_')
        
        if not clean_path:
            clean_path = "root"
        
        return f"{method}_{clean_path}"
    
    def _extract_openapi_from_code(self, kwargs: Dict) -> Dict[str, Any]:
        """Extract OpenAPI spec from generated code (fallback)"""
        # This would analyze generated FastAPI code to extract spec
        # For now, return a minimal spec
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "Generated API",
                "version": "1.0.0",
                "description": "API generated by AutoDevFlow"
            },
            "paths": {},
            "components": {"schemas": {}}
        }
    
    def _generate_fallback_docs(self) -> Dict[str, str]:
        """Generate fallback documentation when no spec is available"""
        return {
            "README.md": self._generate_fallback_readme(),
            "API_DOCS.md": "# API Documentation\n\nDocumentation will be generated when OpenAPI spec is available.",
            "metadata": {"status": "fallback"}
        }
    
    def _generate_fallback_readme(self) -> str:
        """Generate fallback README"""
        return """# Generated API

This API was generated by AutoDevFlow Orchestrator.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

3. Visit the interactive API docs:
```
http://localhost:8000/docs
```

## Features

- RESTful API endpoints
- Interactive documentation
- JSON request/response format
- Error handling

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
flake8 .
black .
```

For detailed API documentation, visit `/docs` when the server is running.
"""