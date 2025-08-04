from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from database import get_db
from services.history_service import HistoryService
from models.prompt_model import PromptHistory, PromptTemplate

router = APIRouter(prefix="/api/v1/history", tags=["history"])
history_service = HistoryService()

# Pydantic models for request/response
class PromptHistoryResponse(BaseModel):
    id: int
    user_id: Optional[str]
    prompt: str
    project_name: Optional[str]
    generated_code: Optional[str]
    figma_url: Optional[str]
    github_repo: Optional[str]
    deploy_url: Optional[str]
    status: str
    job_id: Optional[str]
    generation_time: Optional[int]
    ai_model_used: Optional[str]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    created_at: Optional[str]
    updated_at: Optional[str]
    completed_at: Optional[str]

class PromptHistoryCreate(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    project_name: Optional[str] = None
    job_id: Optional[str] = None

class PromptHistoryUpdate(BaseModel):
    generated_code: Optional[str] = None
    figma_url: Optional[str] = None
    github_repo: Optional[str] = None
    deploy_url: Optional[str] = None
    status: Optional[str] = None
    generation_time: Optional[int] = None
    ai_model_used: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class PromptTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    template: str
    category: Optional[str]
    usage_count: int
    success_rate: int
    tags: Optional[List[str]]
    variables: Optional[List[str]]
    created_at: Optional[str]
    updated_at: Optional[str]
    is_active: bool

class TemplateUseRequest(BaseModel):
    template_id: int
    variables: Dict[str, str]

class StatisticsResponse(BaseModel):
    total_prompts: int
    successful_prompts: int
    failed_prompts: int
    pending_prompts: int
    success_rate: float
    avg_generation_time: float
    period_days: int

@router.get("/", response_model=List[PromptHistoryResponse])
async def get_history(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in prompts and project names"),
    db: Session = Depends(get_db)
):
    """Get prompt history with filtering and pagination"""
    
    history_entries = history_service.get_prompt_history(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        status=status,
        search=search
    )
    
    return [PromptHistoryResponse(**entry.to_dict()) for entry in history_entries]

@router.post("/", response_model=PromptHistoryResponse)
async def create_history(
    request: PromptHistoryCreate,
    db: Session = Depends(get_db)
):
    """Save a new prompt to history"""
    
    history_entry = history_service.save_prompt_history(
        db=db,
        prompt=request.prompt,
        user_id=request.user_id,
        project_name=request.project_name,
        job_id=request.job_id
    )
    
    return PromptHistoryResponse(**history_entry.to_dict())

@router.get("/{history_id}", response_model=PromptHistoryResponse)
async def get_history_item(
    history_id: int,
    user_id: Optional[str] = Query(None, description="User ID for access control"),
    db: Session = Depends(get_db)
):
    """Get a specific prompt history entry"""
    
    history_entry = history_service.get_prompt_by_id(
        db=db,
        history_id=history_id,
        user_id=user_id
    )
    
    if not history_entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return PromptHistoryResponse(**history_entry.to_dict())

@router.put("/{history_id}", response_model=PromptHistoryResponse)
async def update_history(
    history_id: int,
    request: PromptHistoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing prompt history entry"""
    
    # Convert Pydantic model to dict, excluding None values
    updates = request.dict(exclude_unset=True)
    
    history_entry = history_service.update_prompt_history(
        db=db,
        history_id=history_id,
        **updates
    )
    
    if not history_entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return PromptHistoryResponse(**history_entry.to_dict())

@router.delete("/{history_id}")
async def delete_history(
    history_id: int,
    user_id: Optional[str] = Query(None, description="User ID for access control"),
    db: Session = Depends(get_db)
):
    """Delete a prompt history entry"""
    
    success = history_service.delete_prompt_history(
        db=db,
        history_id=history_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return {"message": "History entry deleted successfully"}

@router.get("/{history_id}/reuse")
async def reuse_prompt(
    history_id: int,
    user_id: Optional[str] = Query(None, description="User ID for access control"),
    db: Session = Depends(get_db)
):
    """Get a prompt for reuse"""
    
    history_entry = history_service.get_prompt_by_id(
        db=db,
        history_id=history_id,
        user_id=user_id
    )
    
    if not history_entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    return {
        "prompt": history_entry.prompt,
        "project_name": history_entry.project_name,
        "original_id": history_entry.id,
        "original_created_at": history_entry.created_at.isoformat() if history_entry.created_at else None
    }

@router.get("/similar/{prompt}")
async def get_similar_prompts(
    prompt: str,
    user_id: Optional[str] = Query(None, description="User ID for personalized results"),
    limit: int = Query(5, ge=1, le=10, description="Number of similar prompts to return"),
    db: Session = Depends(get_db)
):
    """Get similar prompts based on the provided prompt"""
    
    similar_prompts = history_service.get_similar_prompts(
        db=db,
        prompt=prompt,
        user_id=user_id,
        limit=limit
    )
    
    return [
        {
            "id": entry.id,
            "prompt": entry.prompt,
            "project_name": entry.project_name,
            "status": entry.status,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
            "generation_time": entry.generation_time
        }
        for entry in similar_prompts
    ]

@router.get("/stats/overview", response_model=StatisticsResponse)
async def get_statistics(
    user_id: Optional[str] = Query(None, description="User ID for personalized stats"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get prompt usage statistics"""
    
    stats = history_service.get_prompt_statistics(
        db=db,
        user_id=user_id,
        days=days
    )
    
    return StatisticsResponse(**stats)

# Template endpoints
@router.get("/templates/", response_model=List[PromptTemplateResponse])
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=50, description="Number of templates to return"),
    db: Session = Depends(get_db)
):
    """Get available prompt templates"""
    
    templates = history_service.get_prompt_templates(
        db=db,
        category=category,
        limit=limit
    )
    
    return [PromptTemplateResponse(**template.to_dict()) for template in templates]

@router.post("/templates/use")
async def use_template(
    request: TemplateUseRequest,
    db: Session = Depends(get_db)
):
    """Use a template with provided variables"""
    
    prompt = history_service.use_template(
        db=db,
        template_id=request.template_id,
        variables=request.variables
    )
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "prompt": prompt,
        "template_id": request.template_id,
        "variables_used": request.variables
    }