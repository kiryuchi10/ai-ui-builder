#!/usr/bin/env python3
"""
AutoDevFlow Orchestrator Demo
Demonstrates end-to-end application generation
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from autodevflow.agent.planner import AutoDevFlowPlanner

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDevFlowDemo:
    """Demonstration of AutoDevFlow capabilities"""
    
    def __init__(self):
        self.demo_dir = Path(__file__).parent / "demo_output"
        self.demo_dir.mkdir(exist_ok=True)
        
    async def run_demo(self):
        """Run complete demonstration"""
        logger.info("🚀 Starting AutoDevFlow Orchestrator Demo")
        
        try:
            # Initialize planner
            planner = AutoDevFlowPlanner()
            
            # Demo 1: Natural language to full-stack app
            await self.demo_nl_to_app(planner)
            
            # Demo 2: UI screenshot to app (simulated)
            await self.demo_ui_to_app(planner)
            
            # Demo 3: Combined UI + NL specification
            await self.demo_combined_input(planner)
            
            logger.info("✅ Demo completed successfully!")
            self.print_demo_results()
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
    
    async def demo_nl_to_app(self, planner: AutoDevFlowPlanner):
        """Demo: Natural language specification to full-stack app"""
        logger.info("📝 Demo 1: Natural Language to Full-Stack App")
        
        nl_spec = """
        Create a user management system with the following features:
        - User registration and login with JWT authentication
        - User profile management (CRUD operations)
        - Admin dashboard for user management
        - RESTful API with proper error handling
        - React frontend with modern UI components
        - Form validation and user feedback
        """
        
        result = await planner.create_application(
            nl_spec=nl_spec,
            output_dir=str(self.demo_dir / "nl_demo")
        )
        
        # Save results
        with open(self.demo_dir / "nl_demo_results.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"✅ Demo 1 completed. Status: {result.get('status')}")
        return result
    
    async def demo_ui_to_app(self, planner: AutoDevFlowPlanner):
        """Demo: UI screenshot to app (simulated with mock data)"""
        logger.info("🖼️ Demo 2: UI Screenshot to Full-Stack App")
        
        # Create a mock screenshot scenario
        mock_image_path = self.create_mock_screenshot()
        
        result = await planner.create_application(
            image_path=str(mock_image_path),
            output_dir=str(self.demo_dir / "ui_demo")
        )
        
        # Save results
        with open(self.demo_dir / "ui_demo_results.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"✅ Demo 2 completed. Status: {result.get('status')}")
        return result
    
    async def demo_combined_input(self, planner: AutoDevFlowPlanner):
        """Demo: Combined UI screenshot + natural language specification"""
        logger.info("🔄 Demo 3: Combined UI + Natural Language Input")
        
        mock_image_path = self.create_mock_screenshot()
        
        nl_spec = """
        Based on the provided UI screenshot, create a complete application with:
        - Backend API endpoints for all visible forms and interactions
        - Proper authentication and authorization
        - Database models for data persistence
        - Error handling and validation
        - API documentation
        """
        
        result = await planner.create_application(
            image_path=str(mock_image_path),
            nl_spec=nl_spec,
            output_dir=str(self.demo_dir / "combined_demo")
        )
        
        # Save results
        with open(self.demo_dir / "combined_demo_results.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"✅ Demo 3 completed. Status: {result.get('status')}")
        return result
    
    def create_mock_screenshot(self) -> Path:
        """Create a mock screenshot for demonstration"""
        # In a real scenario, this would be an actual UI screenshot
        # For demo purposes, we'll create a text file describing the UI
        
        mock_screenshot_path = self.demo_dir / "mock_screenshot.txt"
        
        mock_ui_description = """
        Mock UI Screenshot Description:
        
        Layout: Login/Registration Form
        Components:
        - Header with logo and navigation
        - Login form with:
          * Email input field
          * Password input field
          * "Remember me" checkbox
          * "Login" button
          * "Forgot password?" link
        - Registration section with:
          * "Don't have an account?" text
          * "Sign up" button
        - Footer with links
        
        Visual Style: Modern, clean design with blue accent colors
        """
        
        with open(mock_screenshot_path, 'w') as f:
            f.write(mock_ui_description)
        
        return mock_screenshot_path
    
    def print_demo_results(self):
        """Print demo results summary"""
        print("\n" + "="*60)
        print("🎉 AutoDevFlow Orchestrator Demo Results")
        print("="*60)
        
        # Check generated files
        demo_dirs = ["nl_demo", "ui_demo", "combined_demo"]
        
        for demo_dir in demo_dirs:
            demo_path = self.demo_dir / demo_dir
            if demo_path.exists():
                print(f"\n📁 {demo_dir.upper()}:")
                self.print_directory_structure(demo_path, indent="   ")
        
        print(f"\n📊 Demo Results:")
        print(f"   Output directory: {self.demo_dir}")
        print(f"   Generated applications: {len([d for d in demo_dirs if (self.demo_dir / d).exists()])}")
        
        print("\n🚀 Next Steps:")
        print("   1. Explore the generated applications in demo_output/")
        print("   2. Run the applications using docker-compose up")
        print("   3. Customize the generated code as needed")
        print("   4. Deploy to your preferred platform")
        
        print("\n" + "="*60)
    
    def print_directory_structure(self, path: Path, indent: str = "", max_depth: int = 3, current_depth: int = 0):
        """Print directory structure"""
        if current_depth >= max_depth:
            return
        
        try:
            items = sorted(path.iterdir())
            for item in items[:10]:  # Limit to first 10 items
                if item.is_dir():
                    print(f"{indent}📁 {item.name}/")
                    if current_depth < max_depth - 1:
                        self.print_directory_structure(item, indent + "   ", max_depth, current_depth + 1)
                else:
                    size = item.stat().st_size
                    print(f"{indent}📄 {item.name} ({size} bytes)")
            
            if len(items) > 10:
                print(f"{indent}... and {len(items) - 10} more items")
                
        except PermissionError:
            print(f"{indent}❌ Permission denied")

async def main():
    """Main demo function"""
    demo = AutoDevFlowDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())