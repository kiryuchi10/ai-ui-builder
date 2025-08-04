"""
AI Design Assistant for UI Builder
Provides design critique, color palette generation, and typography recommendations
"""

import openai
import json
import colorsys
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

@dataclass
class ColorPalette:
    """Color palette definition"""
    name: str
    primary: str
    secondary: str
    accent: str
    background: str
    text: str
    colors: List[str]
    theme: str  # light, dark, auto

@dataclass
class DesignCritique:
    """Design critique response"""
    overall_score: float
    accessibility_score: float
    visual_hierarchy_score: float
    color_harmony_score: float
    typography_score: float
    suggestions: List[str]
    improvements: List[Dict[str, Any]]

class ColorPaletteGenerator:
    """Generates color palettes using color theory"""
    
    def __init__(self):
        self.color_schemes = {
            'monochromatic': self._generate_monochromatic,
            'analogous': self._generate_analogous,
            'complementary': self._generate_complementary,
            'triadic': self._generate_triadic,
            'split_complementary': self._generate_split_complementary
        }
    
    def generate_palette(self, base_color: str, scheme: str = 'complementary',
                        theme: str = 'light') -> ColorPalette:
        """Generate color palette from base color"""
        try:
            # Convert hex to HSV
            rgb = self._hex_to_rgb(base_color)
            hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            # Generate colors based on scheme
            if scheme in self.color_schemes:
                colors = self.color_schemes[scheme](hsv)
            else:
                colors = self._generate_complementary(hsv)
            
            # Convert back to hex
            hex_colors = [self._hsv_to_hex(color) for color in colors]
            
            # Create palette
            palette = ColorPalette(
                name=f"{scheme.title()} Palette",
                primary=hex_colors[0],
                secondary=hex_colors[1] if len(hex_colors) > 1 else hex_colors[0],
                accent=hex_colors[2] if len(hex_colors) > 2 else hex_colors[0],
                background='#ffffff' if theme == 'light' else '#1a1a1a',
                text='#333333' if theme == 'light' else '#ffffff',
                colors=hex_colors,
                theme=theme
            )
            
            return palette
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="generate_color_palette",
                result="error",
                details={"error": str(e), "base_color": base_color}
            )
            return self._get_default_palette(theme)
    
    def _generate_monochromatic(self, hsv: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Generate monochromatic color scheme"""
        h, s, v = hsv
        return [
            (h, s, v),
            (h, s * 0.7, v),
            (h, s * 0.4, v),
            (h, s, v * 0.8),
            (h, s, v * 0.6)
        ]  
  
    def _generate_analogous(self, hsv: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Generate analogous color scheme"""
        h, s, v = hsv
        return [
            (h, s, v),
            ((h + 0.083) % 1.0, s, v),  # +30 degrees
            ((h - 0.083) % 1.0, s, v),  # -30 degrees
            ((h + 0.167) % 1.0, s * 0.8, v),  # +60 degrees
            ((h - 0.167) % 1.0, s * 0.8, v)   # -60 degrees
        ]
    
    def _generate_complementary(self, hsv: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Generate complementary color scheme"""
        h, s, v = hsv
        complement = (h + 0.5) % 1.0
        return [
            (h, s, v),
            (complement, s, v),
            (h, s * 0.6, v),
            (complement, s * 0.6, v),
            (h, s * 0.3, v * 0.9)
        ]
    
    def _generate_triadic(self, hsv: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Generate triadic color scheme"""
        h, s, v = hsv
        return [
            (h, s, v),
            ((h + 0.333) % 1.0, s, v),  # +120 degrees
            ((h + 0.667) % 1.0, s, v),  # +240 degrees
            (h, s * 0.7, v),
            ((h + 0.333) % 1.0, s * 0.7, v)
        ]
    
    def _generate_split_complementary(self, hsv: Tuple[float, float, float]) -> List[Tuple[float, float, float]]:
        """Generate split complementary color scheme"""
        h, s, v = hsv
        return [
            (h, s, v),
            ((h + 0.417) % 1.0, s, v),  # +150 degrees
            ((h + 0.583) % 1.0, s, v),  # +210 degrees
            (h, s * 0.6, v),
            ((h + 0.5) % 1.0, s * 0.4, v * 0.9)  # Complement with low saturation
        ]
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _hsv_to_hex(self, hsv: Tuple[float, float, float]) -> str:
        """Convert HSV to hex color"""
        rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
        return '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
    
    def _get_default_palette(self, theme: str) -> ColorPalette:
        """Get default color palette"""
        if theme == 'dark':
            return ColorPalette(
                name="Default Dark",
                primary="#3b82f6",
                secondary="#8b5cf6",
                accent="#10b981",
                background="#1a1a1a",
                text="#ffffff",
                colors=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"],
                theme="dark"
            )
        else:
            return ColorPalette(
                name="Default Light",
                primary="#3b82f6",
                secondary="#8b5cf6",
                accent="#10b981",
                background="#ffffff",
                text="#333333",
                colors=["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"],
                theme="light"
            )

class TypographyRecommender:
    """Provides typography recommendations"""
    
    def __init__(self):
        self.font_categories = {
            'serif': ['Georgia', 'Times New Roman', 'Playfair Display', 'Merriweather'],
            'sans-serif': ['Arial', 'Helvetica', 'Inter', 'Roboto', 'Open Sans'],
            'monospace': ['Courier New', 'Monaco', 'Fira Code', 'Source Code Pro'],
            'display': ['Oswald', 'Montserrat', 'Poppins', 'Raleway']
        }
        
        self.font_pairings = {
            'classic': ('Georgia', 'Arial'),
            'modern': ('Inter', 'Roboto'),
            'elegant': ('Playfair Display', 'Open Sans'),
            'technical': ('Fira Code', 'Inter'),
            'friendly': ('Poppins', 'Open Sans')
        }
    
    def recommend_fonts(self, design_style: str, content_type: str) -> Dict[str, Any]:
        """Recommend font combinations"""
        style_mapping = {
            'modern': 'modern',
            'classic': 'classic',
            'elegant': 'elegant',
            'minimal': 'modern',
            'corporate': 'classic',
            'creative': 'elegant',
            'tech': 'technical'
        }
        
        pairing_key = style_mapping.get(design_style, 'modern')
        heading_font, body_font = self.font_pairings.get(pairing_key, ('Inter', 'Roboto'))
        
        return {
            'heading_font': heading_font,
            'body_font': body_font,
            'font_sizes': self._get_font_scale(content_type),
            'line_heights': {
                'heading': 1.2,
                'body': 1.6,
                'caption': 1.4
            },
            'font_weights': {
                'light': 300,
                'regular': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            }
        }
    
    def _get_font_scale(self, content_type: str) -> Dict[str, str]:
        """Get font scale based on content type"""
        scales = {
            'landing_page': {
                'h1': '3rem',
                'h2': '2.25rem',
                'h3': '1.875rem',
                'h4': '1.5rem',
                'body': '1rem',
                'small': '0.875rem'
            },
            'dashboard': {
                'h1': '2rem',
                'h2': '1.5rem',
                'h3': '1.25rem',
                'h4': '1.125rem',
                'body': '0.875rem',
                'small': '0.75rem'
            },
            'blog': {
                'h1': '2.5rem',
                'h2': '2rem',
                'h3': '1.5rem',
                'h4': '1.25rem',
                'body': '1.125rem',
                'small': '1rem'
            }
        }
        
        return scales.get(content_type, scales['landing_page'])

class AIDesignAssistant:
    """Main AI design assistant class"""
    
    def __init__(self, deepseek_api_key: str):
        self.client = openai.OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        self.color_generator = ColorPaletteGenerator()
        self.typography_recommender = TypographyRecommender()
    
    async def critique_design(self, design_description: str, 
                            target_audience: str = "general") -> DesignCritique:
        """Provide AI-powered design critique"""
        try:
            critique_prompt = f"""
You are a senior UI/UX designer. Analyze this design and provide detailed feedback.

Design Description: {design_description}
Target Audience: {target_audience}

Evaluate the design on these criteria (score 0-10):
1. Overall Design Quality
2. Accessibility (WCAG compliance, color contrast, readability)
3. Visual Hierarchy (clear information structure)
4. Color Harmony (color theory, brand consistency)
5. Typography (readability, font choices, sizing)

Provide specific, actionable suggestions for improvement.

Return your response as JSON with this structure:
{{
  "overall_score": 8.5,
  "accessibility_score": 7.0,
  "visual_hierarchy_score": 9.0,
  "color_harmony_score": 8.0,
  "typography_score": 8.5,
  "suggestions": ["suggestion1", "suggestion2"],
  "improvements": [
    {{"category": "accessibility", "issue": "description", "solution": "fix"}},
    {{"category": "color", "issue": "description", "solution": "fix"}}
  ]
}}
            """
            
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": critique_prompt}],
                temperature=0.3
            )
            
            critique_data = json.loads(response.choices[0].message.content)
            
            critique = DesignCritique(
                overall_score=critique_data.get("overall_score", 0),
                accessibility_score=critique_data.get("accessibility_score", 0),
                visual_hierarchy_score=critique_data.get("visual_hierarchy_score", 0),
                color_harmony_score=critique_data.get("color_harmony_score", 0),
                typography_score=critique_data.get("typography_score", 0),
                suggestions=critique_data.get("suggestions", []),
                improvements=critique_data.get("improvements", [])
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.LOW,
                action="design_critique",
                result="success",
                details={
                    "overall_score": critique.overall_score,
                    "target_audience": target_audience
                }
            )
            
            return critique
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="design_critique",
                result="error",
                details={"error": str(e)}
            )
            raise
    
    def generate_color_palette(self, brand_description: str, 
                             theme: str = "light") -> ColorPalette:
        """Generate color palette based on brand description"""
        try:
            # Extract color preferences from description
            base_color = self._extract_base_color(brand_description)
            scheme = self._determine_color_scheme(brand_description)
            
            palette = self.color_generator.generate_palette(
                base_color, scheme, theme
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_MODIFICATION,
                severity=AuditSeverity.LOW,
                action="generate_color_palette",
                result="success",
                details={
                    "scheme": scheme,
                    "theme": theme,
                    "primary_color": palette.primary
                }
            )
            
            return palette
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="generate_color_palette",
                result="error",
                details={"error": str(e)}
            )
            return self.color_generator._get_default_palette(theme)
    
    def recommend_typography(self, design_style: str, 
                           content_type: str) -> Dict[str, Any]:
        """Get typography recommendations"""
        return self.typography_recommender.recommend_fonts(
            design_style, content_type
        )
    
    async def optimize_layout(self, layout_description: str, 
                            device_type: str = "desktop") -> Dict[str, Any]:
        """Provide layout optimization suggestions"""
        try:
            layout_prompt = f"""
You are a UI/UX expert specializing in layout optimization.

Current Layout: {layout_description}
Device Type: {device_type}

Provide specific recommendations to improve:
1. Visual hierarchy and information flow
2. Spacing and proportions
3. Responsive design considerations
4. User interaction patterns
5. Accessibility improvements

Return suggestions as JSON:
{{
  "hierarchy_improvements": ["suggestion1", "suggestion2"],
  "spacing_recommendations": {{"margins": "value", "padding": "value"}},
  "responsive_adjustments": ["adjustment1", "adjustment2"],
  "interaction_improvements": ["improvement1", "improvement2"],
  "accessibility_fixes": ["fix1", "fix2"]
}}
            """
            
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": layout_prompt}],
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="optimize_layout",
                result="error",
                details={"error": str(e)}
            )
            return {}
    
    def _extract_base_color(self, description: str) -> str:
        """Extract base color from brand description"""
        color_keywords = {
            'blue': '#3b82f6',
            'red': '#ef4444',
            'green': '#10b981',
            'purple': '#8b5cf6',
            'orange': '#f59e0b',
            'pink': '#ec4899',
            'yellow': '#eab308',
            'indigo': '#6366f1',
            'teal': '#14b8a6',
            'gray': '#6b7280'
        }
        
        description_lower = description.lower()
        for color, hex_value in color_keywords.items():
            if color in description_lower:
                return hex_value
        
        return '#3b82f6'  # Default blue
    
    def _determine_color_scheme(self, description: str) -> str:
        """Determine color scheme from description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['vibrant', 'energetic', 'bold']):
            return 'triadic'
        elif any(word in description_lower for word in ['calm', 'peaceful', 'minimal']):
            return 'monochromatic'
        elif any(word in description_lower for word in ['professional', 'corporate']):
            return 'complementary'
        elif any(word in description_lower for word in ['creative', 'artistic']):
            return 'split_complementary'
        else:
            return 'analogous'

# Global design assistant instance
design_assistant = None

def initialize_design_assistant(deepseek_api_key: str):
    """Initialize the global design assistant"""
    global design_assistant
    design_assistant = AIDesignAssistant(deepseek_api_key)