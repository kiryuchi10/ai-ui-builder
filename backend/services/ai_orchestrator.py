import asyncio
from typing import Dict, Any, Callable
import openai
from datetime import datetime

class AIOrchestrator:
    """Orchestrates the entire UI generation pipeline"""
    
    def __init__(self, figma_tool, github_tool, render_tool):
        self.figma_tool = figma_tool
        self.github_tool = github_tool
        self.render_tool = render_tool
        
    async def generate_ui(
        self, 
        job_id: str, 
        prompt: str, 
        project_name: str,
        status_callback: Callable[[int, str, Dict], None]
    ):
        """Main orchestration method"""
        
        try:
            # Step 1: Analyze prompt and generate wireframe
            status_callback(0, "Analyzing prompt", {})
            await asyncio.sleep(1)  # Simulate processing
            
            wireframe_spec = await self._analyze_prompt(prompt)
            status_callback(1, "Generating wireframe", {"wireframe_spec": wireframe_spec})
            
            # Step 2: Create Figma wireframe
            wireframe_url = await self.figma_tool.create_wireframe(wireframe_spec)
            status_callback(1, "Wireframe created", {"wireframe_url": wireframe_url})
            
            # Step 3: Generate React code
            status_callback(2, "Converting to code", {})
            react_code = await self._generate_react_code(prompt, wireframe_spec)
            status_callback(2, "Code generated", {"react_code": react_code})
            
            # Step 4: Push to GitHub
            status_callback(3, "Pushing to GitHub", {})
            repo_url = await self.github_tool.create_and_push(project_name, react_code)
            status_callback(3, "Code pushed", {"repo_url": repo_url})
            
            # Step 5: Deploy to Render
            status_callback(4, "Deploying to Render", {})
            deploy_url = await self.render_tool.deploy(project_name, repo_url)
            status_callback(4, "Deployment complete", {"deploy_url": deploy_url})
            
        except Exception as e:
            raise Exception(f"Generation failed: {str(e)}")
    
    async def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze user prompt and create wireframe specification"""
        # This would use GPT/Claude to analyze the prompt
        return {
            "type": self._detect_ui_type(prompt),
            "components": self._extract_components(prompt),
            "layout": self._determine_layout(prompt),
            "style": self._determine_style(prompt)
        }
    
    def _detect_ui_type(self, prompt: str) -> str:
        """Detect the type of UI from prompt"""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['landing', 'home', 'marketing']):
            return 'landing_page'
        elif any(word in prompt_lower for word in ['dashboard', 'admin', 'panel']):
            return 'dashboard'
        elif any(word in prompt_lower for word in ['form', 'signup', 'login']):
            return 'form'
        else:
            return 'general'
    
    def _extract_components(self, prompt: str) -> list:
        """Extract UI components from prompt"""
        components = []
        prompt_lower = prompt.lower()
        
        component_map = {
            'header': ['header', 'navigation', 'nav', 'menu'],
            'hero': ['hero', 'banner', 'main section'],
            'features': ['features', 'benefits', 'services'],
            'pricing': ['pricing', 'plans', 'packages'],
            'footer': ['footer', 'contact'],
            'sidebar': ['sidebar', 'menu'],
            'cards': ['cards', 'grid', 'gallery'],
            'form': ['form', 'input', 'signup', 'contact form']
        }
        
        for component, keywords in component_map.items():
            if any(keyword in prompt_lower for keyword in keywords):
                components.append(component)
        
        return components or ['header', 'main', 'footer']  # Default components
    
    def _determine_layout(self, prompt: str) -> str:
        """Determine layout type"""
        prompt_lower = prompt.lower()
        if 'sidebar' in prompt_lower:
            return 'sidebar'
        elif 'grid' in prompt_lower:
            return 'grid'
        else:
            return 'vertical'
    
    def _determine_style(self, prompt: str) -> Dict[str, str]:
        """Determine styling preferences"""
        prompt_lower = prompt.lower()
        
        style = {
            'theme': 'light',
            'color_scheme': 'blue',
            'design_style': 'modern'
        }
        
        if 'dark' in prompt_lower:
            style['theme'] = 'dark'
        if any(color in prompt_lower for color in ['red', 'green', 'purple', 'orange']):
            for color in ['red', 'green', 'purple', 'orange']:
                if color in prompt_lower:
                    style['color_scheme'] = color
                    break
        
        return style
    
    async def _generate_react_code(self, prompt: str, wireframe_spec: Dict[str, Any]) -> str:
        """Generate React component code"""
        # This would use GPT/Claude to generate actual React code
        # For now, return a template based on the wireframe spec
        
        ui_type = wireframe_spec.get('type', 'general')
        components = wireframe_spec.get('components', [])
        style = wireframe_spec.get('style', {})
        
        if ui_type == 'landing_page':
            return self._generate_landing_page_code(prompt, components, style)
        elif ui_type == 'dashboard':
            return self._generate_dashboard_code(prompt, components, style)
        else:
            return self._generate_general_code(prompt, components, style)