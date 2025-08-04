import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import ast

@dataclass
class ValidationResult:
    score: float  # 0-10 scale
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    accessibility_score: float
    performance_score: float
    code_quality_score: float

class UIValidator:
    """LLM-based UI code validator with accessibility and performance checks"""
    
    def __init__(self):
        self.accessibility_rules = [
            {
                "rule": "alt_text_missing",
                "pattern": r'<img(?![^>]*alt=)[^>]*>',
                "message": "Images should have alt text for accessibility",
                "severity": "high"
            },
            {
                "rule": "button_without_text",
                "pattern": r'<button[^>]*>\s*</button>',
                "message": "Buttons should have descriptive text",
                "severity": "high"
            },
            {
                "rule": "missing_aria_labels",
                "pattern": r'<input(?![^>]*aria-label)(?![^>]*aria-labelledby)[^>]*>',
                "message": "Form inputs should have aria-label or aria-labelledby",
                "severity": "medium"
            },
            {
                "rule": "low_contrast_colors",
                "pattern": r'color:\s*#([a-fA-F0-9]{3,6})',
                "message": "Ensure sufficient color contrast for accessibility",
                "severity": "medium"
            }
        ]
        
        self.performance_rules = [
            {
                "rule": "inline_styles",
                "pattern": r'style=',
                "message": "Avoid inline styles for better performance and maintainability",
                "severity": "low"
            },
            {
                "rule": "large_images",
                "pattern": r'<img[^>]*src=["\'][^"\']*\.(jpg|jpeg|png|gif)["\'][^>]*>',
                "message": "Consider optimizing images and using appropriate formats",
                "severity": "medium"
            },
            {
                "rule": "missing_lazy_loading",
                "pattern": r'<img(?![^>]*loading=)[^>]*>',
                "message": "Consider adding lazy loading for images",
                "severity": "low"
            }
        ]
        
        self.code_quality_rules = [
            {
                "rule": "unused_imports",
                "pattern": r'import\s+\w+.*?;',
                "message": "Remove unused imports",
                "severity": "low"
            },
            {
                "rule": "console_logs",
                "pattern": r'console\.(log|warn|error)',
                "message": "Remove console statements in production code",
                "severity": "low"
            },
            {
                "rule": "hardcoded_values",
                "pattern": r'(width|height|margin|padding):\s*\d+px',
                "message": "Consider using responsive units instead of fixed pixels",
                "severity": "medium"
            }
        ]
    
    def validate_code(self, code: str, code_type: str = "react") -> ValidationResult:
        """Validate UI code and return comprehensive results"""
        
        issues = []
        suggestions = []
        
        # Run accessibility checks
        accessibility_issues = self._check_accessibility(code)
        issues.extend(accessibility_issues)
        
        # Run performance checks
        performance_issues = self._check_performance(code)
        issues.extend(performance_issues)
        
        # Run code quality checks
        quality_issues = self._check_code_quality(code)
        issues.extend(quality_issues)
        
        # Calculate scores
        accessibility_score = self._calculate_accessibility_score(accessibility_issues)
        performance_score = self._calculate_performance_score(performance_issues)
        code_quality_score = self._calculate_code_quality_score(quality_issues)
        
        # Overall score (weighted average)
        overall_score = (
            accessibility_score * 0.4 +
            performance_score * 0.3 +
            code_quality_score * 0.3
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(issues, code)
        
        return ValidationResult(
            score=round(overall_score, 1),
            issues=issues,
            suggestions=suggestions,
            accessibility_score=round(accessibility_score, 1),
            performance_score=round(performance_score, 1),
            code_quality_score=round(code_quality_score, 1)
        )
    
    def _check_accessibility(self, code: str) -> List[Dict[str, Any]]:
        """Check accessibility issues in the code"""
        issues = []
        
        for rule in self.accessibility_rules:
            matches = re.finditer(rule["pattern"], code, re.IGNORECASE)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "accessibility",
                    "rule": rule["rule"],
                    "message": rule["message"],
                    "severity": rule["severity"],
                    "line": line_number,
                    "code_snippet": self._get_code_snippet(code, match.start(), match.end())
                })
        
        # Check for semantic HTML
        if not re.search(r'<(header|nav|main|section|article|aside|footer)', code, re.IGNORECASE):
            issues.append({
                "type": "accessibility",
                "rule": "semantic_html",
                "message": "Use semantic HTML elements for better accessibility",
                "severity": "medium",
                "line": 1,
                "code_snippet": "Consider using semantic elements like <header>, <nav>, <main>, etc."
            })
        
        return issues
    
    def _check_performance(self, code: str) -> List[Dict[str, Any]]:
        """Check performance issues in the code"""
        issues = []
        
        for rule in self.performance_rules:
            matches = re.finditer(rule["pattern"], code, re.IGNORECASE)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "performance",
                    "rule": rule["rule"],
                    "message": rule["message"],
                    "severity": rule["severity"],
                    "line": line_number,
                    "code_snippet": self._get_code_snippet(code, match.start(), match.end())
                })
        
        # Check for React-specific performance issues
        if "React" in code:
            # Check for missing React.memo or useMemo
            if re.search(r'function\s+\w+\s*\(', code) and not re.search(r'React\.memo|useMemo|useCallback', code):
                issues.append({
                    "type": "performance",
                    "rule": "missing_memoization",
                    "message": "Consider using React.memo, useMemo, or useCallback for performance optimization",
                    "severity": "low",
                    "line": 1,
                    "code_snippet": "Add memoization for expensive computations"
                })
        
        return issues
    
    def _check_code_quality(self, code: str) -> List[Dict[str, Any]]:
        """Check code quality issues"""
        issues = []
        
        for rule in self.code_quality_rules:
            matches = re.finditer(rule["pattern"], code, re.IGNORECASE)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "type": "code_quality",
                    "rule": rule["rule"],
                    "message": rule["message"],
                    "severity": rule["severity"],
                    "line": line_number,
                    "code_snippet": self._get_code_snippet(code, match.start(), match.end())
                })
        
        # Check for proper component structure
        if "function" in code and "return" in code:
            # Check if component returns JSX
            if not re.search(r'return\s*\(?\s*<', code):
                issues.append({
                    "type": "code_quality",
                    "rule": "invalid_component_return",
                    "message": "React components should return JSX",
                    "severity": "high",
                    "line": 1,
                    "code_snippet": "Ensure component returns valid JSX"
                })
        
        return issues
    
    def _calculate_accessibility_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate accessibility score based on issues"""
        accessibility_issues = [issue for issue in issues if issue["type"] == "accessibility"]
        
        if not accessibility_issues:
            return 10.0
        
        penalty = 0
        for issue in accessibility_issues:
            if issue["severity"] == "high":
                penalty += 2.0
            elif issue["severity"] == "medium":
                penalty += 1.0
            else:
                penalty += 0.5
        
        return max(0.0, 10.0 - penalty)
    
    def _calculate_performance_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate performance score based on issues"""
        performance_issues = [issue for issue in issues if issue["type"] == "performance"]
        
        if not performance_issues:
            return 10.0
        
        penalty = 0
        for issue in performance_issues:
            if issue["severity"] == "high":
                penalty += 1.5
            elif issue["severity"] == "medium":
                penalty += 1.0
            else:
                penalty += 0.5
        
        return max(0.0, 10.0 - penalty)
    
    def _calculate_code_quality_score(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate code quality score based on issues"""
        quality_issues = [issue for issue in issues if issue["type"] == "code_quality"]
        
        if not quality_issues:
            return 10.0
        
        penalty = 0
        for issue in quality_issues:
            if issue["severity"] == "high":
                penalty += 2.0
            elif issue["severity"] == "medium":
                penalty += 1.0
            else:
                penalty += 0.5
        
        return max(0.0, 10.0 - penalty)
    
    def _generate_suggestions(self, issues: List[Dict[str, Any]], code: str) -> List[str]:
        """Generate improvement suggestions based on issues"""
        suggestions = []
        
        # Group issues by type
        accessibility_issues = [i for i in issues if i["type"] == "accessibility"]
        performance_issues = [i for i in issues if i["type"] == "performance"]
        quality_issues = [i for i in issues if i["type"] == "code_quality"]
        
        if accessibility_issues:
            suggestions.append("🔍 Accessibility: Add alt text to images, use semantic HTML, and ensure proper ARIA labels")
        
        if performance_issues:
            suggestions.append("⚡ Performance: Optimize images, avoid inline styles, and consider lazy loading")
        
        if quality_issues:
            suggestions.append("🛠️ Code Quality: Remove console logs, use responsive units, and clean up unused imports")
        
        # Add general suggestions
        if "className" in code:
            suggestions.append("🎨 Styling: Consider using CSS modules or styled-components for better maintainability")
        
        if len(code.split('\n')) > 50:
            suggestions.append("📦 Structure: Consider breaking down large components into smaller, reusable pieces")
        
        return suggestions
    
    def _get_code_snippet(self, code: str, start: int, end: int, context: int = 20) -> str:
        """Get a code snippet with context around the issue"""
        snippet_start = max(0, start - context)
        snippet_end = min(len(code), end + context)
        return code[snippet_start:snippet_end].strip()
    
    def generate_fixes(self, code: str, issues: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate automatic fixes for common issues"""
        fixes = {}
        
        for issue in issues:
            if issue["rule"] == "alt_text_missing":
                # Add alt text to images
                fixed_code = re.sub(
                    r'<img([^>]*)>',
                    r'<img\1 alt="Description of image">',
                    code
                )
                fixes["alt_text_fix"] = fixed_code
            
            elif issue["rule"] == "console_logs":
                # Remove console logs
                fixed_code = re.sub(
                    r'console\.(log|warn|error)\([^)]*\);?\n?',
                    '',
                    code
                )
                fixes["console_log_fix"] = fixed_code
        
        return fixes