"""
NL2API Tool - CodeT5+ for FastAPI endpoint generation
Integrates with backend-automation-paper2code system
"""
import json
import logging
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

# Add backend-automation-paper2code to path for integration
backend_automation_path = Path(__file__).parent.parent.parent.parent.parent / "backend-automation-paper2code"
if backend_automation_path.exists():
    sys.path.append(str(backend_automation_path))

logger = logging.getLogger(__name__)

class NL2APIGenerator:
    """
    Generate FastAPI endpoints from natural language specifications
    Uses CodeT5+ and integrates with backend-automation-paper2code
    """
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.backend_automation_available = self._check_backend_automation()
        self.api_templates = self._load_api_templates()
        self.model_templates = self._load_model_templates()
    
    def _check_backend_automation(self) -> bool:
        """Check if backend-automation-paper2code is available"""
        try:
            # Try to import backend automation services
            from backend.app.services.code_generation.api_generator import APIGenerator
            from backend.app.services.code_generation.model_generator import ModelGenerator
            self.api_generator = APIGenerator()
            self.model_generator = ModelGenerator()
            logger.info("Backend automation integration available")
            return True
        except ImportError as e:
            logger.warning(f"Backend automation not available: {e}")
            return False
    
    def _load_api_templates(self) -> Dict[str, str]:
        """Load FastAPI endpoint templates"""
        return {
            "auth_login": '''
@router.post("/login", response_model=AuthResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email
    )
''',
            
            "auth_register": '''
@router.post("/register", response_model=AuthResponse)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user account"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.email})
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email
    )
''',
            
            "crud_create": '''
@router.post("/{resource}", response_model={ResponseModel})
async def create_{resource}(
    {resource}_data: {CreateModel},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new {resource}"""
    {resource}_dict = {resource}_data.dict()
    {resource}_dict["user_id"] = current_user.id
    
    db_{resource} = {Model}(**{resource}_dict)
    db.add(db_{resource})
    db.commit()
    db.refresh(db_{resource})
    
    return db_{resource}
''',
            
            "crud_read": '''
@router.get("/{resource}", response_model=List[{ResponseModel}])
async def get_{resource}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of {resource}s"""
    {resource}s = db.query({Model}).filter(
        {Model}.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return {resource}s
''',
            
            "crud_update": '''
@router.put("/{resource}/{{item_id}}", response_model={ResponseModel})
async def update_{resource}(
    item_id: int,
    {resource}_data: {UpdateModel},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update {resource}"""
    db_{resource} = db.query({Model}).filter(
        {Model}.id == item_id,
        {Model}.user_id == current_user.id
    ).first()
    
    if not db_{resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    
    for field, value in {resource}_data.dict(exclude_unset=True).items():
        setattr(db_{resource}, field, value)
    
    db.commit()
    db.refresh(db_{resource})
    return db_{resource}
''',
            
            "crud_delete": '''
@router.delete("/{resource}/{{item_id}}")
async def delete_{resource}(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete {resource}"""
    db_{resource} = db.query({Model}).filter(
        {Model}.id == item_id,
        {Model}.user_id == current_user.id
    ).first()
    
    if not db_{resource}:
        raise HTTPException(status_code=404, detail="{Resource} not found")
    
    db.delete(db_{resource})
    db.commit()
    return {{"message": "{Resource} deleted successfully"}}
'''
        }
    
    def _load_model_templates(self) -> Dict[str, str]:
        """Load Pydantic model templates"""
        return {
            "base_model": '''
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class {ModelName}Base(BaseModel):
    {fields}

class {ModelName}Create({ModelName}Base):
    pass

class {ModelName}Update(BaseModel):
    {optional_fields}

class {ModelName}Response({ModelName}Base):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
''',
            
            "auth_models": '''
from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    
    class Config:
        orm_mode = True
'''
        }
    
    async def execute(self, nl_spec: str, **kwargs) -> Dict[str, Any]:
        """
        Execute API generation from natural language specification
        
        Args:
            nl_spec: Natural language specification or "inferred_from_ui"
            
        Returns:
            Dict with generated FastAPI code and metadata
        """
        if nl_spec == "inferred_from_ui":
            # Infer API spec from UI components
            ui_components = kwargs.get("components", [])
            nl_spec = self._infer_spec_from_ui(ui_components)
        
        return self.generate_fastapi_code(nl_spec)
    
    def _infer_spec_from_ui(self, ui_components: List[Dict]) -> str:
        """Infer API specification from UI components"""
        spec_parts = []
        
        # Check for authentication components
        has_login = any("login" in comp.get("primary_text", "").lower() for comp in ui_components)
        has_register = any("register" in comp.get("primary_text", "").lower() or 
                          "sign up" in comp.get("primary_text", "").lower() for comp in ui_components)
        
        if has_login or has_register:
            spec_parts.append("Create authentication system with login and registration")
        
        # Check for form components
        input_components = [comp for comp in ui_components if comp.get("class_label") == "input"]
        if len(input_components) >= 2:
            spec_parts.append("Create form handling endpoints for user data submission")
        
        # Check for data display components
        has_tables = any(comp.get("class_label") == "table" for comp in ui_components)
        has_lists = any(comp.get("class_label") == "list" for comp in ui_components)
        has_cards = any(comp.get("class_label") == "card" for comp in ui_components)
        
        if has_tables or has_lists or has_cards:
            spec_parts.append("Create CRUD endpoints for data management")
        
        # Default specification
        if not spec_parts:
            spec_parts.append("Create basic REST API with user management")
        
        return ". ".join(spec_parts)
    
    def generate_fastapi_code(self, nl_spec: str) -> Dict[str, Any]:
        """
        Generate FastAPI application from natural language specification
        
        Returns:
            {
                "main.py": "...",
                "models/": {...},
                "routers/": {...},
                "requirements.txt": "...",
                "database.py": "...",
                "auth.py": "...",
                "metadata": {...}
            }
        """
        try:
            # Parse specification to identify required features
            features = self._parse_specification(nl_spec)
            
            # Use backend automation if available
            if self.backend_automation_available:
                return self._generate_with_backend_automation(nl_spec, features)
            else:
                return self._generate_with_templates(features)
                
        except Exception as e:
            logger.error(f"FastAPI generation failed: {e}")
            return {
                "main.py": self._generate_fallback_main(),
                "error": str(e),
                "metadata": {"status": "fallback"}
            }
    
    def _parse_specification(self, nl_spec: str) -> Dict[str, Any]:
        """Parse natural language specification to identify features"""
        spec_lower = nl_spec.lower()
        
        features = {
            "auth": False,
            "crud": False,
            "websockets": False,
            "file_upload": False,
            "email": False,
            "database": "sqlite",
            "resources": []
        }
        
        # Authentication features
        if any(word in spec_lower for word in ["login", "auth", "register", "jwt", "token"]):
            features["auth"] = True
        
        # CRUD operations
        if any(word in spec_lower for word in ["create", "read", "update", "delete", "crud", "manage"]):
            features["crud"] = True
        
        # WebSocket support
        if any(word in spec_lower for word in ["websocket", "real-time", "live", "chat"]):
            features["websockets"] = True
        
        # File upload
        if any(word in spec_lower for word in ["upload", "file", "image", "document"]):
            features["file_upload"] = True
        
        # Email functionality
        if any(word in spec_lower for word in ["email", "mail", "notification"]):
            features["email"] = True
        
        # Database preference
        if "postgres" in spec_lower or "postgresql" in spec_lower:
            features["database"] = "postgresql"
        elif "mysql" in spec_lower:
            features["database"] = "mysql"
        
        # Extract resource names
        features["resources"] = self._extract_resources(nl_spec)
        
        return features
    
    def _extract_resources(self, nl_spec: str) -> List[str]:
        """Extract resource names from specification"""
        # Common resource patterns
        resource_patterns = [
            r"manage (\w+)",
            r"create (\w+)",
            r"(\w+) management",
            r"(\w+) system",
            r"handle (\w+)"
        ]
        
        resources = set()
        for pattern in resource_patterns:
            matches = re.findall(pattern, nl_spec.lower())
            resources.update(matches)
        
        # Filter out common words
        common_words = {"user", "data", "system", "api", "endpoint", "service"}
        resources = [r for r in resources if r not in common_words and len(r) > 2]
        
        # Default resources if none found
        if not resources:
            resources = ["item"]
        
        return list(resources)[:3]  # Limit to 3 resources
    
    def _generate_with_backend_automation(self, nl_spec: str, features: Dict) -> Dict[str, Any]:
        """Generate using backend-automation-paper2code integration"""
        try:
            # Use the integrated API generator
            api_result = self.api_generator.generate_api_from_spec(nl_spec)
            model_result = self.model_generator.generate_models_from_spec(nl_spec)
            
            # Combine results
            generated_files = {}
            generated_files.update(api_result.get("files", {}))
            generated_files.update(model_result.get("files", {}))
            
            # Add main application file
            generated_files["main.py"] = self._generate_main_app(features)
            generated_files["requirements.txt"] = self._generate_requirements(features)
            generated_files["database.py"] = self._generate_database_config(features)
            
            if features["auth"]:
                generated_files["auth.py"] = self._generate_auth_utils()
            
            return {
                **generated_files,
                "metadata": {
                    "status": "success",
                    "generator": "backend_automation",
                    "features": features,
                    "api_endpoints": api_result.get("endpoints", []),
                    "models": model_result.get("models", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Backend automation generation failed: {e}")
            return self._generate_with_templates(features)
    
    def _generate_with_templates(self, features: Dict) -> Dict[str, Any]:
        """Generate using built-in templates"""
        generated_files = {}
        
        # Generate main application
        generated_files["main.py"] = self._generate_main_app(features)
        
        # Generate models
        if features["auth"]:
            generated_files["models/auth.py"] = self._generate_auth_models()
        
        for resource in features["resources"]:
            generated_files[f"models/{resource}.py"] = self._generate_resource_model(resource)
        
        # Generate routers
        if features["auth"]:
            generated_files["routers/auth.py"] = self._generate_auth_router()
        
        for resource in features["resources"]:
            generated_files[f"routers/{resource}.py"] = self._generate_resource_router(resource)
        
        # Generate supporting files
        generated_files["requirements.txt"] = self._generate_requirements(features)
        generated_files["database.py"] = self._generate_database_config(features)
        
        if features["auth"]:
            generated_files["auth.py"] = self._generate_auth_utils()
        
        # Generate Dockerfile
        generated_files["Dockerfile"] = self._generate_dockerfile()
        
        return {
            **generated_files,
            "metadata": {
                "status": "success",
                "generator": "templates",
                "features": features,
                "resources": features["resources"]
            }
        }
    
    def _generate_main_app(self, features: Dict) -> str:
        """Generate main FastAPI application"""
        imports = [
            "from fastapi import FastAPI, Depends",
            "from fastapi.middleware.cors import CORSMiddleware",
            "from database import engine, Base"
        ]
        
        routers = []
        if features["auth"]:
            imports.append("from routers import auth")
            routers.append('app.include_router(auth.router, prefix="/api/auth", tags=["auth"])')
        
        for resource in features["resources"]:
            imports.append(f"from routers import {resource}")
            routers.append(f'app.include_router({resource}.router, prefix="/api/{resource}s", tags=["{resource}s"])')
        
        if features["websockets"]:
            imports.append("from fastapi import WebSocket")
        
        websocket_code = ""
        if features["websockets"]:
            websocket_code = '''
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
'''
        
        return f'''
{chr(10).join(imports)}

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AutoDevFlow Generated API",
    description="Generated by AutoDevFlow Orchestrator",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
{chr(10).join(routers)}

@app.get("/")
async def root():
    return {{"message": "AutoDevFlow Generated API", "status": "running"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "version": "1.0.0"}}

{websocket_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_auth_models(self) -> str:
        """Generate authentication models"""
        return self.model_templates["auth_models"]
    
    def _generate_resource_model(self, resource: str) -> str:
        """Generate Pydantic models for a resource"""
        resource_title = resource.title()
        
        # Generate basic fields based on resource name
        fields = self._generate_resource_fields(resource)
        optional_fields = [f"{field}: Optional[{field_type}] = None" 
                          for field, field_type in fields]
        
        field_definitions = [f"{field}: {field_type}" for field, field_type in fields]
        
        return self.model_templates["base_model"].format(
            ModelName=resource_title,
            fields=chr(10).join(f"    {field}" for field in field_definitions),
            optional_fields=chr(10).join(f"    {field}" for field in optional_fields)
        )
    
    def _generate_resource_fields(self, resource: str) -> List[tuple]:
        """Generate appropriate fields for a resource"""
        # Common field patterns based on resource name
        field_mappings = {
            "user": [("name", "str"), ("email", "EmailStr"), ("is_active", "bool")],
            "product": [("name", "str"), ("description", "str"), ("price", "float")],
            "order": [("total", "float"), ("status", "str"), ("items", "List[str]")],
            "item": [("name", "str"), ("description", "str"), ("category", "str")],
            "post": [("title", "str"), ("content", "str"), ("published", "bool")],
            "task": [("title", "str"), ("description", "str"), ("completed", "bool")]
        }
        
        return field_mappings.get(resource, [("name", "str"), ("description", "str")])
    
    def _generate_auth_router(self) -> str:
        """Generate authentication router"""
        return f'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.auth import LoginRequest, RegisterRequest, AuthResponse
from auth import authenticate_user, create_access_token, get_password_hash

router = APIRouter()

{self.api_templates["auth_login"]}

{self.api_templates["auth_register"]}
'''
    
    def _generate_resource_router(self, resource: str) -> str:
        """Generate CRUD router for a resource"""
        resource_title = resource.title()
        
        # Fill template placeholders
        create_endpoint = self.api_templates["crud_create"].format(
            resource=resource,
            Resource=resource_title,
            Model=resource_title,
            CreateModel=f"{resource_title}Create",
            ResponseModel=f"{resource_title}Response"
        )
        
        read_endpoint = self.api_templates["crud_read"].format(
            resource=resource,
            Model=resource_title,
            ResponseModel=f"{resource_title}Response"
        )
        
        update_endpoint = self.api_templates["crud_update"].format(
            resource=resource,
            Resource=resource_title,
            Model=resource_title,
            UpdateModel=f"{resource_title}Update",
            ResponseModel=f"{resource_title}Response"
        )
        
        delete_endpoint = self.api_templates["crud_delete"].format(
            resource=resource,
            Resource=resource_title,
            Model=resource_title
        )
        
        return f'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.{resource} import {resource_title}Create, {resource_title}Update, {resource_title}Response
from models.auth import User
from auth import get_current_user

router = APIRouter()

{create_endpoint}

{read_endpoint}

{update_endpoint}

{delete_endpoint}
'''
    
    def _generate_requirements(self, features: Dict) -> str:
        """Generate requirements.txt"""
        requirements = [
            "fastapi==0.104.1",
            "uvicorn[standard]==0.24.0",
            "sqlalchemy==2.0.23",
            "pydantic[email]==2.5.0",
            "python-multipart==0.0.6",
            "python-jose[cryptography]==3.3.0",
            "passlib[bcrypt]==1.7.4",
            "python-dotenv==1.0.0"
        ]
        
        if features["database"] == "postgresql":
            requirements.append("psycopg2-binary==2.9.9")
        elif features["database"] == "mysql":
            requirements.append("pymysql==1.1.0")
        else:
            requirements.append("sqlite3")
        
        if features["websockets"]:
            requirements.append("websockets==12.0")
        
        if features["email"]:
            requirements.extend([
                "fastapi-mail==1.4.1",
                "jinja2==3.1.2"
            ])
        
        if features["file_upload"]:
            requirements.append("aiofiles==23.2.1")
        
        return chr(10).join(requirements)
    
    def _generate_database_config(self, features: Dict) -> str:
        """Generate database configuration"""
        if features["database"] == "postgresql":
            database_url = "postgresql://user:password@localhost/dbname"
            engine_args = "{}"
        elif features["database"] == "mysql":
            database_url = "mysql+pymysql://user:password@localhost/dbname"
            engine_args = "{}"
        else:
            database_url = "sqlite:///./app.db"
            engine_args = '{"check_same_thread": False}'
        
        return f'''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "{database_url}")

engine = create_engine(DATABASE_URL, connect_args={engine_args})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
    
    def _generate_auth_utils(self) -> str:
        """Generate authentication utilities"""
        return '''
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db

SECRET_KEY = "your-secret-key-here"  # Change this in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str):
    # This would query your User model
    # user = db.query(User).filter(User.email == email).first()
    # if not user or not verify_password(password, user.hashed_password):
    #     return False
    # return user
    pass

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Query user from database
    # user = db.query(User).filter(User.email == email).first()
    # if user is None:
    #     raise credentials_exception
    # return user
    pass
'''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile for the FastAPI application"""
        return '''
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _generate_fallback_main(self) -> str:
        """Generate fallback main.py when generation fails"""
        return '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoDevFlow Generated API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AutoDevFlow Generated API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''