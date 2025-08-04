"""
Accessibility Checker for AI UI Builder
Ensures WCAG compliance and inclusive design practices
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import colorsys
from ..security.audit_logger import audit_logger, AuditEventType, AuditSeverity

class WCAGLevel(Enum):
    """WCAG compliance levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"

class AccessibilityIssue(Enum):
    """Types of accessibility issues"""
    COLOR_CONTRAST = "color_contrast"
    MISSING_ALT_TEXT = "missing_alt_text"
    KEYBOARD_NAVIGATION = "keyboard_navigation"
    ARIA_LABELS = "aria_labels"
    HEADING_STRUCTURE = "heading_structure"
    FOCUS_INDICATORS = "focus_indicators"
    TEXT_SIZE = "text_size"
    TOUCH_TARGETS = "touch_targets"
    LANGUAGE_ATTRIBUTES = "language_attributes"
    FORM_LABELS = "form_labels"

@dataclass
class AccessibilityResult:
    """Accessibility check result"""
    level: WCAGLevel
    score: float
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    compliant: bool
    timestamp: datetime

class ColorContrastChecker:
    """Checks color contrast ratios for WCAG compliance"""
    
    def __init__(self):
        self.wcag_ratios = {
            WCAGLevel.A: {'normal': 3.0, 'large': 3.0},
            WCAGLevel.AA: {'normal': 4.5, 'large': 3.0},
            WCAGLevel.AAA: {'normal': 7.0, 'large': 4.5}
        }
    
    def check_contrast(self, foreground: str, background: str, 
                      font_size: int = 16, level: WCAGLevel = WCAGLevel.AA) -> Dict[str, Any]:
        """Check color contrast ratio"""
        try:
            # Calculate contrast ratio
            ratio = self._calculate_contrast_ratio(foreground, background)
            
            # Determine if text is large (18pt+ or 14pt+ bold)
            is_large_text = font_size >= 18
            
            # Get required ratio
            required_ratio = self.wcag_ratios[level]['large' if is_large_text else 'normal']
            
            # Check compliance
            compliant = ratio >= required_ratio
            
            result = {
                'ratio': round(ratio, 2),
                'required_ratio': required_ratio,
                'compliant': compliant,
                'level': level.value,
                'is_large_text': is_large_text,
                'foreground': foreground,
                'background': background
            }
            
            if not compliant:
                result['suggestion'] = self._suggest_contrast_fix(
                    foreground, background, required_ratio
                )
            
            return result
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.MEDIUM,
                action="check_color_contrast",
                result="error",
                details={"error": str(e)}
            )
            return {'error': str(e)}
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors"""
        luminance1 = self._get_luminance(color1)
        luminance2 = self._get_luminance(color2)
        
        # Ensure lighter color is in numerator
        if luminance1 < luminance2:
            luminance1, luminance2 = luminance2, luminance1
        
        return (luminance1 + 0.05) / (luminance2 + 0.05)
    
    def _get_luminance(self, color: str) -> float:
        """Calculate relative luminance of a color"""
        # Convert hex to RGB
        color = color.lstrip('#')
        rgb = [int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        
        # Apply gamma correction
        rgb_corrected = []
        for channel in rgb:
            if channel <= 0.03928:
                rgb_corrected.append(channel / 12.92)
            else:
                rgb_corrected.append(((channel + 0.055) / 1.055) ** 2.4)
        
        # Calculate luminance
        return 0.2126 * rgb_corrected[0] + 0.7152 * rgb_corrected[1] + 0.0722 * rgb_corrected[2]
    
    def _suggest_contrast_fix(self, foreground: str, background: str, 
                            required_ratio: float) -> str:
        """Suggest color adjustments to meet contrast requirements"""
        current_ratio = self._calculate_contrast_ratio(foreground, background)
        
        if current_ratio < required_ratio:
            # Try darkening foreground or lightening background
            fg_luminance = self._get_luminance(foreground)
            bg_luminance = self._get_luminance(background)
            
            if fg_luminance > bg_luminance:
                return f"Consider darkening the text color or lightening the background to achieve a {required_ratio}:1 contrast ratio"
            else:
                return f"Consider lightening the text color or darkening the background to achieve a {required_ratio}:1 contrast ratio"
        
        return "Color contrast is sufficient"

class AccessibilityChecker:
    """Main accessibility checker class"""
    
    def __init__(self):
        self.contrast_checker = ColorContrastChecker()
        self.checks = {
            AccessibilityIssue.COLOR_CONTRAST: self._check_color_contrast,
            AccessibilityIssue.MISSING_ALT_TEXT: self._check_alt_text,
            AccessibilityIssue.KEYBOARD_NAVIGATION: self._check_keyboard_navigation,
            AccessibilityIssue.ARIA_LABELS: self._check_aria_labels,
            AccessibilityIssue.HEADING_STRUCTURE: self._check_heading_structure,
            AccessibilityIssue.FOCUS_INDICATORS: self._check_focus_indicators,
            AccessibilityIssue.TEXT_SIZE: self._check_text_size,
            AccessibilityIssue.TOUCH_TARGETS: self._check_touch_targets,
            AccessibilityIssue.LANGUAGE_ATTRIBUTES: self._check_language_attributes,
            AccessibilityIssue.FORM_LABELS: self._check_form_labels
        }
    
    def check_accessibility(self, html_content: str, css_content: str = "",
                          level: WCAGLevel = WCAGLevel.AA) -> AccessibilityResult:
        """Perform comprehensive accessibility check"""
        try:
            issues = []
            suggestions = []
            
            # Run all accessibility checks
            for issue_type, check_function in self.checks.items():
                check_result = check_function(html_content, css_content, level)
                if check_result['issues']:
                    issues.extend(check_result['issues'])
                if check_result['suggestions']:
                    suggestions.extend(check_result['suggestions'])
            
            # Calculate overall score
            total_checks = len(self.checks)
            failed_checks = len(set(issue['type'] for issue in issues))
            score = ((total_checks - failed_checks) / total_checks) * 100
            
            # Determine compliance
            compliant = len(issues) == 0
            
            result = AccessibilityResult(
                level=level,
                score=round(score, 2),
                issues=issues,
                suggestions=list(set(suggestions)),  # Remove duplicates
                compliant=compliant,
                timestamp=datetime.utcnow()
            )
            
            audit_logger.log_event(
                event_type=AuditEventType.DATA_ACCESS,
                severity=AuditSeverity.LOW,
                action="accessibility_check",
                result="completed",
                details={
                    "level": level.value,
                    "score": result.score,
                    "issues_count": len(issues),
                    "compliant": compliant
                }
            )
            
            return result
            
        except Exception as e:
            audit_logger.log_event(
                event_type=AuditEventType.SYSTEM_ERROR,
                severity=AuditSeverity.HIGH,
                action="accessibility_check",
                result="error",
                details={"error": str(e)}
            )
            raise
    
    def _check_color_contrast(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check color contrast ratios"""
        issues = []
        suggestions = []
        
        # Extract color combinations from CSS
        color_patterns = re.findall(r'color:\s*([#\w]+).*?background(?:-color)?:\s*([#\w]+)', css, re.IGNORECASE)
        
        for fg_color, bg_color in color_patterns:
            if fg_color.startswith('#') and bg_color.startswith('#'):
                contrast_result = self.contrast_checker.check_contrast(fg_color, bg_color, level=level)
                
                if not contrast_result.get('compliant', True):
                    issues.append({
                        'type': AccessibilityIssue.COLOR_CONTRAST.value,
                        'severity': 'high',
                        'message': f"Insufficient color contrast: {contrast_result['ratio']}:1 (required: {contrast_result['required_ratio']}:1)",
                        'element': f"color: {fg_color}, background: {bg_color}",
                        'suggestion': contrast_result.get('suggestion', '')
                    })
                    
                    suggestions.append(contrast_result.get('suggestion', ''))
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_alt_text(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check for missing alt text on images"""
        issues = []
        suggestions = []
        
        # Find img tags without alt attributes or with empty alt
        img_pattern = r'<img[^>]*(?:(?!alt=)[^>])*>'
        missing_alt_images = re.findall(img_pattern, html, re.IGNORECASE)
        
        for img_tag in missing_alt_images:
            issues.append({
                'type': AccessibilityIssue.MISSING_ALT_TEXT.value,
                'severity': 'high',
                'message': 'Image missing alt text',
                'element': img_tag,
                'suggestion': 'Add descriptive alt text to all images'
            })
        
        if missing_alt_images:
            suggestions.append('Add descriptive alt text to all images for screen reader users')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_keyboard_navigation(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check keyboard navigation support"""
        issues = []
        suggestions = []
        
        # Check for interactive elements without tabindex or proper focus handling
        interactive_elements = re.findall(r'<(button|a|input|select|textarea)[^>]*>', html, re.IGNORECASE)
        
        for element in interactive_elements:
            if 'tabindex="-1"' in element.lower():
                issues.append({
                    'type': AccessibilityIssue.KEYBOARD_NAVIGATION.value,
                    'severity': 'medium',
                    'message': 'Interactive element removed from tab order',
                    'element': element,
                    'suggestion': 'Ensure all interactive elements are keyboard accessible'
                })
        
        # Check for custom interactive elements without proper ARIA
        custom_interactive = re.findall(r'<div[^>]*onclick[^>]*>', html, re.IGNORECASE)
        for element in custom_interactive:
            if 'role=' not in element.lower() or 'tabindex=' not in element.lower():
                issues.append({
                    'type': AccessibilityIssue.KEYBOARD_NAVIGATION.value,
                    'severity': 'high',
                    'message': 'Custom interactive element lacks proper keyboard support',
                    'element': element,
                    'suggestion': 'Add role and tabindex attributes to custom interactive elements'
                })
        
        if issues:
            suggestions.append('Ensure all interactive elements are keyboard accessible with proper focus management')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_aria_labels(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check for proper ARIA labels"""
        issues = []
        suggestions = []
        
        # Check for form inputs without labels
        input_pattern = r'<input[^>]*type=["\'](?!hidden)[^"\']*["\'][^>]*>'
        inputs = re.findall(input_pattern, html, re.IGNORECASE)
        
        for input_tag in inputs:
            if 'aria-label=' not in input_tag.lower() and 'aria-labelledby=' not in input_tag.lower():
                # Check if there's an associated label
                input_id_match = re.search(r'id=["\']([^"\']*)["\']', input_tag)
                if input_id_match:
                    input_id = input_id_match.group(1)
                    label_pattern = f'<label[^>]*for=["\']?{input_id}["\']?[^>]*>'
                    if not re.search(label_pattern, html, re.IGNORECASE):
                        issues.append({
                            'type': AccessibilityIssue.ARIA_LABELS.value,
                            'severity': 'high',
                            'message': 'Form input lacks proper labeling',
                            'element': input_tag,
                            'suggestion': 'Add aria-label or associate with a label element'
                        })
        
        if issues:
            suggestions.append('Ensure all form inputs have proper labels or ARIA attributes')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_heading_structure(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check heading hierarchy"""
        issues = []
        suggestions = []
        
        # Extract all headings
        heading_pattern = r'<h([1-6])[^>]*>'
        headings = re.findall(heading_pattern, html, re.IGNORECASE)
        
        if headings:
            heading_levels = [int(h) for h in headings]
            
            # Check if starts with h1
            if heading_levels[0] != 1:
                issues.append({
                    'type': AccessibilityIssue.HEADING_STRUCTURE.value,
                    'severity': 'medium',
                    'message': 'Page should start with h1 heading',
                    'element': f'<h{heading_levels[0]}>',
                    'suggestion': 'Start page with h1 and maintain logical heading hierarchy'
                })
            
            # Check for skipped levels
            for i in range(1, len(heading_levels)):
                if heading_levels[i] > heading_levels[i-1] + 1:
                    issues.append({
                        'type': AccessibilityIssue.HEADING_STRUCTURE.value,
                        'severity': 'medium',
                        'message': f'Heading level skipped from h{heading_levels[i-1]} to h{heading_levels[i]}',
                        'element': f'<h{heading_levels[i]}>',
                        'suggestion': 'Maintain logical heading hierarchy without skipping levels'
                    })
        
        if issues:
            suggestions.append('Maintain proper heading hierarchy (h1 → h2 → h3, etc.) for screen reader navigation')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_focus_indicators(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check for focus indicators"""
        issues = []
        suggestions = []
        
        # Check if focus styles are removed
        if 'outline:none' in css.replace(' ', '') or 'outline:0' in css.replace(' ', ''):
            if ':focus' not in css:
                issues.append({
                    'type': AccessibilityIssue.FOCUS_INDICATORS.value,
                    'severity': 'high',
                    'message': 'Focus indicators removed without custom alternatives',
                    'element': 'CSS outline: none',
                    'suggestion': 'Provide custom focus indicators when removing default outline'
                })
                
                suggestions.append('Always provide visible focus indicators for keyboard navigation')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_text_size(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check minimum text size"""
        issues = []
        suggestions = []
        
        # Check for text smaller than 12px
        font_size_pattern = r'font-size:\s*(\d+(?:\.\d+)?)px'
        font_sizes = re.findall(font_size_pattern, css, re.IGNORECASE)
        
        for size in font_sizes:
            if float(size) < 12:
                issues.append({
                    'type': AccessibilityIssue.TEXT_SIZE.value,
                    'severity': 'medium',
                    'message': f'Text size too small: {size}px',
                    'element': f'font-size: {size}px',
                    'suggestion': 'Use minimum 12px font size for body text'
                })
        
        if issues:
            suggestions.append('Ensure text is large enough to read comfortably (minimum 12px)')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_touch_targets(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check touch target sizes"""
        issues = []
        suggestions = []
        
        # This would require more sophisticated parsing to check actual computed sizes
        # For now, check for common small interactive elements
        small_buttons = re.findall(r'<button[^>]*style=["\'][^"\']*(?:width|height):\s*(?:[1-3]?\d)px[^"\']*["\'][^>]*>', html, re.IGNORECASE)
        
        for button in small_buttons:
            issues.append({
                'type': AccessibilityIssue.TOUCH_TARGETS.value,
                'severity': 'medium',
                'message': 'Touch target may be too small',
                'element': button,
                'suggestion': 'Ensure touch targets are at least 44x44px'
            })
        
        if issues:
            suggestions.append('Make touch targets at least 44x44px for mobile accessibility')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_language_attributes(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check for language attributes"""
        issues = []
        suggestions = []
        
        if '<html' in html and 'lang=' not in html:
            issues.append({
                'type': AccessibilityIssue.LANGUAGE_ATTRIBUTES.value,
                'severity': 'medium',
                'message': 'Missing lang attribute on html element',
                'element': '<html>',
                'suggestion': 'Add lang attribute to html element (e.g., lang="en")'
            })
            
            suggestions.append('Add language attributes to help screen readers pronounce content correctly')
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _check_form_labels(self, html: str, css: str, level: WCAGLevel) -> Dict[str, Any]:
        """Check form label associations"""
        issues = []
        suggestions = []
        
        # Find form inputs
        inputs = re.findall(r'<input[^>]*>', html, re.IGNORECASE)
        
        for input_tag in inputs:
            if 'type="hidden"' in input_tag.lower():
                continue
                
            # Check for proper labeling
            has_label = False
            
            # Check for aria-label
            if 'aria-label=' in input_tag.lower():
                has_label = True
            
            # Check for associated label
            id_match = re.search(r'id=["\']([^"\']*)["\']', input_tag)
            if id_match:
                input_id = id_match.group(1)
                label_pattern = f'<label[^>]*for=["\']?{input_id}["\']?[^>]*>'
                if re.search(label_pattern, html, re.IGNORECASE):
                    has_label = True
            
            if not has_label:
                issues.append({
                    'type': AccessibilityIssue.FORM_LABELS.value,
                    'severity': 'high',
                    'message': 'Form input lacks proper label',
                    'element': input_tag,
                    'suggestion': 'Associate form inputs with labels using for/id or aria-label'
                })
        
        if issues:
            suggestions.append('Ensure all form inputs have proper labels for screen reader users')
        
        return {'issues': issues, 'suggestions': suggestions}

# Global accessibility checker instance
accessibility_checker = AccessibilityChecker()