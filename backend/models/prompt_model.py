from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class PromptHistory(Base):
    __tablename__ = "prompt_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)  # For future user system
    prompt = Column(Text, nullable=False)
    project_name = Column(String(255), nullable=True)
    
    # Generation results
    generated_code = Column(Text, nullable=True)
    figma_url = Column(String(500), nullable=True)
    github_repo = Column(String(255), nullable=True)
    deploy_url = Column(String(500), nullable=True)
    
    # Status and metadata
    status = Column(String(50), default="pending")  # pending, success, failed
    job_id = Column(String(255), nullable=True, index=True)
    generation_time = Column(Integer, nullable=True)  # in seconds
    
    # AI metadata
    ai_model_used = Column(String(100), nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    
    # Additional metadata
    metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # For categorization
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, index=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_prompt_search', 'prompt'),  # For text search
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'prompt': self.prompt,
            'project_name': self.project_name,
            'generated_code': self.generated_code,
            'figma_url': self.figma_url,
            'github_repo': self.github_repo,
            'deploy_url': self.deploy_url,
            'status': self.status,
            'job_id': self.job_id,
            'generation_time': self.generation_time,
            'ai_model_used': self.ai_model_used,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'metadata': self.metadata,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_deleted': self.is_deleted
        }

class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    template = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Integer, default=0)  # Percentage
    
    # Metadata
    tags = Column(JSON, nullable=True)
    variables = Column(JSON, nullable=True)  # Template variables
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Soft delete
    is_active = Column(Boolean, default=True, index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'category': self.category,
            'usage_count': self.usage_count,
            'success_rate': self.success_rate,
            'tags': self.tags,
            'variables': self.variables,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }