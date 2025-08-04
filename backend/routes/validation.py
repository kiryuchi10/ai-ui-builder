from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from services.ui_validator import UIValidator, ValidationResult

router = APIRouter(prefix="/api/v1/validation", tags=["validation"])
validator = UIValidator()

class ValidationRequest(BaseModel):
    code: str
    code_type: str = "react"  # react, html, vue, etc.

class ValidationIssue(BaseModel):
    type: str
    rule: str
    message: str
    severity: str
    line: int
    code_snippet: str

class ValidationResponse(BaseModel):
    score: float
    issues: List[ValidationIssue]
    suggestions: List[str]
    accessibility_score: float
    performance_score: float
    code_quality_score: float
    fixes: Optional[Dict[str, str]] = None

class FixRequest(BaseModel):
    code: str
    fix_types: List[str] = []  # Specific fixes to apply

@router.post("/validate", response_model=ValidationResponse)
async def validate_code(request: ValidationRequest):
    """Validate UI code for accessibility, performance, and quality issues"""
    
    try:
        result = validator.validate_code(request.code, request.code_type)
        
        # Convert issues to Pydantic models
        issues = [
            ValidationIssue(**issue) for issue in result.issues
        ]
        
        # Generate automatic fixes
        fixes = validator.generate_fixes(request.code, result.issues)
        
        return ValidationResponse(
            score=result.score,
            issues=issues,
            suggestions=result.suggestions,
            accessibility_score=result.accessibility_score,
            performance_score=result.performance_score,
            code_quality_score=result.code_quality_score,
            fixes=fixes if fixes else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/fix")
async def apply_fixes(request: FixRequest):
    """Apply automatic fixes to code"""
    
    try:
        # First validate to get issues
        result = validator.validate_code(request.code)
        
        # Generate fixes
        fixes = validator.generate_fixes(request.code, result.issues)
        
        # Apply requested fixes
        fixed_code = request.code
        for fix_type in request.fix_types:
            if fix_type in fixes:
                fixed_code = fixes[fix_type]
        
        # Validate the fixed code
        fixed_result = validator.validate_code(fixed_code)
        
        return {
            "original_code": request.code,
            "fixed_code": fixed_code,
            "original_score": result.score,
            "fixed_score": fixed_result.score,
            "improvements": {
                "accessibility": fixed_result.accessibility_score - result.accessibility_score,
                "performance": fixed_result.performance_score - result.performance_score,
                "code_quality": fixed_result.code_quality_score - result.code_quality_score
            },
            "applied_fixes": request.fix_types
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fix application failed: {str(e)}")

@router.get("/rules")
async def get_validation_rules():
    """Get all available validation rules"""
    
    return {
        "accessibility_rules": [
            {
                "rule": "alt_text_missing",
                "description": "Images should have alt text for accessibility",
                "severity": "high",
                "category": "accessibility"
            },
            {
                "rule": "button_without_text",
                "description": "Buttons should have descriptive text",
                "severity": "high",
                "category": "accessibility"
            },
            {
                "rule": "missing_aria_labels",
                "description": "Form inputs should have aria-label or aria-labelledby",
                "severity": "medium",
                "category": "accessibility"
            },
            {
                "rule": "semantic_html",
                "description": "Use semantic HTML elements for better accessibility",
                "severity": "medium",
                "category": "accessibility"
            }
        ],
        "performance_rules": [
            {
                "rule": "inline_styles",
                "description": "Avoid inline styles for better performance",
                "severity": "low",
                "category": "performance"
            },
            {
                "rule": "large_images",
                "description": "Consider optimizing images and using appropriate formats",
                "severity": "medium",
                "category": "performance"
            },
            {
                "rule": "missing_lazy_loading",
                "description": "Consider adding lazy loading for images",
                "severity": "low",
                "category": "performance"
            },
            {
                "rule": "missing_memoization",
                "description": "Consider using React.memo, useMemo, or useCallback",
                "severity": "low",
                "category": "performance"
            }
        ],
        "code_quality_rules": [
            {
                "rule": "unused_imports",
                "description": "Remove unused imports",
                "severity": "low",
                "category": "code_quality"
            },
            {
                "rule": "console_logs",
                "description": "Remove console statements in production code",
                "severity": "low",
                "category": "code_quality"
            },
            {
                "rule": "hardcoded_values",
                "description": "Consider using responsive units instead of fixed pixels",
                "severity": "medium",
                "category": "code_quality"
            },
            {
                "rule": "invalid_component_return",
                "description": "React components should return JSX",
                "severity": "high",
                "category": "code_quality"
            }
        ]
    }

@router.get("/score/{code_hash}")
async def get_validation_score(code_hash: str):
    """Get cached validation score for code (placeholder for future caching)"""
    
    # This would typically check a cache/database for previously validated code
    # For now, return a placeholder response
    return {
        "code_hash": code_hash,
        "cached": False,
        "message": "Code validation caching not implemented yet"
    }