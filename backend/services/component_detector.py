import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from models.component_model import ComponentLibrary, Component, ComponentMapping

@dataclass
class ComponentRecommendation:
    component_id: int
    component_name: str
    library_name: str
    confidence: float
    reason: str
    code_example: str

@dataclass
class DetectionResult:
    intent: str
    recommendations: List[ComponentRecommendation]
    overall_confidence: float
    suggested_framework: str

class ComponentDetector:
    """AI-powered component detection and mapping service"""
    
    def __init__(self):
        # UI element patterns for detection
        self.ui_patterns = {
            'button': {
                'keywords': ['button', 'btn', 'click', 'submit', 'action', 'cta'],
                'patterns': [
                    r'\b(button|btn)\b',
                    r'\b(click|submit|action)\b',
                    r'\b(primary|secondary|danger|success)\s+(button|btn)\b'
                ],
                'components': ['Button', 'IconButton', 'ActionButton']
            },
            'form': {
                'keywords': ['form', 'input', 'field', 'validation', 'submit'],
                'patterns': [
                    r'\b(form|input|field)\b',
                    r'\b(text\s+field|input\s+field)\b',
                    r'\b(validation|validate)\b'
                ],
                'components': ['Form', 'Input', 'TextField', 'FormField']
            },
            'navigation': {
                'keywords': ['nav', 'menu', 'sidebar', 'header', 'navigation'],
                'patterns': [
                    r'\b(nav|navigation|menu)\b',
                    r'\b(sidebar|header|footer)\b',
                    r'\b(breadcrumb|tabs)\b'
                ],
                'components': ['Navigation', 'Menu', 'Sidebar', 'Header']
            },
            'data_display': {
                'keywords': ['table', 'list', 'grid', 'card', 'data'],
                'patterns': [
                    r'\b(table|list|grid)\b',
                    r'\b(card|cards)\b',
                    r'\b(data\s+table|data\s+grid)\b'
                ],
                'components': ['Table', 'DataGrid', 'Card', 'List']
            },
            'layout': {
                'keywords': ['layout', 'container', 'row', 'column', 'flex'],
                'patterns': [
                    r'\b(layout|container)\b',
                    r'\b(row|column|grid)\b',
                    r'\b(flex|flexbox)\b'
                ],
                'components': ['Container', 'Grid', 'Flex', 'Layout']
            },
            'feedback': {
                'keywords': ['modal', 'dialog', 'alert', 'notification', 'toast'],
                'patterns': [
                    r'\b(modal|dialog|popup)\b',
                    r'\b(alert|notification|toast)\b',
                    r'\b(loading|spinner|progress)\b'
                ],
                'components': ['Modal', 'Alert', 'Toast', 'ProgressBar']
            },
            'charts': {
                'keywords': ['chart', 'graph', 'visualization', 'analytics', 'dashboard'],
                'patterns': [
                    r'\b(chart|graph|plot)\b',
                    r'\b(bar\s+chart|line\s+chart|pie\s+chart)\b',
                    r'\b(analytics|dashboard|visualization)\b'
                ],
                'components': ['Chart', 'BarChart', 'LineChart', 'Dashboard']
            }
        }
        
        # Framework-specific component libraries
        self.framework_libraries = {
            'react': [
                'Material-UI', 'Ant Design', 'Chakra UI', 'React Bootstrap',
                'Mantine', 'Semantic UI React', 'Blueprint', 'Grommet'
            ],
            'vue': [
                'Vuetify', 'Quasar', 'Element Plus', 'Ant Design Vue',
                'Naive UI', 'PrimeVue', 'Buefy', 'BootstrapVue'
            ],
            'angular': [
                'Angular Material', 'PrimeNG', 'Ng-Bootstrap', 'Clarity',
                'Nebular', 'Taiga UI', 'NG-ZORRO', 'Ionic'
            ]
        }
    
    def detect_components(self, prompt: str, db: Session, framework: str = 'react') -> DetectionResult:
        """Detect and recommend components based on user prompt"""
        
        # Analyze the prompt to understand intent
        intent = self._analyze_intent(prompt)
        
        # Find matching UI patterns
        detected_patterns = self._detect_ui_patterns(prompt)
        
        # Get component recommendations
        recommendations = self._get_component_recommendations(
            detected_patterns, db, framework
        )
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(recommendations)
        
        return DetectionResult(
            intent=intent,
            recommendations=recommendations,
            overall_confidence=overall_confidence,
            suggested_framework=framework
        )
    
    def _analyze_intent(self, prompt: str) -> str:
        """Analyze user prompt to understand their intent"""
        prompt_lower = prompt.lower()
        
        # Common UI intents
        if any(word in prompt_lower for word in ['dashboard', 'admin', 'analytics']):
            return "Create a dashboard interface with data visualization and navigation"
        elif any(word in prompt_lower for word in ['landing', 'homepage', 'marketing']):
            return "Build a marketing landing page with hero section and call-to-actions"
        elif any(word in prompt_lower for word in ['form', 'signup', 'login', 'register']):
            return "Design a form interface for user input and validation"
        elif any(word in prompt_lower for word in ['ecommerce', 'shop', 'store', 'product']):
            return "Create an e-commerce interface with product listings and shopping features"
        elif any(word in prompt_lower for word in ['blog', 'article', 'content']):
            return "Build a content-focused interface for articles and blog posts"
        else:
            return f"Create a user interface based on: {prompt[:100]}..."
    
    def _detect_ui_patterns(self, prompt: str) -> Dict[str, float]:
        """Detect UI patterns in the prompt with confidence scores"""
        detected = {}
        prompt_lower = prompt.lower()
        
        for pattern_name, pattern_data in self.ui_patterns.items():
            confidence = 0.0
            
            # Check keywords
            keyword_matches = sum(1 for keyword in pattern_data['keywords'] 
                                if keyword in prompt_lower)
            if keyword_matches > 0:
                confidence += (keyword_matches / len(pattern_data['keywords'])) * 0.6
            
            # Check regex patterns
            pattern_matches = sum(1 for pattern in pattern_data['patterns']
                                if re.search(pattern, prompt_lower))
            if pattern_matches > 0:
                confidence += (pattern_matches / len(pattern_data['patterns'])) * 0.4
            
            if confidence > 0.1:  # Only include if there's reasonable confidence
                detected[pattern_name] = min(confidence, 1.0)
        
        return detected
    
    def _get_component_recommendations(
        self, 
        detected_patterns: Dict[str, float], 
        db: Session, 
        framework: str
    ) -> List[ComponentRecommendation]:
        """Get component recommendations based on detected patterns"""
        recommendations = []
        
        # Get active component libraries for the framework
        libraries = db.query(ComponentLibrary).filter(
            ComponentLibrary.framework == framework,
            ComponentLibrary.is_active == True
        ).all()
        
        if not libraries:
            # Return mock recommendations if no libraries in DB
            return self._get_mock_recommendations(detected_patterns, framework)
        
        for pattern_name, confidence in detected_patterns.items():
            if pattern_name in self.ui_patterns:
                component_names = self.ui_patterns[pattern_name]['components']
                
                for library in libraries:
                    # Find components in this library that match the pattern
                    components = db.query(Component).filter(
                        Component.library_id == library.id,
                        Component.name.in_(component_names),
                        Component.is_active == True
                    ).all()
                    
                    for component in components:
                        recommendations.append(ComponentRecommendation(
                            component_id=component.id,
                            component_name=component.name,
                            library_name=library.name,
                            confidence=confidence * (library.popularity_score / 10.0),
                            reason=f"Matches {pattern_name} pattern with {confidence:.1%} confidence",
                            code_example=component.component_code or self._generate_mock_code(
                                component.name, library.name
                            )
                        ))
        
        # Sort by confidence and return top recommendations
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        return recommendations[:10]  # Top 10 recommendations
    
    def _get_mock_recommendations(
        self, 
        detected_patterns: Dict[str, float], 
        framework: str
    ) -> List[ComponentRecommendation]:
        """Generate mock recommendations when no database entries exist"""
        recommendations = []
        
        # Popular libraries for each framework
        popular_libs = {
            'react': 'Material-UI',
            'vue': 'Vuetify', 
            'angular': 'Angular Material'
        }
        
        lib_name = popular_libs.get(framework, 'Material-UI')
        
        for pattern_name, confidence in detected_patterns.items():
            if pattern_name in self.ui_patterns:
                components = self.ui_patterns[pattern_name]['components']
                
                for i, component_name in enumerate(components[:3]):  # Top 3 per pattern
                    recommendations.append(ComponentRecommendation(
                        component_id=i + 1,
                        component_name=component_name,
                        library_name=lib_name,
                        confidence=confidence * (1.0 - i * 0.1),  # Decrease confidence for lower priority
                        reason=f"Matches {pattern_name} pattern",
                        code_example=self._generate_mock_code(component_name, lib_name)
                    ))
        
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        return recommendations[:8]  # Top 8 recommendations
    
    def _generate_mock_code(self, component_name: str, library_name: str) -> str:
        """Generate mock code example for a component"""
        if 'Material-UI' in library_name or 'MUI' in library_name:
            return f"""import {{ {component_name} }} from '@mui/material/{component_name}';

<{component_name}
  variant="contained"
  color="primary"
>
  {component_name} Example
</{component_name}>"""
        
        elif 'Ant Design' in library_name:
            return f"""import {{ {component_name} }} from 'antd';

<{component_name} type="primary">
  {component_name} Example
</{component_name}>"""
        
        else:
            return f"""import {{ {component_name} }} from '{library_name.lower()}';

<{component_name}>
  {component_name} Example
</{component_name}>"""
    
    def _calculate_overall_confidence(self, recommendations: List[ComponentRecommendation]) -> float:
        """Calculate overall confidence in the recommendations"""
        if not recommendations:
            return 0.0
        
        # Weight by position and confidence
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for i, rec in enumerate(recommendations[:5]):  # Top 5 for calculation
            weight = 1.0 / (i + 1)  # Decreasing weight
            total_weighted_confidence += rec.confidence * weight
            total_weight += weight
        
        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0
    
    def save_mapping(
        self, 
        db: Session, 
        prompt_id: Optional[int], 
        detection_result: DetectionResult,
        framework: str
    ) -> ComponentMapping:
        """Save component mapping to database"""
        
        recommended_components = [
            {
                'component_id': rec.component_id,
                'component_name': rec.component_name,
                'library_name': rec.library_name,
                'confidence': rec.confidence,
                'reason': rec.reason
            }
            for rec in detection_result.recommendations
        ]
        
        mapping = ComponentMapping(
            prompt_id=prompt_id,
            detected_intent=detection_result.intent,
            recommended_components=recommended_components,
            confidence_score=detection_result.overall_confidence,
            framework_preference=framework
        )
        
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        
        return mapping
    
    def get_popular_components(self, db: Session, framework: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular components for a framework"""
        
        libraries = db.query(ComponentLibrary).filter(
            ComponentLibrary.framework == framework,
            ComponentLibrary.is_active == True
        ).order_by(ComponentLibrary.popularity_score.desc()).all()
        
        popular_components = []
        
        for library in libraries:
            components = db.query(Component).filter(
                Component.library_id == library.id,
                Component.is_active == True
            ).order_by(Component.usage_count.desc()).limit(5).all()
            
            for component in components:
                popular_components.append({
                    'component': component.to_dict(),
                    'library': library.to_dict()
                })
        
        return popular_components[:limit]
    
    def update_component_usage(self, db: Session, component_id: int, success: bool = True):
        """Update component usage statistics"""
        component = db.query(Component).filter(Component.id == component_id).first()
        if component:
            component.usage_count += 1
            if success:
                # Update success rate (simple moving average)
                current_success_rate = component.success_rate or 0.0
                component.success_rate = (current_success_rate * 0.9) + (1.0 * 0.1)
            else:
                component.success_rate = (component.success_rate or 0.0) * 0.95
            
            db.commit()