from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any, List

Base = declarative_base()

class ComponentLibrary(Base):
    __tablename__ = "component_libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    framework = Column(String(100), nullable=False, index=True)  # react, vue, angular, etc.
    
    # Library metadata
    version = Column(String(50), nullable=True)
    npm_package = Column(String(255), nullable=True)
    cdn_url = Column(String(500), nullable=True)
    documentation_url = Column(String(500), nullable=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    popularity_score = Column(Float, default=0.0)
    
    # Configuration
    import_statement = Column(Text, nullable=True)  # How to import components
    css_imports = Column(JSON, nullable=True)  # Required CSS files
    dependencies = Column(JSON, nullable=True)  # Required dependencies
    
    # Metadata
    tags = Column(JSON, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'framework': self.framework,
            'version': self.version,
            'npm_package': self.npm_package,
            'cdn_url': self.cdn_url,
            'documentation_url': self.documentation_url,
            'usage_count': self.usage_count,
            'popularity_score': self.popularity_score,
            'import_statement': self.import_statement,
            'css_imports': self.css_imports,
            'dependencies': self.dependencies,
            'tags': self.tags,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class Component(Base):
    __tablename__ = "components"
    
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, nullable=False, index=True)  # Foreign key to ComponentLibrary
    
    # Component details
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    
    # Component code and usage
    component_code = Column(Text, nullable=True)  # Example usage code
    props_schema = Column(JSON, nullable=True)  # Component props definition
    examples = Column(JSON, nullable=True)  # Usage examples
    
    # AI Detection patterns
    detection_patterns = Column(JSON, nullable=True)  # Patterns for AI recognition
    keywords = Column(JSON, nullable=True)  # Keywords for matching
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # How often it's successfully used
    
    # Metadata
    tags = Column(JSON, nullable=True)
    complexity_level = Column(String(50), default="medium")  # easy, medium, hard
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_library_category', 'library_id', 'category'),
        Index('idx_name_search', 'name'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'library_id': self.library_id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'category': self.category,
            'component_code': self.component_code,
            'props_schema': self.props_schema,
            'examples': self.examples,
            'detection_patterns': self.detection_patterns,
            'keywords': self.keywords,
            'usage_count': self.usage_count,
            'success_rate': self.success_rate,
            'tags': self.tags,
            'complexity_level': self.complexity_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class ComponentMapping(Base):
    __tablename__ = "component_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, nullable=True, index=True)  # Link to prompt history
    
    # Mapping details
    detected_intent = Column(Text, nullable=False)  # What the user wants
    recommended_components = Column(JSON, nullable=False)  # List of component IDs
    confidence_score = Column(Float, default=0.0)  # AI confidence in mapping
    
    # Context
    user_context = Column(JSON, nullable=True)  # Additional context
    framework_preference = Column(String(100), nullable=True)
    
    # Results
    selected_components = Column(JSON, nullable=True)  # Components actually used
    generation_success = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'prompt_id': self.prompt_id,
            'detected_intent': self.detected_intent,
            'recommended_components': self.recommended_components,
            'confidence_score': self.confidence_score,
            'user_context': self.user_context,
            'framework_preference': self.framework_preference,
            'selected_components': self.selected_components,
            'generation_success': self.generation_success,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }