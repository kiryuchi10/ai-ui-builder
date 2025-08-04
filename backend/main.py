# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import uuid
from datetime import datetime

from services.ai_orchestrator import AIOrchestrator
from services.figma_tool import FigmaTool
from services.github_tool import GitHubTool
from services.render_tool import RenderTool
from services.history_service import HistoryService
from routes.history import router as history_router
from routes.validation import router as validation_router
from routes.components import router as components_router
from routes.testing import router as testing_router
from routes.export import router as export_router
from database import init_database

app = FastAPI(title="AI UI Builder API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(history_router)
app.include_router(validation_router)
app.include_router(components_router)
app.include_router(testing_router)
app.include_router(export_router)

# Global state (in production, use Redis or database)
generation_status = {}

class GenerationRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None
    project_name: Optional[str] = None

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    job_id: str
    status: str
    current_step: int
    total_steps: int
    step_name: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize tools
figma_tool = FigmaTool()
github_tool = GitHubTool()
render_tool = RenderTool()
orchestrator = AIOrchestrator(figma_tool, github_tool, render_tool)
history_service = HistoryService()

@app.get("/")
async def root():
    return {"message": "AI UI Builder API", "version": "1.0.0"}

@app.post("/generate", response_model=GenerationResponse)
async def generate_ui(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Start UI generation process"""
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    generation_status[job_id] = {
        "status": "started",
        "current_step": 0,
        "total_steps": 5,
        "step_name": "Initializing",
        "created_at": datetime.now(),
        "prompt": request.prompt,
        "results": {}
    }
    
    # Save to history database
    from database import get_db
    db = next(get_db())
    try:
        history_service.save_prompt_history(
            db=db,
            prompt=request.prompt,
            user_id=request.user_id,
            project_name=request.project_name,
            job_id=job_id
        )
    except Exception as e:
        print(f"Error saving to history: {e}")
    finally:
        db.close()
    
    # Start background task
    background_tasks.add_task(run_generation, job_id, request)
    
    return GenerationResponse(
        job_id=job_id,
        status="started",
        message="UI generation started"
    )

@app.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Get generation status"""
    if job_id not in generation_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = generation_status[job_id]
    return StatusResponse(
        job_id=job_id,
        status=status["status"],
        current_step=status["current_step"],
        total_steps=status["total_steps"],
        step_name=status["step_name"],
        results=status.get("results"),
        error=status.get("error")
    )

@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a generation job"""
    if job_id in generation_status:
        generation_status[job_id]["status"] = "cancelled"
        return {"message": "Job cancelled"}
    raise HTTPException(status_code=404, detail="Job not found")

async def run_generation(job_id: str, request: GenerationRequest):
    """Background task to run the full generation pipeline"""
    start_time = datetime.now()
    
    try:
        await orchestrator.generate_ui(
            job_id=job_id,
            prompt=request.prompt,
            project_name=request.project_name or f"ai-ui-{job_id[:8]}",
            status_callback=lambda step, name, data: update_status(job_id, step, name, data)
        )
        
        generation_status[job_id]["status"] = "completed"
        
        # Update history with results
        from database import get_db
        db = next(get_db())
        try:
            generation_time = int((datetime.now() - start_time).total_seconds())
            results = generation_status[job_id].get("results", {})
            
            # Find history entry by job_id and update it
            from models.prompt_model import PromptHistory
            history_entry = db.query(PromptHistory).filter(
                PromptHistory.job_id == job_id
            ).first()
            
            if history_entry:
                history_service.update_prompt_history(
                    db=db,
                    history_id=history_entry.id,
                    status="success",
                    generation_time=generation_time,
                    generated_code=results.get("code"),
                    figma_url=results.get("figma_url"),
                    github_repo=results.get("github_repo"),
                    deploy_url=results.get("deploy_url"),
                    ai_model_used="gpt-4",
                    metadata=results
                )
        except Exception as e:
            print(f"Error updating history: {e}")
        finally:
            db.close()
        
    except Exception as e:
        generation_status[job_id]["status"] = "failed"
        generation_status[job_id]["error"] = str(e)
        
        # Update history with error
        from database import get_db
        db = next(get_db())
        try:
            from models.prompt_model import PromptHistory
            history_entry = db.query(PromptHistory).filter(
                PromptHistory.job_id == job_id
            ).first()
            
            if history_entry:
                history_service.update_prompt_history(
                    db=db,
                    history_id=history_entry.id,
                    status="failed",
                    metadata={"error": str(e)}
                )
        except Exception as update_error:
            print(f"Error updating history with failure: {update_error}")
        finally:
            db.close()

def update_status(job_id: str, step: int, step_name: str, data: Dict[str, Any]):
    """Update job status"""
    if job_id in generation_status:
        generation_status[job_id].update({
            "current_step": step,
            "step_name": step_name,
            "results": {**generation_status[job_id].get("results", {}), **data}
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
