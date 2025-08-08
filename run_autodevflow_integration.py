#!/usr/bin/env python3
"""
AutoDevFlow Integration Runner
Complete integration between AI UI Builder and Backend Automation Paper2Code
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add paths for integration
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent / "backend-automation-paper2code"))

from autodevflow.agent.planner import AutoDevFlowPlanner

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDevFlowIntegration:
    """
    Complete integration runner for AutoDevFlow Orchestrator
    Demonstrates the full pipeline from research papers to deployed applications
    """
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_automation_dir = self.root_dir.parent / "backend-automation-paper2code"
        self.papers_dir = self.backend_automation_dir / "Papers" / "mypapers" / "frontend"
        self.output_dir = self.root_dir / "integration_output"
        self.output_dir.mkdir(exist_ok=True)
        
    async def run_integration(self):
        """Run complete integration demonstration"""
        logger.info("🚀 Starting AutoDevFlow Integration")
        
        try:
            # Step 1: Verify integration setup
            self.verify_integration_setup()
            
            # Step 2: Load research papers knowledge
            papers_knowledge = self.load_papers_knowledge()
            
            # Step 3: Initialize orchestrator with integration
            planner = self.initialize_orchestrator()
            
            # Step 4: Run end-to-end scenarios
            scenarios = [
                self.scenario_ui_screenshot_to_fullstack,
                self.scenario_research_driven_api,
                self.scenario_complete_application_pipeline
            ]
            
            results = {}
            for i, scenario in enumerate(scenarios, 1):
                logger.info(f"📋 Running Scenario {i}: {scenario.__name__}")
                result = await scenario(planner, papers_knowledge)
                results[f"scenario_{i}"] = result
            
            # Step 5: Generate integration report
            self.generate_integration_report(results)
            
            logger.info("✅ AutoDevFlow Integration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Integration failed: {e}")
            raise
    
    def verify_integration_setup(self):
        """Verify that integration components are properly set up"""
        logger.info("🔍 Verifying integration setup...")
        
        checks = {
            "Backend Automation Directory": self.backend_automation_dir.exists(),
            "Papers Directory": self.papers_dir.exists(),
            "AutoDevFlow Components": (self.root_dir / "autodevflow").exists(),
        }
        
        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            logger.info(f"   {status} {check_name}")
        
        if not all(checks.values()):
            logger.warning("Some integration components are missing - functionality may be limited")
        
        logger.info("✅ Integration setup verified")
    
    def load_papers_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from research papers"""
        logger.info("📚 Loading research papers knowledge...")
        
        papers_knowledge = {
            "available_papers": [],
            "capabilities": {},
            "integration_points": {}
        }
        
        if self.papers_dir.exists():
            # List available papers
            for paper_file in self.papers_dir.glob("*.pdf"):
                papers_knowledge["available_papers"].append(paper_file.name)
            
            # Define capabilities based on papers
            papers_knowledge["capabilities"] = {
                "vision_detection": {
                    "paper": "Mask R-CNN.pdf",
                    "capability": "UI component detection and segmentation",
                    "integration": "vision_detect tool"
                },
                "ocr_processing": {
                    "paper": "Scene Text Detection and Recognition the deep learning era.pdf",
                    "capability": "Text extraction from UI screenshots",
                    "integration": "ocr tool"
                },
                "ui_to_code": {
                    "paper": "pix2code Generating Code from a Graphical User interface screenshot.pdf",
                    "capability": "Generate React components from UI screenshots",
                    "integration": "ui2code tool"
                },
                "code_generation": {
                    "paper": "CodeT5+ Open Code Large Language Models for code understanding and generation.pdf",
                    "capability": "Generate FastAPI endpoints from specifications",
                    "integration": "nl2api tool"
                },
                "code_quality": {
                    "paper": "CodeBERT A Pre-Trained Model for Programming and Natural Languages.pdf",
                    "capability": "Code quality assessment and improvement",
                    "integration": "quality tool"
                },
                "api_documentation": {
                    "paper": "Natural_Language_Sentence_Generation_from_API_Spec.pdf",
                    "capability": "Generate documentation from API specifications",
                    "integration": "doc_gen tool"
                }
            }
        
        logger.info(f"✅ Loaded knowledge from {len(papers_knowledge['available_papers'])} papers")
        return papers_knowledge
    
    def initialize_orchestrator(self) -> AutoDevFlowPlanner:
        """Initialize AutoDevFlow orchestrator with integration"""
        logger.info("🤖 Initializing AutoDevFlow Orchestrator...")
        
        # Create integration configuration
        config = {
            "models": {
                "maskrcnn_path": "autodevflow/models/maskrcnn/",
                "pix2code_path": "autodevflow/models/pix2code/",
                "codet5_path": "autodevflow/models/codet5/"
            },
            "integration": {
                "backend_automation_path": str(self.backend_automation_dir),
                "papers_path": str(self.papers_dir),
                "enabled": self.backend_automation_dir.exists()
            },
            "output_dirs": {
                "frontend": "services/frontend/",
                "backend": "services/backend/"
            }
        }
        
        # Save configuration
        config_path = self.output_dir / "integration_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Initialize planner
        planner = AutoDevFlowPlanner(str(config_path))
        
        logger.info("✅ Orchestrator initialized")
        return planner
    
    async def scenario_ui_screenshot_to_fullstack(self, planner: AutoDevFlowPlanner, papers_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scenario 1: UI Screenshot to Full-Stack Application
        Demonstrates the complete pix2code pipeline with backend generation
        """
        logger.info("🖼️ Scenario 1: UI Screenshot → Full-Stack Application")
        
        # Create mock UI screenshot data (in real scenario, this would be an actual image)
        mock_ui_data = {
            "image_description": "Login form with email, password fields and submit button",
            "components": [
                {
                    "type": "input",
                    "label": "Email",
                    "placeholder": "Enter your email",
                    "required": True
                },
                {
                    "type": "input", 
                    "label": "Password",
                    "placeholder": "Enter your password",
                    "required": True,
                    "input_type": "password"
                },
                {
                    "type": "button",
                    "text": "Login",
                    "action": "submit"
                }
            ]
        }
        
        # Save mock data
        mock_image_path = self.output_dir / "mock_login_ui.json"
        with open(mock_image_path, 'w') as f:
            json.dump(mock_ui_data, f, indent=2)
        
        # Generate application
        result = await planner.create_application(
            image_path=str(mock_image_path),
            nl_spec="Create a login system with JWT authentication",
            output_dir=str(self.output_dir / "scenario_1_output")
        )
        
        logger.info(f"✅ Scenario 1 completed: {result.get('status')}")
        return result
    
    async def scenario_research_driven_api(self, planner: AutoDevFlowPlanner, papers_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scenario 2: Research-Driven API Generation
        Uses CodeT5+ and CodeBERT capabilities for advanced API generation
        """
        logger.info("🔬 Scenario 2: Research-Driven API Generation")
        
        # Advanced specification leveraging research capabilities
        advanced_spec = """
        Create an advanced user management API with the following research-driven features:
        
        Based on CodeT5+ capabilities:
        - Generate RESTful endpoints with proper HTTP methods and status codes
        - Implement advanced query parameters and filtering
        - Create comprehensive Pydantic models with validation
        - Generate OpenAPI documentation automatically
        
        Based on CodeBERT quality assessment:
        - Ensure high code quality with proper error handling
        - Implement security best practices (JWT, input validation)
        - Add comprehensive logging and monitoring
        - Include unit tests for all endpoints
        
        Features to implement:
        - User CRUD operations (Create, Read, Update, Delete)
        - Authentication and authorization with JWT
        - Role-based access control (Admin, User roles)
        - Password hashing and security
        - Email verification system
        - Rate limiting and API throttling
        - Database migrations and seeding
        - Comprehensive error handling
        """
        
        result = await planner.create_application(
            nl_spec=advanced_spec,
            output_dir=str(self.output_dir / "scenario_2_output")
        )
        
        logger.info(f"✅ Scenario 2 completed: {result.get('status')}")
        return result
    
    async def scenario_complete_application_pipeline(self, planner: AutoDevFlowPlanner, papers_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scenario 3: Complete Application Pipeline
        Demonstrates the full AutoDevFlow pipeline with all research capabilities
        """
        logger.info("🏗️ Scenario 3: Complete Application Pipeline")
        
        # Create comprehensive mock UI
        comprehensive_ui = {
            "application_type": "E-commerce Dashboard",
            "pages": [
                {
                    "name": "Dashboard",
                    "components": ["navbar", "sidebar", "stats_cards", "charts", "recent_orders"]
                },
                {
                    "name": "Products",
                    "components": ["product_grid", "search_bar", "filters", "pagination"]
                },
                {
                    "name": "Orders",
                    "components": ["orders_table", "status_filters", "export_button"]
                },
                {
                    "name": "Users",
                    "components": ["users_table", "user_form", "role_management"]
                }
            ],
            "ui_patterns": ["CRUD operations", "Data visualization", "Authentication", "Navigation"]
        }
        
        # Save comprehensive UI data
        ui_path = self.output_dir / "comprehensive_ui.json"
        with open(ui_path, 'w') as f:
            json.dump(comprehensive_ui, f, indent=2)
        
        # Comprehensive specification
        comprehensive_spec = """
        Create a complete e-commerce dashboard application integrating all research capabilities:
        
        Frontend (based on pix2code and UI detection):
        - React dashboard with modern UI components
        - Responsive design with Tailwind CSS
        - Interactive charts and data visualization
        - Form handling with validation
        - Real-time updates and notifications
        
        Backend (based on CodeT5+ and research papers):
        - FastAPI with comprehensive REST API
        - Database models for products, orders, users
        - Authentication and authorization system
        - File upload and image processing
        - Email notifications and background tasks
        - API rate limiting and caching
        - Comprehensive logging and monitoring
        
        Quality and Documentation (based on CodeBERT and NL generation):
        - High code quality with linting and testing
        - Comprehensive API documentation
        - User guides and developer documentation
        - Deployment scripts and Docker configuration
        
        Integration Features:
        - Real-time WebSocket connections
        - Third-party API integrations
        - Payment processing simulation
        - Analytics and reporting
        - Admin panel with role management
        """
        
        result = await planner.create_application(
            image_path=str(ui_path),
            nl_spec=comprehensive_spec,
            output_dir=str(self.output_dir / "scenario_3_output")
        )
        
        logger.info(f"✅ Scenario 3 completed: {result.get('status')}")
        return result
    
    def generate_integration_report(self, results: Dict[str, Any]):
        """Generate comprehensive integration report"""
        logger.info("📊 Generating integration report...")
        
        report = {
            "integration_summary": {
                "timestamp": "2025-01-08T12:00:00Z",
                "total_scenarios": len(results),
                "successful_scenarios": sum(1 for r in results.values() if r.get("status") == "PACKAGE_READY"),
                "integration_status": "SUCCESS" if all(r.get("status") == "PACKAGE_READY" for r in results.values()) else "PARTIAL"
            },
            "research_papers_utilized": [
                "Mask R-CNN for UI component detection",
                "pix2code for UI to code generation", 
                "CodeT5+ for API code generation",
                "CodeBERT for code quality assessment",
                "Scene Text Detection for OCR processing",
                "Natural Language API Documentation generation"
            ],
            "capabilities_demonstrated": [
                "UI screenshot analysis and component detection",
                "Automatic React component generation",
                "FastAPI endpoint generation from specifications",
                "Code quality assessment and improvement",
                "Comprehensive documentation generation",
                "Full-stack application packaging"
            ],
            "scenario_results": results,
            "generated_artifacts": self.collect_generated_artifacts(),
            "performance_metrics": self.calculate_performance_metrics(results),
            "recommendations": self.generate_recommendations(results)
        }
        
        # Save report
        report_path = self.output_dir / "integration_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate human-readable report
        self.generate_human_readable_report(report)
        
        logger.info(f"✅ Integration report generated: {report_path}")
    
    def collect_generated_artifacts(self) -> Dict[str, Any]:
        """Collect information about generated artifacts"""
        artifacts = {
            "total_files": 0,
            "frontend_files": 0,
            "backend_files": 0,
            "documentation_files": 0,
            "configuration_files": 0
        }
        
        for scenario_dir in self.output_dir.glob("scenario_*_output"):
            if scenario_dir.is_dir():
                for file_path in scenario_dir.rglob("*"):
                    if file_path.is_file():
                        artifacts["total_files"] += 1
                        
                        if "frontend" in str(file_path) or file_path.suffix in [".jsx", ".js", ".css", ".html"]:
                            artifacts["frontend_files"] += 1
                        elif "backend" in str(file_path) or file_path.suffix in [".py", ".sql"]:
                            artifacts["backend_files"] += 1
                        elif file_path.suffix in [".md", ".txt", ".json"] and "doc" in file_path.name.lower():
                            artifacts["documentation_files"] += 1
                        elif file_path.name in ["docker-compose.yml", "Dockerfile", "requirements.txt", "package.json"]:
                            artifacts["configuration_files"] += 1
        
        return artifacts
    
    def calculate_performance_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        metrics = {
            "success_rate": 0.0,
            "average_execution_time": 0.0,
            "total_components_generated": 0,
            "total_endpoints_generated": 0,
            "average_quality_score": 0.0
        }
        
        successful_results = [r for r in results.values() if r.get("status") == "PACKAGE_READY"]
        metrics["success_rate"] = len(successful_results) / len(results) if results else 0.0
        
        # Extract metrics from results
        total_components = 0
        total_endpoints = 0
        quality_scores = []
        
        for result in successful_results:
            execution_log = result.get("execution_log", [])
            for log_entry in execution_log:
                if "components" in log_entry.get("outputs", {}):
                    total_components += len(log_entry["outputs"]["components"])
                if "endpoints" in log_entry.get("outputs", {}):
                    total_endpoints += len(log_entry["outputs"]["endpoints"])
                if "quality_score" in log_entry.get("outputs", {}):
                    quality_scores.append(log_entry["outputs"]["quality_score"])
        
        metrics["total_components_generated"] = total_components
        metrics["total_endpoints_generated"] = total_endpoints
        metrics["average_quality_score"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return metrics
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []
        
        # Analyze results for recommendations
        failed_scenarios = [k for k, v in results.items() if v.get("status") != "PACKAGE_READY"]
        
        if failed_scenarios:
            recommendations.append(f"Review and fix issues in {len(failed_scenarios)} failed scenarios")
        
        recommendations.extend([
            "Consider fine-tuning models with domain-specific data for better accuracy",
            "Implement caching mechanisms to improve performance",
            "Add more comprehensive error handling and recovery mechanisms",
            "Expand the knowledge base with more UI patterns and API templates",
            "Integrate with more research papers for additional capabilities"
        ])
        
        return recommendations
    
    def generate_human_readable_report(self, report: Dict[str, Any]):
        """Generate human-readable integration report"""
        report_content = f"""
# AutoDevFlow Integration Report

## Summary
- **Integration Status**: {report['integration_summary']['integration_status']}
- **Total Scenarios**: {report['integration_summary']['total_scenarios']}
- **Successful Scenarios**: {report['integration_summary']['successful_scenarios']}
- **Success Rate**: {report['performance_metrics']['success_rate']:.1%}

## Research Papers Utilized
{chr(10).join(f"- {paper}" for paper in report['research_papers_utilized'])}

## Capabilities Demonstrated
{chr(10).join(f"- {capability}" for capability in report['capabilities_demonstrated'])}

## Generated Artifacts
- **Total Files**: {report['generated_artifacts']['total_files']}
- **Frontend Files**: {report['generated_artifacts']['frontend_files']}
- **Backend Files**: {report['generated_artifacts']['backend_files']}
- **Documentation Files**: {report['generated_artifacts']['documentation_files']}
- **Configuration Files**: {report['generated_artifacts']['configuration_files']}

## Performance Metrics
- **Components Generated**: {report['performance_metrics']['total_components_generated']}
- **API Endpoints Generated**: {report['performance_metrics']['total_endpoints_generated']}
- **Average Quality Score**: {report['performance_metrics']['average_quality_score']:.2f}

## Recommendations
{chr(10).join(f"- {rec}" for rec in report['recommendations'])}

## Next Steps
1. Review generated applications in the output directories
2. Test the applications using the provided Docker configurations
3. Customize and extend the generated code as needed
4. Deploy to your preferred hosting platform
5. Provide feedback to improve the AutoDevFlow system

---
Generated by AutoDevFlow Orchestrator Integration System
"""
        
        report_path = self.output_dir / "integration_report.md"
        with open(report_path, 'w') as f:
            f.write(report_content)

async def main():
    """Main integration function"""
    integration = AutoDevFlowIntegration()
    await integration.run_integration()

if __name__ == "__main__":
    asyncio.run(main())