"""
Authentication & Security Fundamentals - Protected Notes API
===========================================================

This example demonstrates authentication and security concepts using FastAPI.
Learn how to implement JWT tokens, password hashing, protected endpoints,
and user management through a secure notes application.

Key Concepts Demonstrated:
- JWT token creation and validation
- Password hashing with bcrypt
- Protected endpoints with dependencies
- User registration and login
- Token-based authentication flow
- Role-based access control (RBAC)
- Security middleware and headers
- Authentication error handling

Author: bug6129
"""

from typing import List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import (
    FastAPI, HTTPException, status, Depends, 
    Form, Header, Query
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr

# Create FastAPI app
app = FastAPI(
    title="Authentication Fundamentals - Protected Notes",
    description="Learn authentication and security through a notes management API",
    version="1.0.0"
)

# =============================================================================
# 1. SECURITY CONFIGURATION
# =============================================================================

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production-make-it-long-and-random"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token security
security = HTTPBearer()

# =============================================================================
# 2. DATA MODELS - Users and Authentication
# =============================================================================

class UserRole(str, Enum):
    """User role enumeration."""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class UserBase(SQLModel):
    """Base user model with shared fields."""
    email: str = Field(..., description="User email address", max_length=255)
    full_name: str = Field(..., description="User's full name", max_length=100)
    is_active: bool = Field(default=True, description="Whether user account is active")
    role: UserRole = Field(default=UserRole.USER, description="User role")

class User(UserBase, table=True):
    """User database table model."""
    
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")

class UserCreate(SQLModel):
    """Model for user registration."""
    email: EmailStr = Field(..., description="Valid email address")
    full_name: str = Field(..., description="User's full name", max_length=100)
    password: str = Field(..., description="Password (min 8 characters)", min_length=8)

class UserLogin(SQLModel):
    """Model for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

class UserResponse(SQLModel):
    """Response model for user data (no password)."""
    id: int
    email: str
    full_name: str
    is_active: bool
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# =============================================================================
# Notes Model - Protected Resource
# =============================================================================

class NoteBase(SQLModel):
    """Base note model with shared fields."""
    title: str = Field(..., description="Note title", max_length=200)
    content: str = Field(..., description="Note content")
    is_private: bool = Field(default=True, description="Whether note is private")
    tags: str = Field(default="", description="Comma-separated tags")

class Note(NoteBase, table=True):
    """Note database table model."""
    
    __tablename__ = "notes"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(..., foreign_key="users.id", description="Note owner")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NoteCreate(NoteBase):
    """Model for creating notes."""
    pass

class NoteUpdate(SQLModel):
    """Model for updating notes."""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    is_private: Optional[bool] = None
    tags: Optional[str] = None

class NoteResponse(SQLModel):
    """Response model for note data."""
    id: int
    title: str
    content: str
    is_private: bool
    tags: str
    owner_id: int
    owner_name: str
    created_at: datetime
    updated_at: datetime

# =============================================================================
# 3. DATABASE SETUP
# =============================================================================

DATABASE_URL = "sqlite:///auth_notes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session

# Initialize database
create_db_and_tables()

# =============================================================================
# 4. AUTHENTICATION UTILITIES
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for secure storage."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get user by email address."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return session.get(User, user_id)

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# =============================================================================
# 5. AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    This dependency extracts and validates the JWT token from the Authorization header.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from Authorization header
        token = credentials.credentials
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user email from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = get_user_by_email(session, email)
    if user is None:
        raise credentials_exception
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check for active status)."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user and verify admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# =============================================================================
# 6. SAMPLE DATA CREATION
# =============================================================================

def create_sample_users(session: Session):
    """Create sample users for demonstration."""
    
    # Check if users already exist
    existing_user = session.exec(select(User)).first()
    if existing_user:
        return
    
    sample_users = [
        {
            "email": "admin@example.com",
            "full_name": "System Administrator",
            "password": "admin123",
            "role": UserRole.ADMIN,
            "is_active": True
        },
        {
            "email": "user@example.com",
            "full_name": "Regular User",
            "password": "user123",
            "role": UserRole.USER,
            "is_active": True
        },
        {
            "email": "moderator@example.com",
            "full_name": "Content Moderator",
            "password": "mod123",
            "role": UserRole.MODERATOR,
            "is_active": True
        },
        {
            "email": "inactive@example.com",
            "full_name": "Inactive User",
            "password": "inactive123",
            "role": UserRole.USER,
            "is_active": False
        }
    ]
    
    for user_data in sample_users:
        user = User(
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"],
            is_active=user_data["is_active"],
            created_at=datetime.utcnow()
        )
        session.add(user)
    
    session.commit()
    
    # Create sample notes
    users = session.exec(select(User)).all()
    sample_notes = [
        {
            "title": "Welcome to Protected Notes",
            "content": "This is your first protected note! Only you can see this unless you make it public.",
            "is_private": True,
            "tags": "welcome,getting-started",
            "owner": users[1]  # Regular user
        },
        {
            "title": "Public Announcement",
            "content": "This is a public note that everyone can see.",
            "is_private": False,
            "tags": "public,announcement",
            "owner": users[0]  # Admin
        },
        {
            "title": "Admin Notes",
            "content": "Administrative notes for system management.",
            "is_private": True,
            "tags": "admin,system",
            "owner": users[0]  # Admin
        },
        {
            "title": "Moderation Guidelines",
            "content": "Guidelines for content moderation and community management.",
            "is_private": False,
            "tags": "moderation,guidelines",
            "owner": users[2]  # Moderator
        }
    ]
    
    for note_data in sample_notes:
        note = Note(
            title=note_data["title"],
            content=note_data["content"],
            is_private=note_data["is_private"],
            tags=note_data["tags"],
            owner_id=note_data["owner"].id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(note)
    
    session.commit()
    print("Sample users and notes created!")
    print("Test accounts:")
    print("  admin@example.com / admin123 (Admin)")
    print("  user@example.com / user123 (User)")
    print("  moderator@example.com / mod123 (Moderator)")

# Create sample data on startup
with Session(engine) as session:
    create_sample_users(session)

# =============================================================================
# 7. API ENDPOINTS - Root and Authentication
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API information and authentication endpoints."""
    return {
        "message": "Protected Notes API - Authentication Fundamentals",
        "description": "Learn authentication and security through notes management",
        "authentication": {
            "type": "JWT Bearer Token",
            "login_endpoint": "/auth/login",
            "register_endpoint": "/auth/register",
            "token_header": "Authorization: Bearer <token>"
        },
        "test_accounts": {
            "admin": "admin@example.com / admin123",
            "user": "user@example.com / user123",
            "moderator": "moderator@example.com / mod123"
        },
        "endpoints": {
            "public": ["/", "/auth/login", "/auth/register", "/notes/public"],
            "protected": ["/auth/me", "/notes", "/notes/{id}"],
            "admin_only": ["/admin/users", "/admin/stats"]
        },
        "documentation": "/docs"
    }

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user account.
    
    This endpoint demonstrates:
    - User registration without authentication
    - Password hashing for secure storage
    - Duplicate email validation
    - Account creation workflow
    """
    # Check if user already exists
    existing_user = get_user_by_email(session, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=UserRole.USER,  # Default role
        is_active=True,      # Auto-activate (in production, might require email verification)
        created_at=datetime.utcnow()
    )
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        role=db_user.role,
        created_at=db_user.created_at,
        last_login=db_user.last_login
    )

@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login_user(user_credentials: UserLogin, session: Session = Depends(get_session)):
    """
    Login user and return JWT token.
    
    This endpoint demonstrates:
    - User authentication with email/password
    - JWT token creation
    - Login timestamp tracking
    - Error handling for invalid credentials
    """
    # Authenticate user
    user = authenticate_user(session, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    # Update last login timestamp
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # Return token and user info
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login
        )
    )

@app.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    This endpoint demonstrates:
    - Protected endpoint requiring authentication
    - JWT token validation
    - Current user information retrieval
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role=current_user.role,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

# =============================================================================
# PROTECTED NOTES ENDPOINTS
# =============================================================================

@app.get("/notes", response_model=List[NoteResponse], tags=["Notes"])
async def get_user_notes(
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    include_private: bool = Query(True, description="Include private notes"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get notes for the authenticated user.
    
    This endpoint demonstrates:
    - Protected endpoint requiring authentication
    - User-specific data filtering
    - Authorization (users can only see their own private notes)
    - Optional filtering parameters
    """
    query = select(Note).where(Note.owner_id == current_user.id)
    
    if not include_private:
        query = query.where(Note.is_private == False)
    
    query = query.offset(skip).limit(limit).order_by(Note.updated_at.desc())
    notes = session.exec(query).all()
    
    # Build response with owner information
    note_responses = []
    for note in notes:
        note_responses.append(NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            is_private=note.is_private,
            tags=note.tags,
            owner_id=note.owner_id,
            owner_name=current_user.full_name,
            created_at=note.created_at,
            updated_at=note.updated_at
        ))
    
    return note_responses

@app.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED, tags=["Notes"])
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Create a new note for the authenticated user.
    
    This endpoint demonstrates:
    - Protected resource creation
    - Automatic owner assignment from authenticated user
    - Data validation and sanitization
    """
    db_note = Note(
        **note_data.dict(),
        owner_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        is_private=db_note.is_private,
        tags=db_note.tags,
        owner_id=db_note.owner_id,
        owner_name=current_user.full_name,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

@app.get("/notes/{note_id}", response_model=NoteResponse, tags=["Notes"])
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific note.
    
    This endpoint demonstrates:
    - Resource-level authorization
    - Owner verification for private notes
    - Public note access for all authenticated users
    """
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Authorization check: users can only see their own private notes
    if note.is_private and note.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: This is a private note"
        )
    
    # Get owner information
    owner = session.get(User, note.owner_id)
    
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        is_private=note.is_private,
        tags=note.tags,
        owner_id=note.owner_id,
        owner_name=owner.full_name if owner else "Unknown",
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.put("/notes/{note_id}", response_model=NoteResponse, tags=["Notes"])
async def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Update a note (only owner can update).
    
    This endpoint demonstrates:
    - Ownership-based authorization
    - Partial resource updates
    - Update timestamp management
    """
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Authorization: only owner can update
    if note.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only update your own notes"
        )
    
    # Update fields
    update_data = note_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(note, field, value)
    
    note.updated_at = datetime.utcnow()
    session.add(note)
    session.commit()
    session.refresh(note)
    
    return NoteResponse(
        id=note.id,
        title=note.title,
        content=note.content,
        is_private=note.is_private,
        tags=note.tags,
        owner_id=note.owner_id,
        owner_name=current_user.full_name,
        created_at=note.created_at,
        updated_at=note.updated_at
    )

@app.delete("/notes/{note_id}", tags=["Notes"])
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Delete a note (only owner can delete).
    
    This endpoint demonstrates:
    - Ownership-based authorization
    - Resource deletion with proper authorization
    """
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Authorization: only owner can delete
    if note.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only delete your own notes"
        )
    
    session.delete(note)
    session.commit()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Note '{note.title}' has been deleted successfully",
            "note_id": note_id
        }
    )

# =============================================================================
# PUBLIC ENDPOINTS (No Authentication Required)
# =============================================================================

@app.get("/notes/public", response_model=List[NoteResponse], tags=["Public"])
async def get_public_notes(
    session: Session = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get public notes (no authentication required).
    
    This endpoint demonstrates:
    - Public access without authentication
    - Filtering for public content only
    - Anonymous access patterns
    """
    query = select(Note).where(Note.is_private == False)
    query = query.offset(skip).limit(limit).order_by(Note.created_at.desc())
    notes = session.exec(query).all()
    
    note_responses = []
    for note in notes:
        # Get owner information
        owner = session.get(User, note.owner_id)
        
        note_responses.append(NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            is_private=note.is_private,
            tags=note.tags,
            owner_id=note.owner_id,
            owner_name=owner.full_name if owner else "Unknown",
            created_at=note.created_at,
            updated_at=note.updated_at
        ))
    
    return note_responses

# =============================================================================
# ADMIN ENDPOINTS - Role-Based Access Control
# =============================================================================

@app.get("/admin/users", response_model=List[UserResponse], tags=["Admin"])
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
    include_inactive: bool = Query(False, description="Include inactive users"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    Get all users (admin only).
    
    This endpoint demonstrates:
    - Role-based access control (RBAC)
    - Admin-only functionality
    - User management capabilities
    """
    query = select(User)
    
    if not include_inactive:
        query = query.where(User.is_active == True)
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    users = session.exec(query).all()
    
    return [
        UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login
        )
        for user in users
    ]

@app.get("/admin/stats", tags=["Admin"])
async def get_admin_stats(
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    """
    Get system statistics (admin only).
    
    This endpoint demonstrates:
    - Admin-only analytics
    - System monitoring capabilities
    - Role-based data access
    """
    # User statistics
    total_users = len(session.exec(select(User)).all())
    active_users = len(session.exec(select(User).where(User.is_active == True)).all())
    admin_users = len(session.exec(select(User).where(User.role == UserRole.ADMIN)).all())
    
    # Notes statistics
    total_notes = len(session.exec(select(Note)).all())
    private_notes = len(session.exec(select(Note).where(Note.is_private == True)).all())
    public_notes = len(session.exec(select(Note).where(Note.is_private == False)).all())
    
    # User activity
    users_with_notes = len(session.exec(
        select(User).join(Note, User.id == Note.owner_id)
    ).unique().all())
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users,
            "admins": admin_users,
            "users_with_notes": users_with_notes
        },
        "notes": {
            "total": total_notes,
            "private": private_notes,
            "public": public_notes,
            "avg_per_user": round(total_notes / users_with_notes, 2) if users_with_notes > 0 else 0
        },
        "security": {
            "jwt_algorithm": ALGORITHM,
            "token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
            "password_hashing": "bcrypt"
        },
        "admin_requested_by": admin_user.email
    }

@app.patch("/admin/users/{user_id}/toggle", response_model=UserResponse, tags=["Admin"])
async def toggle_user_status(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session)
):
    """
    Toggle user active status (admin only).
    
    This endpoint demonstrates:
    - Admin user management
    - Account activation/deactivation
    - Administrative controls
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Toggle active status
    user.is_active = not user.is_active
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        role=user.role,
        created_at=user.created_at,
        last_login=user.last_login
    )

# =============================================================================
# HEALTH CHECK AND SYSTEM INFO
# =============================================================================

@app.get("/health", tags=["System"])
async def health_check(session: Session = Depends(get_session)):
    """Health check with authentication system status."""
    try:
        # Test database connection
        user_count = len(session.exec(select(User)).all())
        note_count = len(session.exec(select(Note)).all())
        
        return {
            "status": "healthy",
            "service": "Protected Notes API - Authentication Fundamentals",
            "database": {
                "status": "connected",
                "user_count": user_count,
                "note_count": note_count
            },
            "security": {
                "jwt_enabled": True,
                "password_hashing": "bcrypt",
                "token_expiry_minutes": ACCESS_TOKEN_EXPIRE_MINUTES
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
        )

# Main execution
if __name__ == "__main__":
    import uvicorn
    print("🚀 Authentication Fundamentals - Protected Notes API")
    print("=" * 65)
    print("This tutorial demonstrates authentication and security through notes management.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Public Notes: http://localhost:8000/notes/public")
    print("")
    print("🔑 Test Accounts:")
    print("   • Admin: admin@example.com / admin123")
    print("   • User: user@example.com / user123")
    print("   • Moderator: moderator@example.com / mod123")
    print("")
    print("🔐 Authentication Flow:")
    print("   1. POST /auth/register - Create new account")
    print("   2. POST /auth/login - Get JWT token")
    print("   3. Use token in Authorization: Bearer <token>")
    print("   4. Access protected endpoints")
    print("")
    print("📚 What you'll learn:")
    print("   • JWT token creation and validation")
    print("   • Password hashing with bcrypt")
    print("   • Protected endpoints with dependencies")
    print("   • Role-based access control (RBAC)")
    print("   • User registration and login flow")
    print("   • Authentication error handling")
    print("")
    print("🎯 Try these operations:")
    print("   1. POST /auth/login - Login with test account")
    print("   2. GET /auth/me - Get your user info")
    print("   3. POST /notes - Create a protected note")
    print("   4. GET /notes - Get your notes")
    print("   5. GET /admin/users - Admin-only endpoint")
    print("")
    print("💾 Database: auth_notes.db")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 65)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)