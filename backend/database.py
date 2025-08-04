from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_ui_builder.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL debugging
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    from models.prompt_model import Base as PromptBase
    from models.component_model import Base as ComponentBase
    PromptBase.metadata.create_all(bind=engine)
    ComponentBase.metadata.create_all(bind=engine)

def init_database():
    """Initialize database with tables and sample data"""
    create_tables()
    
    # Add sample prompt templates
    db = SessionLocal()
    try:
        from models.prompt_model import PromptTemplate
        
        # Check if templates already exist
        existing_templates = db.query(PromptTemplate).count()
        if existing_templates == 0:
            sample_templates = [
                PromptTemplate(
                    name="Dashboard Template",
                    description="Modern dashboard with sidebar navigation and charts",
                    template="Create a modern {type} dashboard with {navigation} navigation, {charts} charts, and {theme} theme",
                    category="dashboard",
                    tags=["dashboard", "charts", "navigation"],
                    variables=["type", "navigation", "charts", "theme"]
                ),
                PromptTemplate(
                    name="Landing Page Template",
                    description="Marketing landing page with hero section",
                    template="Design a {industry} landing page with hero section, {features} features, testimonials, and {cta} call-to-action",
                    category="marketing",
                    tags=["landing", "marketing", "hero"],
                    variables=["industry", "features", "cta"]
                ),
                PromptTemplate(
                    name="E-commerce Template",
                    description="Online store with product catalog",
                    template="Build an e-commerce site for {product_type} with product grid, shopping cart, {payment} payment, and {style} design",
                    category="ecommerce",
                    tags=["ecommerce", "shopping", "products"],
                    variables=["product_type", "payment", "style"]
                ),
                PromptTemplate(
                    name="Blog Template",
                    description="Content blog with article listing",
                    template="Create a {niche} blog with article listing, {layout} layout, search functionality, and {features} features",
                    category="blog",
                    tags=["blog", "content", "articles"],
                    variables=["niche", "layout", "features"]
                )
            ]
            
            for template in sample_templates:
                db.add(template)
            
            db.commit()
            print("Sample prompt templates added to database")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()