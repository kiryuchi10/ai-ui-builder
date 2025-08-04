from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from database import get_db
from services.component_detector import ComponentDetector, DetectionResult, ComponentRecommendation
from models.component_model import ComponentLibrary, Component, ComponentMapping

router = APIRouter(prefix="/api/v1/components", tags=["components"])
detector = ComponentDetector()

# Pydantic models
class ComponentDetectionRequest(BaseModel):
    prompt: str
    framework: str = "react"
    prompt_id: Optional[int] = None

class ComponentRecommendationResponse(BaseModel):
    component_id: int
    component_name: str
    library_name: str
    confidence: float
    reason: str
    code_example: str

class DetectionResponse(BaseModel):
    intent: str
    recommendations: List[ComponentRecommendationResponse]
    overall_confidence: float
    suggested_framework: str
    mapping_id: Optional[int] = None

class ComponentLibraryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    framework: str
    version: Optional[str]
    npm_package: Optional[str]
    documentation_url: Optional[str]
    usage_count: int
    popularity_score: float
    category: Optional[str]
    tags: Optional[List[str]]
    is_active: bool

class ComponentResponse(BaseModel):
    id: int
    library_id: int
    name: str
    display_name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    component_code: Optional[str]
    props_schema: Optional[Dict[str, Any]]
    examples: Optional[List[Dict[str, Any]]]
    usage_count: int
    success_rate: float
    complexity_level: str
    tags: Optional[List[str]]

class ComponentLibraryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    framework: str
    version: Optional[str] = None
    npm_package: Optional[str] = None
    cdn_url: Optional[str] = None
    documentation_url: Optional[str] = None
    import_statement: Optional[str] = None
    css_imports: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None

class ComponentCreate(BaseModel):
    library_id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    component_code: Optional[str] = None
    props_schema: Optional[Dict[str, Any]] = None
    examples: Optional[List[Dict[str, Any]]] = None
    detection_patterns: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    complexity_level: str = "medium"
    tags: Optional[List[str]] = None

@router.post("/detect", response_model=DetectionResponse)
async def detect_components(
    request: ComponentDetectionRequest,
    db: Session = Depends(get_db)
):
    """Detect and recommend components based on user prompt"""
    
    try:
        # Detect components using AI
        result = detector.detect_components(
            prompt=request.prompt,
            db=db,
            framework=request.framework
        )
        
        # Save the mapping to database
        mapping = detector.save_mapping(
            db=db,
            prompt_id=request.prompt_id,
            detection_result=result,
            framework=request.framework
        )
        
        # Convert recommendations to response format
        recommendations = [
            ComponentRecommendationResponse(
                component_id=rec.component_id,
                component_name=rec.component_name,
                library_name=rec.library_name,
                confidence=rec.confidence,
                reason=rec.reason,
                code_example=rec.code_example
            )
            for rec in result.recommendations
        ]
        
        return DetectionResponse(
            intent=result.intent,
            recommendations=recommendations,
            overall_confidence=result.overall_confidence,
            suggested_framework=result.suggested_framework,
            mapping_id=mapping.id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component detection failed: {str(e)}")

@router.get("/libraries", response_model=List[ComponentLibraryResponse])
async def get_component_libraries(
    framework: Optional[str] = Query(None, description="Filter by framework"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100, description="Number of libraries to return"),
    db: Session = Depends(get_db)
):
    """Get available component libraries"""
    
    query = db.query(ComponentLibrary).filter(ComponentLibrary.is_active == True)
    
    if framework:
        query = query.filter(ComponentLibrary.framework == framework)
    
    if category:
        query = query.filter(ComponentLibrary.category == category)
    
    libraries = query.order_by(ComponentLibrary.popularity_score.desc()).limit(limit).all()
    
    return [ComponentLibraryResponse(**lib.to_dict()) for lib in libraries]

@router.get("/libraries/{library_id}/components", response_model=List[ComponentResponse])
async def get_library_components(
    library_id: int,
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Number of components to return"),
    db: Session = Depends(get_db)
):
    """Get components from a specific library"""
    
    # Verify library exists
    library = db.query(ComponentLibrary).filter(
        ComponentLibrary.id == library_id,
        ComponentLibrary.is_active == True
    ).first()
    
    if not library:
        raise HTTPException(status_code=404, detail="Component library not found")
    
    query = db.query(Component).filter(
        Component.library_id == library_id,
        Component.is_active == True
    )
    
    if category:
        query = query.filter(Component.category == category)
    
    components = query.order_by(Component.usage_count.desc()).limit(limit).all()
    
    return [ComponentResponse(**comp.to_dict()) for comp in components]

@router.get("/popular", response_model=List[Dict[str, Any]])
async def get_popular_components(
    framework: str = Query("react", description="Framework to get popular components for"),
    limit: int = Query(20, ge=1, le=50, description="Number of components to return"),
    db: Session = Depends(get_db)
):
    """Get most popular components for a framework"""
    
    popular_components = detector.get_popular_components(
        db=db,
        framework=framework,
        limit=limit
    )
    
    return popular_components

@router.post("/libraries", response_model=ComponentLibraryResponse)
async def create_component_library(
    library: ComponentLibraryCreate,
    db: Session = Depends(get_db)
):
    """Create a new component library"""
    
    # Check if library already exists
    existing = db.query(ComponentLibrary).filter(
        ComponentLibrary.name == library.name,
        ComponentLibrary.framework == library.framework
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Library '{library.name}' already exists for {library.framework}"
        )
    
    db_library = ComponentLibrary(
        name=library.name,
        description=library.description,
        framework=library.framework,
        version=library.version,
        npm_package=library.npm_package,
        cdn_url=library.cdn_url,
        documentation_url=library.documentation_url,
        import_statement=library.import_statement,
        css_imports=library.css_imports,
        dependencies=library.dependencies,
        tags=library.tags,
        category=library.category
    )
    
    db.add(db_library)
    db.commit()
    db.refresh(db_library)
    
    return ComponentLibraryResponse(**db_library.to_dict())

@router.post("/components", response_model=ComponentResponse)
async def create_component(
    component: ComponentCreate,
    db: Session = Depends(get_db)
):
    """Create a new component"""
    
    # Verify library exists
    library = db.query(ComponentLibrary).filter(
        ComponentLibrary.id == component.library_id
    ).first()
    
    if not library:
        raise HTTPException(status_code=404, detail="Component library not found")
    
    # Check if component already exists in this library
    existing = db.query(Component).filter(
        Component.library_id == component.library_id,
        Component.name == component.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Component '{component.name}' already exists in this library"
        )
    
    db_component = Component(
        library_id=component.library_id,
        name=component.name,
        display_name=component.display_name,
        description=component.description,
        category=component.category,
        component_code=component.component_code,
        props_schema=component.props_schema,
        examples=component.examples,
        detection_patterns=component.detection_patterns,
        keywords=component.keywords,
        complexity_level=component.complexity_level,
        tags=component.tags
    )
    
    db.add(db_component)
    db.commit()
    db.refresh(db_component)
    
    return ComponentResponse(**db_component.to_dict())

@router.put("/components/{component_id}/usage")
async def update_component_usage(
    component_id: int,
    success: bool = Query(True, description="Whether the component was used successfully"),
    db: Session = Depends(get_db)
):
    """Update component usage statistics"""
    
    detector.update_component_usage(db=db, component_id=component_id, success=success)
    
    return {"message": "Component usage updated successfully"}

@router.get("/mappings/{mapping_id}")
async def get_component_mapping(
    mapping_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific component mapping"""
    
    mapping = db.query(ComponentMapping).filter(
        ComponentMapping.id == mapping_id
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=404, detail="Component mapping not found")
    
    return mapping.to_dict()

@router.get("/frameworks")
async def get_supported_frameworks():
    """Get list of supported frameworks"""
    
    return {
        "frameworks": [
            {
                "name": "react",
                "display_name": "React",
                "description": "A JavaScript library for building user interfaces",
                "popular_libraries": ["Material-UI", "Ant Design", "Chakra UI", "React Bootstrap"]
            },
            {
                "name": "vue",
                "display_name": "Vue.js",
                "description": "The Progressive JavaScript Framework",
                "popular_libraries": ["Vuetify", "Quasar", "Element Plus", "Ant Design Vue"]
            },
            {
                "name": "angular",
                "display_name": "Angular",
                "description": "Platform for building mobile and desktop web applications",
                "popular_libraries": ["Angular Material", "PrimeNG", "Ng-Bootstrap", "Clarity"]
            }
        ]
    }