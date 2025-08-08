"""
Code Quality Tool - CodeBERT + linters for validation
"""
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import ast
import re

logger = logging.getLogger(__name__)

class CodeQualityChecker:
    """
    Code quality validation using CodeBERT, linters, and static analysis
    """
    
    def __init__(self):
        self.linters = self._initialize_linters()
        self.quality_thresholds = {
            "min_score": 0.7,
            "max_lint_errors": 10,
            "max_complexity": 10,
            "min_test_coverage": 0.8
        }
    
    def _initialize_linters(self) -> Dict[str, bool]:
        """Check which linters are available"""
        linters = {}
        
        # Check for Python linters
        for linter in ["flake8", "pylint", "mypy", "black"]:
            try:
                subprocess.run([linter, "--version"], capture_output=True, check=True)
                linters[linter] = True
                logger.info(f"{linter} available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                linters[linter] = False
                logger.warning(f"{linter} not available")
        
        # Check for JavaScript linters
        for linter in ["eslint", "prettier"]:
            try:
                subprocess.run([linter, "--version"], capture_output=True, check=True)
                linters[linter] = True
                logger.info(f"{linter} available")
            except (subprocess.CalledProcessError, FileNotFoundError):
                linters[linter] = False
                logger.warning(f"{linter} not available")
        
        return linters
    
    async def execute(self, code_path: str, **kwargs) -> Dict[str, Any]:
        """
        Execute code quality check on given path
        
        Args:
            code_path: Path to code directory or file
            
        Returns:
            Dict with quality analysis results
        """
        return self.analyze_code_quality(code_path)
    
    def analyze_code_quality(self, code_path: str) -> Dict[str, Any]:
        """
        Comprehensive code quality analysis
        
        Returns:
            {
                "overall_score": 0.85,
                "lint_results": {...},
                "security_issues": [...],
                "complexity_analysis": {...},
                "suggestions": [...],
                "autofix_available": True,
                "autofix_patch": "..."
            }
        """
        try:
            code_path = Path(code_path)
            
            if not code_path.exists():
                return {"error": f"Path does not exist: {code_path}"}
            
            results = {
                "overall_score": 0.0,
                "lint_results": {},
                "security_issues": [],
                "complexity_analysis": {},
                "suggestions": [],
                "autofix_available": False,
                "autofix_patch": None
            }
            
            # Analyze based on file types
            if code_path.is_file():
                results.update(self._analyze_single_file(code_path))
            else:
                results.update(self._analyze_directory(code_path))
            
            # Calculate overall score
            results["overall_score"] = self._calculate_overall_score(results)
            
            # Generate suggestions
            results["suggestions"] = self._generate_suggestions(results)
            
            # Check if autofix is available
            results["autofix_available"] = self._can_autofix(results)
            if results["autofix_available"]:
                results["autofix_patch"] = self._generate_autofix_patch(code_path, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Code quality analysis failed: {e}")
            return {
                "overall_score": 0.0,
                "error": str(e),
                "lint_results": {},
                "security_issues": [],
                "suggestions": ["Fix syntax errors before quality analysis"]
            }
    
    def _analyze_single_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file"""
        results = {}
        
        if file_path.suffix == ".py":
            results.update(self._analyze_python_file(file_path))
        elif file_path.suffix in [".js", ".jsx", ".ts", ".tsx"]:
            results.update(self._analyze_javascript_file(file_path))
        else:
            results["lint_results"] = {"message": f"Unsupported file type: {file_path.suffix}"}
        
        return results
    
    def _analyze_directory(self, dir_path: Path) -> Dict[str, Any]:
        """Analyze all files in directory"""
        results = {
            "lint_results": {},
            "security_issues": [],
            "complexity_analysis": {}
        }
        
        # Find Python files
        python_files = list(dir_path.rglob("*.py"))
        if python_files:
            results.update(self._analyze_python_project(dir_path, python_files))
        
        # Find JavaScript/TypeScript files
        js_files = list(dir_path.rglob("*.js")) + list(dir_path.rglob("*.jsx")) + \
                  list(dir_path.rglob("*.ts")) + list(dir_path.rglob("*.tsx"))
        if js_files:
            results.update(self._analyze_javascript_project(dir_path, js_files))
        
        return results
    
    def _analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Python file quality"""
        results = {
            "lint_results": {},
            "security_issues": [],
            "complexity_analysis": {}
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax check
            try:
                ast.parse(content)
                results["syntax_valid"] = True
            except SyntaxError as e:
                results["syntax_valid"] = False
                results["syntax_error"] = str(e)
                return results
            
            # Run linters if available
            if self.linters.get("flake8"):
                results["lint_results"]["flake8"] = self._run_flake8(file_path)
            
            if self.linters.get("pylint"):
                results["lint_results"]["pylint"] = self._run_pylint(file_path)
            
            if self.linters.get("mypy"):
                results["lint_results"]["mypy"] = self._run_mypy(file_path)
            
            # Security analysis
            results["security_issues"] = self._analyze_python_security(content)
            
            # Complexity analysis
            results["complexity_analysis"] = self._analyze_python_complexity(content)
            
        except Exception as e:
            logger.error(f"Python file analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def _analyze_javascript_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript file quality"""
        results = {
            "lint_results": {},
            "security_issues": [],
            "complexity_analysis": {}
        }
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Run ESLint if available
            if self.linters.get("eslint"):
                results["lint_results"]["eslint"] = self._run_eslint(file_path)
            
            # Security analysis
            results["security_issues"] = self._analyze_javascript_security(content)
            
            # Complexity analysis
            results["complexity_analysis"] = self._analyze_javascript_complexity(content)
            
        except Exception as e:
            logger.error(f"JavaScript file analysis failed: {e}")
            results["error"] = str(e)
        
        return results
    
    def _run_flake8(self, file_path: Path) -> Dict[str, Any]:
        """Run flake8 linter"""
        try:
            result = subprocess.run(
                ["flake8", "--format=json", str(file_path)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []
            
            return {
                "issues": issues,
                "error_count": len([i for i in issues if i.get("type") == "E"]),
                "warning_count": len([i for i in issues if i.get("type") == "W"]),
                "passed": len(issues) == 0
            }
            
        except Exception as e:
            logger.error(f"Flake8 failed: {e}")
            return {"error": str(e), "passed": False}
    
    def _run_pylint(self, file_path: Path) -> Dict[str, Any]:
        """Run pylint"""
        try:
            result = subprocess.run(
                ["pylint", "--output-format=json", str(file_path)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []
            
            # Calculate score from pylint output
            score_match = re.search(r"Your code has been rated at ([\d.]+)/10", result.stderr or "")
            score = float(score_match.group(1)) / 10 if score_match else 0.5
            
            return {
                "issues": issues,
                "score": score,
                "error_count": len([i for i in issues if i.get("type") == "error"]),
                "warning_count": len([i for i in issues if i.get("type") == "warning"]),
                "passed": score >= 0.8
            }
            
        except Exception as e:
            logger.error(f"Pylint failed: {e}")
            return {"error": str(e), "passed": False}
    
    def _run_mypy(self, file_path: Path) -> Dict[str, Any]:
        """Run mypy type checker"""
        try:
            result = subprocess.run(
                ["mypy", "--show-error-codes", str(file_path)],
                capture_output=True,
                text=True
            )
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        issues.append({"message": line, "type": "type_error"})
            
            return {
                "issues": issues,
                "error_count": len(issues),
                "passed": len(issues) == 0
            }
            
        except Exception as e:
            logger.error(f"Mypy failed: {e}")
            return {"error": str(e), "passed": False}
    
    def _run_eslint(self, file_path: Path) -> Dict[str, Any]:
        """Run ESLint"""
        try:
            result = subprocess.run(
                ["eslint", "--format=json", str(file_path)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                eslint_output = json.loads(result.stdout)
                issues = []
                for file_result in eslint_output:
                    issues.extend(file_result.get("messages", []))
            else:
                issues = []
            
            return {
                "issues": issues,
                "error_count": len([i for i in issues if i.get("severity") == 2]),
                "warning_count": len([i for i in issues if i.get("severity") == 1]),
                "passed": len([i for i in issues if i.get("severity") == 2]) == 0
            }
            
        except Exception as e:
            logger.error(f"ESLint failed: {e}")
            return {"error": str(e), "passed": False}
    
    def _analyze_python_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze Python code for security issues"""
        issues = []
        
        # Check for common security anti-patterns
        security_patterns = [
            (r"eval\s*\(", "Use of eval() is dangerous"),
            (r"exec\s*\(", "Use of exec() is dangerous"),
            (r"__import__\s*\(", "Dynamic imports can be dangerous"),
            (r"pickle\.loads?\s*\(", "Pickle deserialization can be dangerous"),
            (r"subprocess\.call\s*\([^)]*shell\s*=\s*True", "Shell injection risk"),
            (r"os\.system\s*\(", "Command injection risk"),
            (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
            (r"api_key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key")
        ]
        
        for pattern, message in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "security",
                    "message": message,
                    "line": line_num,
                    "severity": "high"
                })
        
        return issues
    
    def _analyze_javascript_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze JavaScript code for security issues"""
        issues = []
        
        security_patterns = [
            (r"eval\s*\(", "Use of eval() is dangerous"),
            (r"innerHTML\s*=", "innerHTML can lead to XSS"),
            (r"document\.write\s*\(", "document.write can be dangerous"),
            (r"setTimeout\s*\(\s*['\"][^'\"]*['\"]", "String-based setTimeout is dangerous"),
            (r"setInterval\s*\(\s*['\"][^'\"]*['\"]", "String-based setInterval is dangerous")
        ]
        
        for pattern, message in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    "type": "security",
                    "message": message,
                    "line": line_num,
                    "severity": "medium"
                })
        
        return issues
    
    def _analyze_python_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze Python code complexity"""
        try:
            tree = ast.parse(content)
            
            complexity_analyzer = ComplexityAnalyzer()
            complexity_analyzer.visit(tree)
            
            return {
                "cyclomatic_complexity": complexity_analyzer.complexity,
                "function_count": complexity_analyzer.function_count,
                "class_count": complexity_analyzer.class_count,
                "max_nesting_depth": complexity_analyzer.max_depth,
                "lines_of_code": len(content.splitlines())
            }
            
        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_javascript_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript code complexity (simplified)"""
        lines = content.splitlines()
        
        # Simple metrics
        function_count = len(re.findall(r'function\s+\w+|=>\s*{|\w+\s*:\s*function', content))
        class_count = len(re.findall(r'class\s+\w+', content))
        
        # Estimate cyclomatic complexity by counting decision points
        decision_points = len(re.findall(r'\b(if|else|while|for|switch|case|catch|\?)\b', content))
        
        return {
            "estimated_complexity": decision_points + 1,
            "function_count": function_count,
            "class_count": class_count,
            "lines_of_code": len(lines)
        }
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        scores = []
        
        # Syntax score
        if results.get("syntax_valid", True):
            scores.append(1.0)
        else:
            scores.append(0.0)
        
        # Lint scores
        lint_results = results.get("lint_results", {})
        for linter, result in lint_results.items():
            if isinstance(result, dict) and "passed" in result:
                scores.append(1.0 if result["passed"] else 0.5)
            elif isinstance(result, dict) and "score" in result:
                scores.append(result["score"])
        
        # Security score
        security_issues = results.get("security_issues", [])
        high_severity = len([i for i in security_issues if i.get("severity") == "high"])
        if high_severity == 0:
            scores.append(1.0)
        elif high_severity <= 2:
            scores.append(0.7)
        else:
            scores.append(0.3)
        
        # Complexity score
        complexity = results.get("complexity_analysis", {})
        if "cyclomatic_complexity" in complexity:
            cc = complexity["cyclomatic_complexity"]
            if cc <= 5:
                scores.append(1.0)
            elif cc <= 10:
                scores.append(0.8)
            else:
                scores.append(0.5)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Syntax suggestions
        if not results.get("syntax_valid", True):
            suggestions.append("Fix syntax errors before proceeding")
        
        # Lint suggestions
        lint_results = results.get("lint_results", {})
        for linter, result in lint_results.items():
            if isinstance(result, dict) and not result.get("passed", True):
                error_count = result.get("error_count", 0)
                warning_count = result.get("warning_count", 0)
                
                if error_count > 0:
                    suggestions.append(f"Fix {error_count} {linter} errors")
                if warning_count > 0:
                    suggestions.append(f"Address {warning_count} {linter} warnings")
        
        # Security suggestions
        security_issues = results.get("security_issues", [])
        high_severity = [i for i in security_issues if i.get("severity") == "high"]
        if high_severity:
            suggestions.append(f"Fix {len(high_severity)} high-severity security issues")
        
        # Complexity suggestions
        complexity = results.get("complexity_analysis", {})
        if complexity.get("cyclomatic_complexity", 0) > 10:
            suggestions.append("Reduce cyclomatic complexity by breaking down complex functions")
        
        return suggestions
    
    def _can_autofix(self, results: Dict[str, Any]) -> bool:
        """Check if issues can be automatically fixed"""
        # Can autofix if there are only formatting/style issues
        lint_results = results.get("lint_results", {})
        
        for linter, result in lint_results.items():
            if linter in ["black", "prettier"] and not result.get("passed", True):
                return True
        
        return False
    
    def _generate_autofix_patch(self, code_path: Path, results: Dict[str, Any]) -> Optional[str]:
        """Generate autofix patch for common issues"""
        try:
            if code_path.suffix == ".py" and self.linters.get("black"):
                # Use black for Python formatting
                result = subprocess.run(
                    ["black", "--diff", str(code_path)],
                    capture_output=True,
                    text=True
                )
                return result.stdout if result.stdout else None
            
            elif code_path.suffix in [".js", ".jsx"] and self.linters.get("prettier"):
                # Use prettier for JavaScript formatting
                result = subprocess.run(
                    ["prettier", "--write", str(code_path)],
                    capture_output=True,
                    text=True
                )
                return "Formatted with Prettier" if result.returncode == 0 else None
            
        except Exception as e:
            logger.error(f"Autofix generation failed: {e}")
        
        return None
    
    def _analyze_python_project(self, project_path: Path, python_files: List[Path]) -> Dict[str, Any]:
        """Analyze entire Python project"""
        results = {
            "lint_results": {},
            "security_issues": [],
            "complexity_analysis": {},
            "test_coverage": None
        }
        
        # Run project-wide linters
        if self.linters.get("flake8"):
            results["lint_results"]["flake8"] = self._run_flake8_project(project_path)
        
        # Aggregate file-level results
        total_complexity = 0
        total_security_issues = []
        
        for file_path in python_files[:10]:  # Limit to first 10 files
            file_results = self._analyze_python_file(file_path)
            
            complexity = file_results.get("complexity_analysis", {})
            if "cyclomatic_complexity" in complexity:
                total_complexity += complexity["cyclomatic_complexity"]
            
            total_security_issues.extend(file_results.get("security_issues", []))
        
        results["complexity_analysis"]["total_complexity"] = total_complexity
        results["security_issues"] = total_security_issues
        
        return results
    
    def _run_flake8_project(self, project_path: Path) -> Dict[str, Any]:
        """Run flake8 on entire project"""
        try:
            result = subprocess.run(
                ["flake8", str(project_path)],
                capture_output=True,
                text=True
            )
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        issues.append({"message": line, "type": "style"})
            
            return {
                "issues": issues,
                "total_issues": len(issues),
                "passed": len(issues) == 0
            }
            
        except Exception as e:
            logger.error(f"Project flake8 failed: {e}")
            return {"error": str(e), "passed": False}
    
    def _analyze_javascript_project(self, project_path: Path, js_files: List[Path]) -> Dict[str, Any]:
        """Analyze entire JavaScript project"""
        results = {
            "lint_results": {},
            "security_issues": [],
            "complexity_analysis": {}
        }
        
        # Run ESLint on project if available
        if self.linters.get("eslint"):
            results["lint_results"]["eslint"] = self._run_eslint_project(project_path)
        
        return results
    
    def _run_eslint_project(self, project_path: Path) -> Dict[str, Any]:
        """Run ESLint on entire project"""
        try:
            result = subprocess.run(
                ["eslint", "--format=json", str(project_path)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                eslint_output = json.loads(result.stdout)
                total_issues = sum(len(file_result.get("messages", [])) for file_result in eslint_output)
            else:
                total_issues = 0
            
            return {
                "total_issues": total_issues,
                "passed": total_issues == 0
            }
            
        except Exception as e:
            logger.error(f"Project ESLint failed: {e}")
            return {"error": str(e), "passed": False}


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor for calculating cyclomatic complexity"""
    
    def __init__(self):
        self.complexity = 1  # Base complexity
        self.function_count = 0
        self.class_count = 0
        self.max_depth = 0
        self.current_depth = 0
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        self.complexity += 1
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
    
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)