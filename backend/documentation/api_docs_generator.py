"""
Automatic API Documentation Generator for AI UI Builder
Generates comprehensive API documentation with examples and interactive features
"""

import inspect
import json
import yaml
from typing import Dict, List, Any, Optional, get_type_hints
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import re
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

@dataclass
class APIEndpoint:
    """API endpoint documentation"""
    path: str
    method: str
    summary: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    tags: List[str]
    security: List[str]
    examples: List[Dict[str, Any]]

@dataclass
class APISchema:
    """API schema definition"""
    name: str
    type: str
    properties: Dict[str, Any]
    required: List[str]
    example: Dict[str, Any]

class OpenAPIGenerator:
    """Generates OpenAPI 3.0 specification"""
    
    def __init__(self, title: str, version: str, description: str):
        self.title = title
        self.version = version
        self.description = description
        self.endpoints: List[APIEndpoint] = []
        self.schemas: Dict[str, APISchema] = {}
        self.security_schemes = {}
    
    def add_endpoint(self, endpoint: APIEndpoint):
        """Add API endpoint to documentation"""
        self.endpoints.append(endpoint)
    
    def add_schema(self, schema: APISchema):
        """Add schema definition"""
        self.schemas[schema.name] = schema
    
    def add_security_scheme(self, name: str, scheme_type: str, **kwargs):
        """Add security scheme"""
        self.security_schemes[name] = {
            'type': scheme_type,
            **kwargs
        }
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate complete OpenAPI specification"""
        spec = {
            'openapi': '3.0.3',
            'info': {
                'title': self.title,
                'version': self.version,
                'description': self.description,
                'contact': {
                    'name': 'AI UI Builder Support',
                    'email': 'support@ai-ui-builder.com'
                },
                'license': {
                    'name': 'MIT',
                    'url': 'https://opensource.org/licenses/MIT'
                }
            },
            'servers': [
                {
                    'url': 'https://api.ai-ui-builder.com/v1',
                    'description': 'Production server'
                },
                {
                    'url': 'https://staging-api.ai-ui-builder.com/v1',
                    'description': 'Staging server'
                },
                {
                    'url': 'http://localhost:8000/v1',
                    'description': 'Development server'
                }
            ],
            'paths': self._generate_paths(),
            'components': {
                'schemas': self._generate_schemas(),
                'securitySchemes': self.security_schemes,
                'responses': self._generate_common_responses(),
                'parameters': self._generate_common_parameters()
            },
            'security': [
                {'BearerAuth': []},
                {'ApiKeyAuth': []}
            ],
            'tags': self._generate_tags()
        }
        
        return spec
    
    def _generate_paths(self) -> Dict[str, Any]:
        """Generate paths section"""
        paths = {}
        
        for endpoint in self.endpoints:
            if endpoint.path not in paths:
                paths[endpoint.path] = {}
            
            paths[endpoint.path][endpoint.method.lower()] = {
                'summary': endpoint.summary,
                'description': endpoint.description,
                'tags': endpoint.tags,
                'parameters': endpoint.parameters,
                'responses': endpoint.responses,
                'security': [{'BearerAuth': []}] if endpoint.security else []
            }
            
            # Add request body if present
            if endpoint.request_body:
                paths[endpoint.path][endpoint.method.lower()]['requestBody'] = endpoint.request_body
            
            # Add examples
            if endpoint.examples:
                paths[endpoint.path][endpoint.method.lower()]['examples'] = endpoint.examples
        
        return paths
    
    def _generate_schemas(self) -> Dict[str, Any]:
        """Generate schemas section"""
        schemas = {}
        
        for name, schema in self.schemas.items():
            schemas[name] = {
                'type': schema.type,
                'properties': schema.properties,
                'required': schema.required,
                'example': schema.example
            }
        
        return schemas
    
    def _generate_common_responses(self) -> Dict[str, Any]:
        """Generate common response definitions"""
        return {
            'BadRequest': {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'error': {'type': 'string'},
                                'message': {'type': 'string'},
                                'details': {'type': 'object'}
                            }
                        }
                    }
                }
            },
            'Unauthorized': {
                'description': 'Unauthorized',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'error': {'type': 'string', 'example': 'Unauthorized'},
                                'message': {'type': 'string', 'example': 'Invalid or missing authentication token'}
                            }
                        }
                    }
                }
            },
            'NotFound': {
                'description': 'Resource not found',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'error': {'type': 'string', 'example': 'Not Found'},
                                'message': {'type': 'string', 'example': 'The requested resource was not found'}
                            }
                        }
                    }
                }
            },
            'InternalServerError': {
                'description': 'Internal server error',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'error': {'type': 'string', 'example': 'Internal Server Error'},
                                'message': {'type': 'string', 'example': 'An unexpected error occurred'}
                            }
                        }
                    }
                }
            }
        }
    
    def _generate_common_parameters(self) -> Dict[str, Any]:
        """Generate common parameter definitions"""
        return {
            'PageParam': {
                'name': 'page',
                'in': 'query',
                'description': 'Page number for pagination',
                'required': False,
                'schema': {
                    'type': 'integer',
                    'minimum': 1,
                    'default': 1
                }
            },
            'LimitParam': {
                'name': 'limit',
                'in': 'query',
                'description': 'Number of items per page',
                'required': False,
                'schema': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 100,
                    'default': 20
                }
            },
            'SortParam': {
                'name': 'sort',
                'in': 'query',
                'description': 'Sort field and direction (e.g., created_at:desc)',
                'required': False,
                'schema': {
                    'type': 'string'
                }
            }
        }
    
    def _generate_tags(self) -> List[Dict[str, str]]:
        """Generate tags section"""
        tags = set()
        for endpoint in self.endpoints:
            tags.update(endpoint.tags)
        
        tag_descriptions = {
            'Authentication': 'User authentication and authorization',
            'UI Generation': 'AI-powered UI generation endpoints',
            'Projects': 'Project management operations',
            'Deployments': 'Deployment management',
            'Users': 'User management operations',
            'Organizations': 'Organization management',
            'Analytics': 'Analytics and reporting',
            'System': 'System administration endpoints'
        }
        
        return [
            {
                'name': tag,
                'description': tag_descriptions.get(tag, f'{tag} operations')
            }
            for tag in sorted(tags)
        ]

class CodeExampleGenerator:
    """Generates code examples for API endpoints"""
    
    def __init__(self):
        self.languages = ['curl', 'python', 'javascript', 'java', 'go']
    
    def generate_examples(self, endpoint: APIEndpoint) -> Dict[str, str]:
        """Generate code examples for all supported languages"""
        examples = {}
        
        for language in self.languages:
            if language == 'curl':
                examples[language] = self._generate_curl_example(endpoint)
            elif language == 'python':
                examples[language] = self._generate_python_example(endpoint)
            elif language == 'javascript':
                examples[language] = self._generate_javascript_example(endpoint)
            elif language == 'java':
                examples[language] = self._generate_java_example(endpoint)
            elif language == 'go':
                examples[language] = self._generate_go_example(endpoint)
        
        return examples
    
    def _generate_curl_example(self, endpoint: APIEndpoint) -> str:
        """Generate cURL example"""
        url = f"https://api.ai-ui-builder.com/v1{endpoint.path}"
        
        # Replace path parameters with example values
        url = re.sub(r'\{(\w+)\}', r'example_\1', url)
        
        curl_cmd = f"curl -X {endpoint.method.upper()} \\\n"
        curl_cmd += f"  '{url}' \\\n"
        curl_cmd += "  -H 'Authorization: Bearer YOUR_API_TOKEN' \\\n"
        curl_cmd += "  -H 'Content-Type: application/json'"
        
        if endpoint.request_body and endpoint.method.upper() in ['POST', 'PUT', 'PATCH']:
            example_body = self._get_example_request_body(endpoint)
            curl_cmd += " \\\n  -d '" + json.dumps(example_body, indent=2) + "'"
        
        return curl_cmd
    
    def _generate_python_example(self, endpoint: APIEndpoint) -> str:
        """Generate Python example"""
        code = "import requests\nimport json\n\n"
        code += "# Set your API token\n"
        code += "API_TOKEN = 'your_api_token_here'\n"
        code += "BASE_URL = 'https://api.ai-ui-builder.com/v1'\n\n"
        
        url = f"BASE_URL + '{endpoint.path}'"
        url = re.sub(r'\{(\w+)\}', r"' + example_\1 + '", url)
        
        code += "# Make the request\n"
        code += f"response = requests.{endpoint.method.lower()}(\n"
        code += f"    {url},\n"
        code += "    headers={\n"
        code += "        'Authorization': f'Bearer {API_TOKEN}',\n"
        code += "        'Content-Type': 'application/json'\n"
        code += "    }"
        
        if endpoint.request_body and endpoint.method.upper() in ['POST', 'PUT', 'PATCH']:
            example_body = self._get_example_request_body(endpoint)
            code += ",\n    json=" + json.dumps(example_body, indent=4)
        
        code += "\n)\n\n"
        code += "# Handle the response\n"
        code += "if response.status_code == 200:\n"
        code += "    data = response.json()\n"
        code += "    print(json.dumps(data, indent=2))\n"
        code += "else:\n"
        code += "    print(f'Error: {response.status_code} - {response.text}')"
        
        return code
    
    def _generate_javascript_example(self, endpoint: APIEndpoint) -> str:
        """Generate JavaScript example"""
        code = "// Set your API token\n"
        code += "const API_TOKEN = 'your_api_token_here';\n"
        code += "const BASE_URL = 'https://api.ai-ui-builder.com/v1';\n\n"
        
        url = f"BASE_URL + '{endpoint.path}'"
        url = re.sub(r'\{(\w+)\}', r"${example_\1}", url)
        
        code += "// Make the request\n"
        code += f"const response = await fetch(`{url}`, {{\n"
        code += f"  method: '{endpoint.method.upper()}',\n"
        code += "  headers: {\n"
        code += "    'Authorization': `Bearer ${API_TOKEN}`,\n"
        code += "    'Content-Type': 'application/json'\n"
        code += "  }"
        
        if endpoint.request_body and endpoint.method.upper() in ['POST', 'PUT', 'PATCH']:
            example_body = self._get_example_request_body(endpoint)
            code += ",\n  body: JSON.stringify(" + json.dumps(example_body, indent=2) + ")"
        
        code += "\n});\n\n"
        code += "// Handle the response\n"
        code += "if (response.ok) {\n"
        code += "  const data = await response.json();\n"
        code += "  console.log(data);\n"
        code += "} else {\n"
        code += "  console.error(`Error: ${response.status} - ${await response.text()}`);\n"
        code += "}"
        
        return code
    
    def _generate_java_example(self, endpoint: APIEndpoint) -> str:
        """Generate Java example"""
        code = "import java.net.http.*;\nimport java.net.URI;\nimport java.io.IOException;\n\n"
        code += "public class AIUIBuilderExample {\n"
        code += "    private static final String API_TOKEN = \"your_api_token_here\";\n"
        code += "    private static final String BASE_URL = \"https://api.ai-ui-builder.com/v1\";\n\n"
        code += "    public static void main(String[] args) throws IOException, InterruptedException {\n"
        code += "        HttpClient client = HttpClient.newHttpClient();\n\n"
        
        url = f"BASE_URL + \"{endpoint.path}\""
        url = re.sub(r'\{(\w+)\}', r'" + example_\1 + "', url)
        
        code += f"        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()\n"
        code += f"            .uri(URI.create({url}))\n"
        code += "            .header(\"Authorization\", \"Bearer \" + API_TOKEN)\n"
        code += "            .header(\"Content-Type\", \"application/json\")"
        
        if endpoint.request_body and endpoint.method.upper() in ['POST', 'PUT', 'PATCH']:
            example_body = self._get_example_request_body(endpoint)
            json_body = json.dumps(example_body).replace('"', '\\"')
            code += f"\n            .{endpoint.method.upper()}(HttpRequest.BodyPublishers.ofString(\"{json_body}\"))"
        else:
            code += f"\n            .{endpoint.method.upper()}()"
        
        code += ";\n\n"
        code += "        HttpRequest request = requestBuilder.build();\n"
        code += "        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());\n\n"
        code += "        if (response.statusCode() == 200) {\n"
        code += "            System.out.println(response.body());\n"
        code += "        } else {\n"
        code += "            System.err.println(\"Error: \" + response.statusCode() + \" - \" + response.body());\n"
        code += "        }\n"
        code += "    }\n"
        code += "}"
        
        return code
    
    def _generate_go_example(self, endpoint: APIEndpoint) -> str:
        """Generate Go example"""
        code = "package main\n\n"
        code += "import (\n"
        code += "    \"bytes\"\n"
        code += "    \"encoding/json\"\n"
        code += "    \"fmt\"\n"
        code += "    \"io/ioutil\"\n"
        code += "    \"net/http\"\n"
        code += ")\n\n"
        code += "const (\n"
        code += "    APIToken = \"your_api_token_here\"\n"
        code += "    BaseURL  = \"https://api.ai-ui-builder.com/v1\"\n"
        code += ")\n\n"
        code += "func main() {\n"
        
        url = f"BaseURL + \"{endpoint.path}\""
        url = re.sub(r'\{(\w+)\}', r'" + example_\1 + "', url)
        
        if endpoint.request_body and endpoint.method.upper() in ['POST', 'PUT', 'PATCH']:
            example_body = self._get_example_request_body(endpoint)
            code += "    requestBody := map[string]interface{}{\n"
            for key, value in example_body.items():
                if isinstance(value, str):
                    code += f"        \"{key}\": \"{value}\",\n"
                else:
                    code += f"        \"{key}\": {json.dumps(value)},\n"
            code += "    }\n\n"
            code += "    jsonBody, _ := json.Marshal(requestBody)\n"
            code += f"    req, _ := http.NewRequest(\"{endpoint.method.upper()}\", {url}, bytes.NewBuffer(jsonBody))\n"
        else:
            code += f"    req, _ := http.NewRequest(\"{endpoint.method.upper()}\", {url}, nil)\n"
        
        code += "    req.Header.Set(\"Authorization\", \"Bearer \"+APIToken)\n"
        code += "    req.Header.Set(\"Content-Type\", \"application/json\")\n\n"
        code += "    client := &http.Client{}\n"
        code += "    resp, err := client.Do(req)\n"
        code += "    if err != nil {\n"
        code += "        fmt.Printf(\"Error: %v\\n\", err)\n"
        code += "        return\n"
        code += "    }\n"
        code += "    defer resp.Body.Close()\n\n"
        code += "    body, _ := ioutil.ReadAll(resp.Body)\n"
        code += "    if resp.StatusCode == 200 {\n"
        code += "        fmt.Println(string(body))\n"
        code += "    } else {\n"
        code += "        fmt.Printf(\"Error: %d - %s\\n\", resp.StatusCode, string(body))\n"
        code += "    }\n"
        code += "}"
        
        return code
    
    def _get_example_request_body(self, endpoint: APIEndpoint) -> Dict[str, Any]:
        """Get example request body for endpoint"""
        # This would typically be extracted from the endpoint's request body schema
        # For now, return a generic example
        return {
            "prompt": "Create a modern landing page with hero section",
            "style": "modern",
            "framework": "react",
            "theme": "light"
        }

class DocumentationManager:
    """Manages API documentation generation and publishing"""
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.openapi_generator = OpenAPIGenerator(
            title="AI UI Builder API",
            version="1.0.0",
            description="AI-powered UI generation and management platform"
        )
        self.code_generator = CodeExampleGenerator()
    
    def scan_endpoints(self, app_module):
        """Scan application for API endpoints"""
        # This would scan your FastAPI/Flask app for endpoints
        # Implementation depends on your web framework
        pass
    
    def generate_documentation(self) -> Dict[str, Any]:
        """Generate complete API documentation"""
        try:
            # Add security schemes
            self.openapi_generator.add_security_scheme(
                'BearerAuth',
                'http',
                scheme='bearer',
                bearerFormat='JWT'
            )
            
            self.openapi_generator.add_security_scheme(
                'ApiKeyAuth',
                'apiKey',
                **{'in': 'header', 'name': 'X-API-Key'}
            )
            
            # Generate OpenAPI spec
            spec = self.openapi_generator.generate_openapi_spec()
            
            # Save to files
            self._save_openapi_spec(spec)
            self._generate_html_docs(spec)
            self._generate_markdown_docs(spec)
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.LOW,
                action="generate_api_documentation",
                result="success",
                details={
                    "endpoints_count": len(self.openapi_generator.endpoints),
                    "schemas_count": len(self.openapi_generator.schemas)
                }
            )
            
            return spec
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="generate_api_documentation",
                result="error",
                details={"error": str(e)}
            )
            raise
    
    def _save_openapi_spec(self, spec: Dict[str, Any]):
        """Save OpenAPI specification to files"""
        # Save as JSON
        json_path = self.output_dir / "openapi.json"
        with open(json_path, 'w') as f:
            json.dump(spec, f, indent=2, default=str)
        
        # Save as YAML
        yaml_path = self.output_dir / "openapi.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False)
    
    def _generate_html_docs(self, spec: Dict[str, Any]):
        """Generate HTML documentation using Swagger UI"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>AI UI Builder API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                spec: """ + json.dumps(spec) + """,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>
        """
        
        html_path = self.output_dir / "index.html"
        with open(html_path, 'w') as f:
            f.write(html_template)
    
    def _generate_markdown_docs(self, spec: Dict[str, Any]):
        """Generate Markdown documentation"""
        md_content = f"# {spec['info']['title']}\n\n"
        md_content += f"{spec['info']['description']}\n\n"
        md_content += f"**Version:** {spec['info']['version']}\n\n"
        
        # Add authentication section
        md_content += "## Authentication\n\n"
        md_content += "This API uses Bearer token authentication. Include your API token in the Authorization header:\n\n"
        md_content += "```\nAuthorization: Bearer YOUR_API_TOKEN\n```\n\n"
        
        # Add endpoints
        md_content += "## Endpoints\n\n"
        
        for path, methods in spec['paths'].items():
            for method, details in methods.items():
                md_content += f"### {method.upper()} {path}\n\n"
                md_content += f"{details['summary']}\n\n"
                md_content += f"{details['description']}\n\n"
                
                # Add parameters
                if details.get('parameters'):
                    md_content += "**Parameters:**\n\n"
                    for param in details['parameters']:
                        md_content += f"- `{param['name']}` ({param['in']}) - {param.get('description', '')}\n"
                    md_content += "\n"
                
                # Add request body
                if details.get('requestBody'):
                    md_content += "**Request Body:**\n\n"
                    md_content += "```json\n"
                    md_content += json.dumps(details['requestBody'], indent=2)
                    md_content += "\n```\n\n"
                
                # Add responses
                md_content += "**Responses:**\n\n"
                for status, response in details['responses'].items():
                    md_content += f"- `{status}` - {response['description']}\n"
                md_content += "\n"
        
        md_path = self.output_dir / "README.md"
        with open(md_path, 'w') as f:
            f.write(md_content)

# Global documentation manager instance
docs_manager = DocumentationManager()