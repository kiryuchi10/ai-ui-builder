from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from models.prompt_model import PromptHistory, PromptTemplate
from database import get_db

class HistoryService:
    """Service for managing prompt history and templates"""
    
    def __init__(self):
        pass
    
    def save_prompt_history(
        self, 
        db: Session,
        prompt: str,
        user_id: Optional[str] = None,
        project_name: Optional[str] = None,
        job_id: Optional[str] = None,
        **kwargs
    ) -> PromptHistory:
        """Save a new prompt to history"""
        
        history_entry = PromptHistory(
            user_id=user_id,
            prompt=prompt,
            project_name=project_name,
            job_id=job_id,
            status="pending",
            **kwargs
        )
        
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)
        
        return history_entry
    
    def update_prompt_history(
        self,
        db: Session,
        history_id: int,
        **updates
    ) -> Optional[PromptHistory]:
        """Update an existing prompt history entry"""
        
        history_entry = db.query(PromptHistory).filter(
            PromptHistory.id == history_id,
            PromptHistory.is_deleted == False
        ).first()
        
        if not history_entry:
            return None
        
        for key, value in updates.items():
            if hasattr(history_entry, key):
                setattr(history_entry, key, value)
        
        history_entry.updated_at = datetime.utcnow()
        
        if updates.get('status') == 'success':
            history_entry.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(history_entry)
        
        return history_entry
    
    def get_prompt_history(
        self,
        db: Session,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[PromptHistory]:
        """Get prompt history with filtering and pagination"""
        
        query = db.query(PromptHistory).filter(
            PromptHistory.is_deleted == False
        )
        
        if user_id:
            query = query.filter(PromptHistory.user_id == user_id)
        
        if status:
            query = query.filter(PromptHistory.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    PromptHistory.prompt.ilike(search_term),
                    PromptHistory.project_name.ilike(search_term)
                )
            )
        
        return query.order_by(desc(PromptHistory.created_at)).offset(offset).limit(limit).all()
    
    def get_prompt_by_id(
        self,
        db: Session,
        history_id: int,
        user_id: Optional[str] = None
    ) -> Optional[PromptHistory]:
        """Get a specific prompt history entry"""
        
        query = db.query(PromptHistory).filter(
            PromptHistory.id == history_id,
            PromptHistory.is_deleted == False
        )
        
        if user_id:
            query = query.filter(PromptHistory.user_id == user_id)
        
        return query.first()
    
    def delete_prompt_history(
        self,
        db: Session,
        history_id: int,
        user_id: Optional[str] = None
    ) -> bool:
        """Soft delete a prompt history entry"""
        
        query = db.query(PromptHistory).filter(
            PromptHistory.id == history_id,
            PromptHistory.is_deleted == False
        )
        
        if user_id:
            query = query.filter(PromptHistory.user_id == user_id)
        
        history_entry = query.first()
        if not history_entry:
            return False
        
        history_entry.is_deleted = True
        history_entry.updated_at = datetime.utcnow()
        
        db.commit()
        return True
    
    def get_similar_prompts(
        self,
        db: Session,
        prompt: str,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[PromptHistory]:
        """Get similar prompts based on text similarity (basic implementation)"""
        
        # Simple keyword-based similarity (can be enhanced with embeddings)
        keywords = prompt.lower().split()
        
        query = db.query(PromptHistory).filter(
            PromptHistory.is_deleted == False,
            PromptHistory.status == "success"
        )
        
        if user_id:
            query = query.filter(PromptHistory.user_id == user_id)
        
        # Filter by keyword matches
        conditions = []
        for keyword in keywords:
            if len(keyword) > 3:  # Only use meaningful keywords
                conditions.append(PromptHistory.prompt.ilike(f"%{keyword}%"))
        
        if conditions:
            query = query.filter(or_(*conditions))
        
        return query.order_by(desc(PromptHistory.created_at)).limit(limit).all()
    
    def get_prompt_statistics(
        self,
        db: Session,
        user_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get prompt usage statistics"""
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(PromptHistory).filter(
            PromptHistory.is_deleted == False,
            PromptHistory.created_at >= since_date
        )
        
        if user_id:
            query = query.filter(PromptHistory.user_id == user_id)
        
        total_prompts = query.count()
        successful_prompts = query.filter(PromptHistory.status == "success").count()
        failed_prompts = query.filter(PromptHistory.status == "failed").count()
        pending_prompts = query.filter(PromptHistory.status == "pending").count()
        
        success_rate = (successful_prompts / total_prompts * 100) if total_prompts > 0 else 0
        
        # Average generation time for successful prompts
        successful_entries = query.filter(
            PromptHistory.status == "success",
            PromptHistory.generation_time.isnot(None)
        ).all()
        
        avg_generation_time = 0
        if successful_entries:
            avg_generation_time = sum(entry.generation_time for entry in successful_entries) / len(successful_entries)
        
        return {
            "total_prompts": total_prompts,
            "successful_prompts": successful_prompts,
            "failed_prompts": failed_prompts,
            "pending_prompts": pending_prompts,
            "success_rate": round(success_rate, 2),
            "avg_generation_time": round(avg_generation_time, 2),
            "period_days": days
        }
    
    # Template methods
    def get_prompt_templates(
        self,
        db: Session,
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[PromptTemplate]:
        """Get available prompt templates"""
        
        query = db.query(PromptTemplate).filter(
            PromptTemplate.is_active == True
        )
        
        if category:
            query = query.filter(PromptTemplate.category == category)
        
        return query.order_by(desc(PromptTemplate.usage_count)).limit(limit).all()
    
    def use_template(
        self,
        db: Session,
        template_id: int,
        variables: Dict[str, str]
    ) -> Optional[str]:
        """Use a template with provided variables"""
        
        template = db.query(PromptTemplate).filter(
            PromptTemplate.id == template_id,
            PromptTemplate.is_active == True
        ).first()
        
        if not template:
            return None
        
        # Replace variables in template
        prompt = template.template
        for var, value in variables.items():
            prompt = prompt.replace(f"{{{var}}}", value)
        
        # Update usage count
        template.usage_count += 1
        db.commit()
        
        return prompt
    
    def create_template(
        self,
        db: Session,
        name: str,
        template: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        variables: Optional[List[str]] = None
    ) -> PromptTemplate:
        """Create a new prompt template"""
        
        template_entry = PromptTemplate(
            name=name,
            description=description,
            template=template,
            category=category,
            tags=tags,
            variables=variables
        )
        
        db.add(template_entry)
        db.commit()
        db.refresh(template_entry)
        
        return template_entry