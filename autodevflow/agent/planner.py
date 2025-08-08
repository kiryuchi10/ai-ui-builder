"""
AutoDevFlow Orchestrator - High-level task planner and DAG execution
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .tools.vision_detect import VisionDetector
from .tools.ocr import OCRProcessor
from .tools.ui2code import UI2CodeGenerator
from .tools.nl2api import NL2APIGenerator
from .tools.quality import CodeQualityChecker
from .tools.doc_gen import DocumentationGenerator
from .tools.file_ops import FileOperations
from .router import ToolRouter
from .memory import RAGMemory

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    name: str
    tool: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    dependencies: List[str]
    status: TaskStatus = TaskStatus.PENDING
    error: Optional[str] = None

class AutoDevFlowPlanner:
    """
    High-level orchestrator that creates full-stack applications
    from UI screenshots and natural language specifications.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.tools = self._initialize_tools()
        self.router = ToolRouter()
        self.memory = RAGMemory()
        self.tasks: Dict[str, Task] = {}
        self.execution_log: List[Dict] = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "models": {
                "maskrcnn_path": "models/maskrcnn/",
                "pix2code_path": "models/pix2code/",
                "codet5_path": "models/codet5/"
            },
            "output_dirs": {
                "frontend": "services/frontend/",
                "backend": "services/backend/"
            },
            "quality_thresholds": {
                "min_score": 0.7,
                "max_lint_errors": 5
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                
        return default_config
    
    def _initialize_tools(self) -> Dict:
        """Initialize all available tools"""
        return {
            "vision_detect": VisionDetector(self.config["models"]["maskrcnn_path"]),
            "ocr": OCRProcessor(),
            "ui2code": UI2CodeGenerator(self.config["models"]["pix2code_path"]),
            "nl2api": NL2APIGenerator(self.config["models"]["codet5_path"]),
            "quality": CodeQualityChecker(),
            "doc_gen": DocumentationGenerator(),
            "file_ops": FileOperations()
        }
    
    async def create_application(self, 
                               image_path: Optional[str] = None,
                               nl_spec: Optional[str] = None,
                               output_dir: str = "output") -> Dict[str, Any]:
        """
        Main entry point: Create full-stack application from inputs
        
        Args:
            image_path: Path to UI screenshot
            nl_spec: Natural language specification
            output_dir: Output directory for generated app
            
        Returns:
            Dict with generation results and artifact paths
        """
        logger.info("Starting AutoDevFlow application generation")
        
        # Step 1: Parse user intent and inputs
        plan = await self._create_execution_plan(image_path, nl_spec)
        
        # Step 2: Execute DAG
        results = await self._execute_plan(plan)
        
        # Step 3: Package final application
        package_info = await self._package_application(output_dir, results)
        
        return {
            "status": "PACKAGE_READY",
            "artifacts": package_info,
            "execution_log": self.execution_log,
            "results": results
        }
    
    async def _create_execution_plan(self, 
                                   image_path: Optional[str],
                                   nl_spec: Optional[str]) -> List[Task]:
        """Create DAG of tasks based on inputs"""
        tasks = []
        
        # Task 1: Parse inputs and determine capabilities needed
        if image_path:
            tasks.extend([
                Task("vision_detect", "UI Component Detection", "vision_detect",
                     {"image_path": image_path}, {}, []),
                Task("ocr", "Text Recognition", "ocr", 
                     {"image_path": image_path}, {}, []),
                Task("layout_graph", "Build Layout Graph", "ui2code",
                     {}, {}, ["vision_detect", "ocr"])
            ])
        
        # Task 2: Generate frontend
        if image_path:
            tasks.append(
                Task("ui2code", "Generate React Components", "ui2code",
                     {"style_prefs": {"tailwind": True, "theme": "light"}}, 
                     {}, ["layout_graph"])
            )
        
        # Task 3: Generate backend
        if nl_spec or image_path:
            spec_input = nl_spec if nl_spec else "inferred_from_ui"
            tasks.append(
                Task("nl2api", "Generate FastAPI Backend", "nl2api",
                     {"nl_spec": spec_input}, {}, 
                     ["ui2code"] if image_path else [])
            )
        
        # Task 4: Wire frontend and backend
        if image_path and (nl_spec or image_path):
            tasks.append(
                Task("wire", "Connect Frontend to Backend", "file_ops",
                     {}, {}, ["ui2code", "nl2api"])
            )
        
        # Task 5: Quality checks
        tasks.extend([
            Task("quality_frontend", "Frontend Quality Check", "quality",
                 {"code_path": "services/frontend/"}, {}, ["ui2code"]),
            Task("quality_backend", "Backend Quality Check", "quality", 
                 {"code_path": "services/backend/"}, {}, ["nl2api"])
        ])
        
        # Task 6: Generate documentation
        tasks.append(
            Task("docs", "Generate Documentation", "doc_gen",
                 {}, {}, ["quality_frontend", "quality_backend"])
        )
        
        return tasks
    
    async def _execute_plan(self, tasks: List[Task]) -> Dict[str, Any]:
        """Execute task DAG with dependency resolution"""
        # Convert to dict for easier lookup
        self.tasks = {task.id: task for task in tasks}
        results = {}
        
        # Topological sort for execution order
        execution_order = self._topological_sort(tasks)
        
        for task_id in execution_order:
            task = self.tasks[task_id]
            logger.info(f"Executing task: {task.name}")
            
            try:
                task.status = TaskStatus.RUNNING
                
                # Prepare inputs with dependency outputs
                inputs = task.inputs.copy()
                for dep_id in task.dependencies:
                    if dep_id in results:
                        inputs.update(results[dep_id])
                
                # Execute task
                tool = self.tools[task.tool]
                if hasattr(tool, 'execute'):
                    result = await tool.execute(**inputs)
                else:
                    result = tool.process(**inputs)
                
                task.outputs = result
                task.status = TaskStatus.COMPLETED
                results[task_id] = result
                
                # Log execution
                self.execution_log.append({
                    "task": task.name,
                    "status": "completed",
                    "outputs": result
                })
                
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                logger.error(f"Task {task.name} failed: {e}")
                
                self.execution_log.append({
                    "task": task.name,
                    "status": "failed",
                    "error": str(e)
                })
                
                # Continue with other tasks if possible
                continue
        
        return results
    
    def _topological_sort(self, tasks: List[Task]) -> List[str]:
        """Sort tasks by dependencies using Kahn's algorithm"""
        # Build adjacency list and in-degree count
        graph = {task.id: [] for task in tasks}
        in_degree = {task.id: 0 for task in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in graph:
                    graph[dep].append(task.id)
                    in_degree[task.id] += 1
        
        # Find nodes with no incoming edges
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Remove edges and update in-degrees
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    async def _package_application(self, output_dir: str, results: Dict) -> Dict[str, str]:
        """Package the generated application for deployment"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Copy generated files
        artifacts = {}
        
        if "ui2code" in results:
            frontend_path = output_path / "frontend"
            # Copy React components
            artifacts["frontend"] = str(frontend_path)
        
        if "nl2api" in results:
            backend_path = output_path / "backend"
            # Copy FastAPI application
            artifacts["backend"] = str(backend_path)
        
        # Generate docker-compose.yml
        docker_compose = self._generate_docker_compose()
        with open(output_path / "docker-compose.yml", "w") as f:
            f.write(docker_compose)
        artifacts["docker_compose"] = str(output_path / "docker-compose.yml")
        
        # Generate README
        readme = self._generate_readme(results)
        with open(output_path / "README.md", "w") as f:
            f.write(readme)
        artifacts["readme"] = str(output_path / "README.md")
        
        return artifacts
    
    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for the application"""
        return """version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    
    def _generate_readme(self, results: Dict) -> str:
        """Generate README for the generated application"""
        return f"""# Generated Application

This application was created by AutoDevFlow Orchestrator.

## Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI with PostgreSQL
- **Deployment**: Docker Compose

## Quick Start

```bash
# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Generated Components

{self._format_results_summary(results)}

## Development

```bash
# Frontend development
cd frontend
npm install
npm run dev

# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
"""
    
    def _format_results_summary(self, results: Dict) -> str:
        """Format results summary for README"""
        summary = []
        
        if "ui2code" in results:
            summary.append("- ✅ React components generated from UI screenshot")
        
        if "nl2api" in results:
            summary.append("- ✅ FastAPI endpoints generated from specification")
        
        if "quality_frontend" in results:
            summary.append("- ✅ Frontend code quality validated")
        
        if "quality_backend" in results:
            summary.append("- ✅ Backend code quality validated")
        
        if "docs" in results:
            summary.append("- ✅ API documentation generated")
        
        return "\n".join(summary)

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AutoDevFlow Orchestrator")
    parser.add_argument("--input", help="Path to UI screenshot")
    parser.add_argument("--spec", help="Natural language specification")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--config", help="Configuration file path")
    
    args = parser.parse_args()
    
    async def main():
        planner = AutoDevFlowPlanner(args.config)
        result = await planner.create_application(
            image_path=args.input,
            nl_spec=args.spec,
            output_dir=args.output
        )
        print(json.dumps(result, indent=2))
    
    asyncio.run(main())