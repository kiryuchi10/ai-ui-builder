"""
Tool Router - Intelligent tool selection and routing
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ToolCapability:
    """Represents a tool's capabilities"""
    name: str
    input_types: List[str]
    output_types: List[str]
    dependencies: List[str]
    confidence_threshold: float = 0.7

class ToolRouter:
    """
    Intelligent routing of tasks to appropriate tools
    """
    
    def __init__(self):
        self.tool_capabilities = self._initialize_tool_capabilities()
        self.routing_rules = self._initialize_routing_rules()
    
    def _initialize_tool_capabilities(self) -> Dict[str, ToolCapability]:
        """Initialize tool capability definitions"""
        return {
            "vision_detect": ToolCapability(
                name="vision_detect",
                input_types=["image", "screenshot"],
                output_types=["components", "bounding_boxes"],
                dependencies=[]
            ),
            
            "ocr": ToolCapability(
                name="ocr",
                input_types=["image", "screenshot", "regions"],
                output_types=["text", "text_regions"],
                dependencies=[]
            ),
            
            "ui2code": ToolCapability(
                name="ui2code",
                input_types=["layout_graph", "components", "text_regions"],
                output_types=["react_components", "jsx", "css"],
                dependencies=["vision_detect", "ocr"]
            ),
            
            "nl2api": ToolCapability(
                name="nl2api",
                input_types=["natural_language", "specification", "ui_components"],
                output_types=["fastapi_code", "endpoints", "models"],
                dependencies=[]
            ),
            
            "quality": ToolCapability(
                name="quality",
                input_types=["code", "directory", "files"],
                output_types=["quality_report", "suggestions", "fixes"],
                dependencies=[]
            ),
            
            "doc_gen": ToolCapability(
                name="doc_gen",
                input_types=["openapi_spec", "code", "api_endpoints"],
                output_types=["documentation", "examples", "guides"],
                dependencies=[]
            ),
            
            "file_ops": ToolCapability(
                name="file_ops",
                input_types=["files", "directories", "project_structure"],
                output_types=["project", "integration", "deployment"],
                dependencies=[]
            )
        }
    
    def _initialize_routing_rules(self) -> Dict[str, Any]:
        """Initialize routing rules and policies"""
        return {
            "image_processing": {
                "triggers": ["image_path", "screenshot", "ui_image"],
                "sequence": ["vision_detect", "ocr"],
                "parallel": False
            },
            
            "ui_generation": {
                "triggers": ["components", "layout_graph", "ui_elements"],
                "sequence": ["ui2code"],
                "parallel": False,
                "requires": ["vision_detect", "ocr"]
            },
            
            "api_generation": {
                "triggers": ["nl_spec", "specification", "requirements"],
                "sequence": ["nl2api"],
                "parallel": False
            },
            
            "quality_assurance": {
                "triggers": ["code_generated", "files_created"],
                "sequence": ["quality"],
                "parallel": True,
                "applies_to": ["ui2code", "nl2api"]
            },
            
            "documentation": {
                "triggers": ["api_generated", "project_complete"],
                "sequence": ["doc_gen"],
                "parallel": True,
                "requires": ["nl2api"]
            },
            
            "integration": {
                "triggers": ["frontend_ready", "backend_ready"],
                "sequence": ["file_ops"],
                "parallel": False,
                "requires": ["ui2code", "nl2api"]
            }
        }
    
    def route_task(self, task_type: str, inputs: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route a task to the appropriate tool(s)
        
        Args:
            task_type: Type of task to route
            inputs: Input data for the task
            context: Additional context information
            
        Returns:
            Dict with routing decision and tool selection
        """
        try:
            context = context or {}
            
            # Analyze inputs to determine required tools
            required_tools = self._analyze_inputs(inputs)
            
            # Apply routing rules
            routing_plan = self._apply_routing_rules(task_type, inputs, required_tools)
            
            # Optimize tool sequence
            optimized_plan = self._optimize_tool_sequence(routing_plan, context)
            
            # Validate routing plan
            validation_result = self._validate_routing_plan(optimized_plan)
            
            return {
                "routing_plan": optimized_plan,
                "validation": validation_result,
                "confidence": self._calculate_routing_confidence(optimized_plan),
                "estimated_duration": self._estimate_execution_time(optimized_plan)
            }
            
        except Exception as e:
            logger.error(f"Task routing failed: {e}")
            return {
                "error": str(e),
                "fallback_plan": self._generate_fallback_plan(task_type, inputs)
            }
    
    def _analyze_inputs(self, inputs: Dict[str, Any]) -> List[str]:
        """Analyze inputs to determine which tools are needed"""
        required_tools = []
        
        # Check for image inputs
        if any(key in inputs for key in ["image_path", "screenshot", "ui_image"]):
            required_tools.extend(["vision_detect", "ocr"])
        
        # Check for natural language inputs
        if any(key in inputs for key in ["nl_spec", "specification", "requirements"]):
            required_tools.append("nl2api")
        
        # Check for component inputs
        if any(key in inputs for key in ["components", "layout_graph"]):
            required_tools.append("ui2code")
        
        # Check for code inputs
        if any(key in inputs for key in ["code_path", "files", "directory"]):
            required_tools.append("quality")
        
        # Check for API spec inputs
        if any(key in inputs for key in ["openapi_spec", "api_endpoints"]):
            required_tools.append("doc_gen")
        
        return required_tools
    
    def _apply_routing_rules(self, task_type: str, inputs: Dict[str, Any], required_tools: List[str]) -> Dict[str, Any]:
        """Apply routing rules to determine tool sequence"""
        
        # Find matching routing rules
        matching_rules = []
        for rule_name, rule in self.routing_rules.items():
            triggers = rule.get("triggers", [])
            
            # Check if any trigger matches the inputs
            if any(trigger in str(inputs).lower() for trigger in triggers):
                matching_rules.append((rule_name, rule))
        
        # If no specific rules match, create a default plan
        if not matching_rules:
            return {
                "sequence": required_tools,
                "parallel_groups": [],
                "dependencies": self._build_dependency_graph(required_tools)
            }
        
        # Combine matching rules
        combined_sequence = []
        parallel_groups = []
        
        for rule_name, rule in matching_rules:
            sequence = rule.get("sequence", [])
            parallel = rule.get("parallel", False)
            
            if parallel:
                parallel_groups.append(sequence)
            else:
                combined_sequence.extend(sequence)
        
        return {
            "sequence": combined_sequence,
            "parallel_groups": parallel_groups,
            "dependencies": self._build_dependency_graph(combined_sequence + [tool for group in parallel_groups for tool in group])
        }
    
    def _build_dependency_graph(self, tools: List[str]) -> Dict[str, List[str]]:
        """Build dependency graph for tools"""
        dependency_graph = {}
        
        for tool in tools:
            capability = self.tool_capabilities.get(tool)
            if capability:
                # Only include dependencies that are also in the tool list
                deps = [dep for dep in capability.dependencies if dep in tools]
                dependency_graph[tool] = deps
            else:
                dependency_graph[tool] = []
        
        return dependency_graph
    
    def _optimize_tool_sequence(self, routing_plan: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize tool execution sequence"""
        sequence = routing_plan.get("sequence", [])
        parallel_groups = routing_plan.get("parallel_groups", [])
        dependencies = routing_plan.get("dependencies", {})
        
        # Topological sort based on dependencies
        optimized_sequence = self._topological_sort(sequence, dependencies)
        
        # Identify opportunities for parallelization
        parallel_opportunities = self._identify_parallel_opportunities(optimized_sequence, dependencies)
        
        # Consider resource constraints
        resource_optimized = self._apply_resource_constraints(optimized_sequence, parallel_opportunities, context)
        
        return {
            "sequence": resource_optimized["sequence"],
            "parallel_groups": resource_optimized["parallel_groups"] + parallel_groups,
            "dependencies": dependencies,
            "optimizations_applied": resource_optimized["optimizations"]
        }
    
    def _topological_sort(self, tools: List[str], dependencies: Dict[str, List[str]]) -> List[str]:
        """Sort tools based on dependencies using topological sort"""
        # Build in-degree count
        in_degree = {tool: 0 for tool in tools}
        
        for tool in tools:
            for dep in dependencies.get(tool, []):
                if dep in in_degree:
                    in_degree[tool] += 1
        
        # Find tools with no dependencies
        queue = [tool for tool, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Update in-degrees
            for tool in tools:
                if current in dependencies.get(tool, []):
                    in_degree[tool] -= 1
                    if in_degree[tool] == 0:
                        queue.append(tool)
        
        return result
    
    def _identify_parallel_opportunities(self, sequence: List[str], dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Identify tools that can run in parallel"""
        parallel_groups = []
        processed = set()
        
        for i, tool in enumerate(sequence):
            if tool in processed:
                continue
            
            # Find tools that can run in parallel with this one
            parallel_candidates = []
            
            for j in range(i + 1, len(sequence)):
                candidate = sequence[j]
                
                # Check if candidate can run in parallel
                if (tool not in dependencies.get(candidate, []) and 
                    candidate not in dependencies.get(tool, [])):
                    parallel_candidates.append(candidate)
            
            if parallel_candidates:
                group = [tool] + parallel_candidates
                parallel_groups.append(group)
                processed.update(group)
            else:
                processed.add(tool)
        
        return parallel_groups
    
    def _apply_resource_constraints(self, sequence: List[str], parallel_opportunities: List[List[str]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resource constraints to optimize execution"""
        
        # Get resource information from context
        max_parallel = context.get("max_parallel_tools", 2)
        memory_limit = context.get("memory_limit_mb", 4096)
        cpu_cores = context.get("cpu_cores", 4)
        
        # Tool resource requirements (estimated)
        resource_requirements = {
            "vision_detect": {"memory": 1024, "cpu": 2},
            "ocr": {"memory": 512, "cpu": 1},
            "ui2code": {"memory": 256, "cpu": 1},
            "nl2api": {"memory": 512, "cpu": 1},
            "quality": {"memory": 128, "cpu": 1},
            "doc_gen": {"memory": 64, "cpu": 1},
            "file_ops": {"memory": 32, "cpu": 1}
        }
        
        # Filter parallel opportunities based on resource constraints
        filtered_parallel = []
        optimizations = []
        
        for group in parallel_opportunities:
            total_memory = sum(resource_requirements.get(tool, {}).get("memory", 0) for tool in group)
            total_cpu = sum(resource_requirements.get(tool, {}).get("cpu", 0) for tool in group)
            
            if (len(group) <= max_parallel and 
                total_memory <= memory_limit and 
                total_cpu <= cpu_cores):
                filtered_parallel.append(group)
                optimizations.append(f"Parallelized {len(group)} tools: {', '.join(group)}")
            else:
                # Split group if it's too resource-intensive
                split_groups = self._split_resource_intensive_group(group, resource_requirements, max_parallel, memory_limit, cpu_cores)
                filtered_parallel.extend(split_groups)
                optimizations.append(f"Split resource-intensive group: {', '.join(group)}")
        
        return {
            "sequence": sequence,
            "parallel_groups": filtered_parallel,
            "optimizations": optimizations
        }
    
    def _split_resource_intensive_group(self, group: List[str], requirements: Dict[str, Dict[str, int]], 
                                      max_parallel: int, memory_limit: int, cpu_limit: int) -> List[List[str]]:
        """Split a resource-intensive group into smaller groups"""
        
        # Sort tools by resource requirements (heaviest first)
        sorted_tools = sorted(group, key=lambda t: requirements.get(t, {}).get("memory", 0), reverse=True)
        
        split_groups = []
        current_group = []
        current_memory = 0
        current_cpu = 0
        
        for tool in sorted_tools:
            tool_memory = requirements.get(tool, {}).get("memory", 0)
            tool_cpu = requirements.get(tool, {}).get("cpu", 0)
            
            if (len(current_group) < max_parallel and 
                current_memory + tool_memory <= memory_limit and 
                current_cpu + tool_cpu <= cpu_limit):
                current_group.append(tool)
                current_memory += tool_memory
                current_cpu += tool_cpu
            else:
                if current_group:
                    split_groups.append(current_group)
                current_group = [tool]
                current_memory = tool_memory
                current_cpu = tool_cpu
        
        if current_group:
            split_groups.append(current_group)
        
        return split_groups
    
    def _validate_routing_plan(self, routing_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the routing plan"""
        issues = []
        warnings = []
        
        sequence = routing_plan.get("sequence", [])
        parallel_groups = routing_plan.get("parallel_groups", [])
        dependencies = routing_plan.get("dependencies", {})
        
        # Check for missing tools
        all_tools = set(sequence + [tool for group in parallel_groups for tool in group])
        for tool in all_tools:
            if tool not in self.tool_capabilities:
                issues.append(f"Unknown tool: {tool}")
        
        # Check dependency satisfaction
        for tool, deps in dependencies.items():
            for dep in deps:
                if dep not in all_tools:
                    warnings.append(f"Dependency {dep} for {tool} not in execution plan")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(dependencies):
            issues.append("Circular dependencies detected")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_issues": len(issues),
            "total_warnings": len(warnings)
        }
    
    def _has_circular_dependencies(self, dependencies: Dict[str, List[str]]) -> bool:
        """Check for circular dependencies"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependencies:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _calculate_routing_confidence(self, routing_plan: Dict[str, Any]) -> float:
        """Calculate confidence score for the routing plan"""
        sequence = routing_plan.get("sequence", [])
        dependencies = routing_plan.get("dependencies", {})
        
        # Base confidence
        confidence = 0.8
        
        # Adjust based on tool availability
        for tool in sequence:
            if tool in self.tool_capabilities:
                confidence += 0.02
            else:
                confidence -= 0.1
        
        # Adjust based on dependency satisfaction
        satisfied_deps = 0
        total_deps = 0
        
        for tool, deps in dependencies.items():
            total_deps += len(deps)
            for dep in deps:
                if dep in sequence:
                    satisfied_deps += 1
        
        if total_deps > 0:
            dep_ratio = satisfied_deps / total_deps
            confidence = confidence * 0.7 + dep_ratio * 0.3
        
        return min(max(confidence, 0.0), 1.0)
    
    def _estimate_execution_time(self, routing_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate execution time for the routing plan"""
        
        # Estimated execution times (in seconds)
        tool_times = {
            "vision_detect": 30,
            "ocr": 15,
            "ui2code": 45,
            "nl2api": 60,
            "quality": 20,
            "doc_gen": 10,
            "file_ops": 5
        }
        
        sequence = routing_plan.get("sequence", [])
        parallel_groups = routing_plan.get("parallel_groups", [])
        
        # Sequential execution time
        sequential_time = sum(tool_times.get(tool, 30) for tool in sequence)
        
        # Parallel execution time (max time in each group)
        parallel_time = sum(max(tool_times.get(tool, 30) for tool in group) for group in parallel_groups)
        
        total_estimated_time = sequential_time + parallel_time
        
        return {
            "sequential_time": sequential_time,
            "parallel_time": parallel_time,
            "total_estimated_time": total_estimated_time,
            "time_saved_by_parallelization": sum(sum(tool_times.get(tool, 30) for tool in group) for group in parallel_groups) - parallel_time
        }
    
    def _generate_fallback_plan(self, task_type: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback routing plan when normal routing fails"""
        
        # Simple fallback based on input types
        fallback_sequence = []
        
        if any(key in inputs for key in ["image_path", "screenshot"]):
            fallback_sequence.extend(["vision_detect", "ocr", "ui2code"])
        
        if any(key in inputs for key in ["nl_spec", "specification"]):
            fallback_sequence.append("nl2api")
        
        # Always include quality check and file operations
        fallback_sequence.extend(["quality", "file_ops"])
        
        return {
            "sequence": fallback_sequence,
            "parallel_groups": [],
            "dependencies": {},
            "confidence": 0.5,
            "note": "Fallback routing plan - may not be optimal"
        }
    
    def get_tool_recommendations(self, task_description: str, available_inputs: List[str]) -> Dict[str, Any]:
        """Get tool recommendations based on task description and available inputs"""
        
        recommendations = []
        
        # Analyze task description
        task_lower = task_description.lower()
        
        # UI-related tasks
        if any(word in task_lower for word in ["ui", "interface", "screenshot", "design"]):
            recommendations.append({
                "tool": "vision_detect",
                "reason": "UI component detection from screenshot",
                "confidence": 0.9
            })
            recommendations.append({
                "tool": "ocr",
                "reason": "Text extraction from UI elements",
                "confidence": 0.8
            })
            recommendations.append({
                "tool": "ui2code",
                "reason": "Generate React components from UI",
                "confidence": 0.9
            })
        
        # API-related tasks
        if any(word in task_lower for word in ["api", "backend", "endpoint", "server"]):
            recommendations.append({
                "tool": "nl2api",
                "reason": "Generate API endpoints from specification",
                "confidence": 0.9
            })
        
        # Quality-related tasks
        if any(word in task_lower for word in ["quality", "lint", "test", "validate"]):
            recommendations.append({
                "tool": "quality",
                "reason": "Code quality analysis and validation",
                "confidence": 0.8
            })
        
        # Documentation tasks
        if any(word in task_lower for word in ["document", "docs", "guide", "readme"]):
            recommendations.append({
                "tool": "doc_gen",
                "reason": "Generate documentation from code",
                "confidence": 0.8
            })
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "confidence_score": sum(r["confidence"] for r in recommendations) / len(recommendations) if recommendations else 0
        }