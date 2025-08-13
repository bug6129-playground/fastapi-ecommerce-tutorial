# Tutorial B2: User Management System

**Build a production-ready user management system for your e-commerce API** 👥

In this tutorial, you'll apply Pydantic concepts to build a complete user management system. You'll learn how to design data models for real-world e-commerce requirements, handle complex validation scenarios, and structure your application for maintainability.

## 🎯 Learning Objectives

By the end of this tutorial, you'll be able to:
- ✅ Design comprehensive user data models for e-commerce
- ✅ Implement advanced validation rules for business requirements
- ✅ Separate database models from API schemas effectively
- ✅ Handle complex user registration and profile management
- ✅ Structure user-related code using service patterns
- ✅ Implement proper error handling and response models

## 🏗️ What We're Building

### **Complete User Management System**

**User Registration**:
- Email validation and uniqueness checking
- Password strength requirements
- Profile information collection
- Terms acceptance and verification

**User Profiles**:
- Personal information management
- Address management for shipping
- Preference settings
- Account status tracking

**User Roles & Permissions**:
- Customer, admin, and staff roles
- Role-based access control foundation
- Account activation and verification

## ⚡ Prerequisites

**Before starting this tutorial:**
1. Complete [Tutorial B1: E-Commerce Foundation](../01-getting-started/apply-ecommerce.md)
2. Understand [Tutorial A2: Pydantic Fundamentals](learn-pydantic.md) concepts
3. Have the e-commerce app running from Chapter 1

## 🚀 Setup

### Step 1: Navigate to E-Commerce App
```bash
cd ecommerce-app
```

### Step 2: Install Additional Dependencies
```bash
# Install email validation and password hashing
pip install "pydantic[email]" "passlib[bcrypt]"
```

### Step 3: Verify Base Application
```bash
python -m uvicorn app.main:app --reload
# Visit http://localhost:8000 to confirm base app works
```

## 📋 Architecture Overview

### **User System Components**

```
app/
├── models/
│   └── user.py          # Database models (SQLModel)
├── schemas/
│   └── user.py          # API request/response models (Pydantic)
├── routers/
│   └── users.py         # API endpoints
├── services/
│   └── user_service.py  # Business logic
└── utils/
    └── security.py      # Password hashing, validation
```

### **Data Flow Pattern**

```
API Request → Pydantic Schema → Service Layer → SQLModel → Database
                     ↓
API Response ← Response Schema ← Service Layer ← SQLModel ← Database
```

## 🎨 Step 1: User Database Models

Let's start by creating the database models that represent how user data is stored:

### Create `app/models/user.py`

```python
"""
User Database Models
===================

SQLModel models that define how user data is stored in the database.
These models represent the actual database tables and relationships.

Author: bug6129
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

class UserRole(str, Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"

class UserStatus(str, Enum):
    """User account status."""
    PENDING = "pending"        # Email not verified
    ACTIVE = "active"          # Normal active user
    SUSPENDED = "suspended"    # Temporarily suspended
    BANNED = "banned"         # Permanently banned

# Base class for shared user fields
class UserBase(SQLModel):
    """Base user model with shared fields."""
    
    # Personal Information
    email: str = Field(unique=True, index=True, max_length=255)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    
    # Account Information
    role: UserRole = Field(default=UserRole.CUSTOMER)
    status: UserStatus = Field(default=UserStatus.PENDING)
    is_email_verified: bool = Field(default=False)
    
    # Profile Information
    phone: Optional[str] = Field(default=None, max_length=20)
    date_of_birth: Optional[datetime] = Field(default=None)
    
    # Preferences
    newsletter_subscribed: bool = Field(default=True)
    marketing_emails: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = Field(default=None)

# Database table model
class User(UserBase, table=True):
    """User database table model."""
    
    __tablename__ = "users"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Authentication
    hashed_password: str = Field(max_length=255)
    
    # Relationships (we'll add these in future chapters)
    # addresses: List["Address"] = Relationship(back_populates="user")
    # orders: List["Order"] = Relationship(back_populates="customer")

# For creating users (excludes computed fields)
class UserCreate(UserBase):
    """Model for creating new users."""
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)
    terms_accepted: bool = Field(description="User must accept terms and conditions")

# For updating users (all fields optional)
class UserUpdate(SQLModel):
    """Model for updating existing users."""
    first_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    date_of_birth: Optional[datetime] = Field(default=None)
    newsletter_subscribed: Optional[bool] = Field(default=None)
    marketing_emails: Optional[bool] = Field(default=None)

# Address model (for shipping addresses)
class AddressBase(SQLModel):
    """Base address model."""
    street_address: str = Field(max_length=200)
    apartment: Optional[str] = Field(default=None, max_length=50)
    city: str = Field(max_length=100)
    state_province: str = Field(max_length=100)
    postal_code: str = Field(max_length=20)
    country: str = Field(default="USA", max_length=100)
    is_default: bool = Field(default=False)

class Address(AddressBase, table=True):
    """Address database table."""
    
    __tablename__ = "addresses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    # user: User = Relationship(back_populates="addresses")
```

## 🔧 Step 2: API Schema Models

Now let's create the Pydantic models that define the API interface:

### Create `app/schemas/user.py`

```python
"""
User API Schemas
===============

Pydantic models that define the API request/response interface.
These models handle validation, serialization, and documentation.

Author: bug6129
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from ..models.user import UserRole, UserStatus

# =============================================================================
# REQUEST MODELS (What the API accepts)
# =============================================================================

class UserRegistration(BaseModel):
    """Model for user registration requests."""
    
    # Personal Information
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., min_length=2, max_length=50, description="First name")
    last_name: str = Field(..., min_length=2, max_length=50, description="Last name")
    
    # Authentication
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100, 
        description="Password (min 8 characters)"
    )
    confirm_password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="Password confirmation"
    )
    
    # Contact Information
    phone: Optional[str] = Field(
        None, 
        description="Phone number (optional)",
        regex=r'^\+?[\d\s\-\(\)]+$'
    )
    date_of_birth: Optional[datetime] = Field(None, description="Date of birth")
    
    # Preferences
    newsletter_subscribed: bool = Field(
        default=True, 
        description="Subscribe to newsletter"
    )
    marketing_emails: bool = Field(
        default=False, 
        description="Receive marketing emails"
    )
    
    # Legal
    terms_accepted: bool = Field(
        ..., 
        description="Must accept terms and conditions"
    )
    
    # Custom validators
    @validator('first_name', 'last_name')
    def name_must_be_alpha(cls, v):
        """Names should contain only letters and common characters."""
        if not v.replace('-', '').replace("'", '').replace(' ', '').isalpha():
            raise ValueError('Names must contain only letters, hyphens, and apostrophes')
        return v.title()  # Capitalize properly
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, and one digit'
            )
        
        return v
    
    @validator('phone')
    def validate_phone_number(cls, v):
        """Clean and validate phone number format."""
        if v is None:
            return v
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, v))
        
        # Validate length (US phone numbers)
        if len(digits) not in [10, 11]:  # 10 digits or 11 with country code
            raise ValueError('Phone number must be 10 or 11 digits')
        
        # Format as (XXX) XXX-XXXX
        if len(digits) == 11 and digits[0] == '1':
            digits = digits[1:]  # Remove country code
        
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        """Ensure user is at least 13 years old."""
        if v is None:
            return v
        
        today = datetime.now().date()
        age = today.year - v.date().year
        
        # Adjust for birthday not yet occurred this year
        if today < v.date().replace(year=today.year):
            age -= 1
        
        if age < 13:
            raise ValueError('User must be at least 13 years old')
        
        return v
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        """Terms and conditions must be accepted."""
        if not v:
            raise ValueError('You must accept the terms and conditions')
        return v
    
    @root_validator
    def passwords_match(cls, values):
        """Ensure password and confirm_password match."""
        password = values.get('password')
        confirm_password = values.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValueError('Passwords do not match')
        
        return values
    
    class Config:
        schema_extra = {
            "example": {
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Johnson", 
                "password": "SecurePass123",
                "confirm_password": "SecurePass123",
                "phone": "(555) 123-4567",
                "newsletter_subscribed": True,
                "marketing_emails": False,
                "terms_accepted": True
            }
        }

class UserProfileUpdate(BaseModel):
    """Model for updating user profile information."""
    
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    phone: Optional[str] = Field(None, regex=r'^\+?[\d\s\-\(\)]+$')
    date_of_birth: Optional[datetime] = None
    newsletter_subscribed: Optional[bool] = None
    marketing_emails: Optional[bool] = None
    
    @validator('first_name', 'last_name')
    def name_must_be_alpha(cls, v):
        if v and not v.replace('-', '').replace("'", '').replace(' ', '').isalpha():
            raise ValueError('Names must contain only letters, hyphens, and apostrophes')
        return v.title() if v else v
    
    @validator('phone')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) not in [10, 11]:
            raise ValueError('Phone number must be 10 or 11 digits')
        
        if len(digits) == 11 and digits[0] == '1':
            digits = digits[1:]
        
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

class AddressCreate(BaseModel):
    """Model for creating new addresses."""
    
    street_address: str = Field(..., min_length=5, max_length=200)
    apartment: Optional[str] = Field(None, max_length=50)
    city: str = Field(..., min_length=2, max_length=100)
    state_province: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., min_length=3, max_length=20)
    country: str = Field(default="USA", max_length=100)
    is_default: bool = Field(default=False)
    
    @validator('postal_code')
    def validate_postal_code(cls, v, values):
        """Validate postal code format based on country."""
        country = values.get('country', 'USA')
        
        if country.upper() == 'USA':
            # US ZIP code validation
            import re
            if not re.match(r'^\d{5}(-\d{4})?$', v):
                raise ValueError('US postal code must be in format: 12345 or 12345-6789')
        
        return v

# =============================================================================
# RESPONSE MODELS (What the API returns)
# =============================================================================

class UserResponse(BaseModel):
    """Model for user responses (excludes sensitive information)."""
    
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    phone: Optional[str]
    date_of_birth: Optional[datetime]
    newsletter_subscribed: bool
    marketing_emails: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    
    # Computed fields
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self) -> str:
        """Get display-friendly name."""
        return self.full_name or self.email
    
    class Config:
        orm_mode = True  # Allow creating from ORM objects

class UserPublicProfile(BaseModel):
    """Public user profile (minimal information)."""
    
    id: int
    first_name: str
    last_name: str
    created_at: datetime
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class AddressResponse(BaseModel):
    """Model for address responses."""
    
    id: int
    street_address: str
    apartment: Optional[str]
    city: str
    state_province: str
    postal_code: str
    country: str
    is_default: bool
    created_at: datetime
    updated_at: datetime
    
    @property
    def formatted_address(self) -> str:
        """Get formatted address string."""
        parts = [self.street_address]
        if self.apartment:
            parts.append(f"Apt {self.apartment}")
        parts.append(f"{self.city}, {self.state_province} {self.postal_code}")
        if self.country != "USA":
            parts.append(self.country)
        return ", ".join(parts)
    
    class Config:
        orm_mode = True

# =============================================================================
# STATUS AND ERROR MODELS
# =============================================================================

class UserRegistrationResponse(BaseModel):
    """Response model for successful registration."""
    
    message: str
    user: UserResponse
    verification_required: bool = True
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Registration successful! Please check your email to verify your account.",
                "user": {
                    "id": 1,
                    "email": "alice@example.com",
                    "first_name": "Alice",
                    "last_name": "Johnson",
                    "status": "pending"
                },
                "verification_required": True
            }
        }

class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""
    
    field: str
    message: str
    invalid_value: Optional[str] = None

class ValidationErrorResponse(BaseModel):
    """Response for validation errors."""
    
    error_type: str = "validation_error"
    message: str = "Invalid input data"
    details: List[ValidationErrorDetail]
    
    class Config:
        schema_extra = {
            "example": {
                "error_type": "validation_error",
                "message": "Invalid input data",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "invalid_value": "invalid-email"
                    },
                    {
                        "field": "password",
                        "message": "Password must contain at least one uppercase letter",
                        "invalid_value": None
                    }
                ]
            }
        }
```

## 🔧 Step 3: Service Layer

The service layer contains all business logic and coordinates between the API and database:

### Create `app/services/user_service.py`

```python
"""
User Service Layer - Business Logic Hub

This service handles:
- User registration with validation
- Authentication and password management
- Profile updates and management
- Address management
- Business rule enforcement
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from ..models.user import User, UserCreate, UserUpdate, Address, UserRole, UserStatus
from ..schemas.user import (
    UserRegistration, UserResponse, UserRegistrationResponse, 
    AddressCreate, AddressResponse, UserProfileUpdate
)
from ..utils.security import hash_password, verify_password, sanitize_email
from fastapi import HTTPException, status

class UserService:
    """Main service class for user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UserRegistration) -> UserRegistrationResponse:
        """Register new user with full validation."""
        
        # Check email uniqueness
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(400, "Email already registered")
        
        # Create user with hashed password
        db_user = User(
            email=sanitize_email(user_data.email),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hash_password(user_data.password),
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            newsletter_subscribed=user_data.newsletter_subscribed,
            marketing_emails=user_data.marketing_emails,
            role=UserRole.CUSTOMER,
            status=UserStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserRegistrationResponse(
            message="Registration successful! Check your email for verification.",
            user=UserResponse.from_orm(db_user),
            verification_required=True
        )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        # Update login timestamp
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        return user
    
    # ... Additional methods for profile management, addresses, etc.
```

**Key Service Concepts**:
- **Business Logic Separation**: All rules live in the service layer
- **Database Abstraction**: Services handle database operations
- **Error Handling**: Consistent error responses
- **Validation Coordination**: Services coordinate with Pydantic models

## 🛣️ Step 4: API Router

Create the REST API endpoints that tie everything together:

### Create `app/routers/users.py`

```python
"""
User API Endpoints - Complete REST Interface

This router provides:
- User registration and authentication
- Profile management
- Address management
- Educational examples and documentation
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..schemas.user import (
    UserRegistration, UserResponse, UserRegistrationResponse,
    UserProfileUpdate, AddressCreate, AddressResponse
)
from ..services.user_service import UserService, get_user_service
from ..database import get_session

router = APIRouter(prefix="/users", tags=["User Management"])

@router.post("/register", response_model=UserRegistrationResponse)
async def register_user(
    user_data: UserRegistration,
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user account.
    
    Features demonstrated:
    - Comprehensive input validation
    - Password strength requirements
    - Email uniqueness checking
    - Business rule enforcement
    """
    return await user_service.register_user(user_data)

@router.post("/login")
async def login_user(
    email: str,
    password: str,
    user_service: UserService = Depends(get_user_service)
):
    """Basic authentication example."""
    user = await user_service.authenticate_user(email, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "role": user.role,
        "status": user.status
    }

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user profile by ID."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return UserResponse.from_orm(user)

# Additional endpoints for profile updates, addresses, etc...
```

**Router Concepts**:
- **Dependency Injection**: Services injected via FastAPI dependencies
- **Response Models**: Automatic serialization and documentation
- **Error Handling**: Consistent HTTP status codes
- **Path Operations**: RESTful endpoint design

## 🔗 Step 5: Application Integration

Update the main application to include the user system:

### Update `app/main.py`

```python
from fastapi import FastAPI
from .database import create_db_and_tables
from .routers import users

app = FastAPI(title="E-Commerce API with User Management")

# Include user router
app.include_router(users.router)

@app.on_event("startup")
async def startup():
    # Create database tables on startup
    create_db_and_tables()
    print("Database initialized with user tables")
```

## 🚀 Step 6: Testing Your User System

### Install Dependencies

```bash
cd ecommerce-app
pip install "pydantic[email]" "passlib[bcrypt]" sqlmodel
```

### Start the Application

```bash
python -m uvicorn app.main:app --reload
```

### Test Registration

Visit `http://localhost:8000/docs` and try the `/users/register` endpoint:

```json
{
  "email": "alice@example.com",
  "first_name": "Alice",
  "last_name": "Johnson", 
  "password": "SecurePass123",
  "confirm_password": "SecurePass123",
  "phone": "(555) 123-4567",
  "newsletter_subscribed": true,
  "marketing_emails": false,
  "terms_accepted": true
}
```

**Expected Response**:
```json
{
  "message": "Registration successful! Check your email for verification.",
  "user": {
    "id": 1,
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Johnson",
    "status": "pending"
  },
  "verification_required": true
}
```

### Test Validation Errors

Try invalid data to see Pydantic validation in action:

```json
{
  "email": "invalid-email",
  "first_name": "A",
  "password": "weak",
  "terms_accepted": false
}
```

## 🎓 What You've Accomplished

### **Production-Ready Architecture**
✅ **Separation of Concerns**: Models, schemas, services, and routers each have distinct roles  
✅ **Data Validation**: Comprehensive input validation and transformation  
✅ **Security Best Practices**: Password hashing, input sanitization  
✅ **Business Logic**: Centralized in service layer  
✅ **Error Handling**: Consistent and informative error responses  

### **Advanced Pydantic Features**
✅ **Custom Validators**: Password strength, age verification, phone formatting  
✅ **Cross-Field Validation**: Password confirmation matching  
✅ **Data Transformation**: Automatic name capitalization, email normalization  
✅ **Nested Models**: Address models within user system  
✅ **Response Models**: Secure API outputs excluding sensitive data  

### **Real-World Patterns**
✅ **Database Integration**: SQLModel for type-safe database operations  
✅ **Dependency Injection**: Clean service layer integration  
✅ **RESTful API Design**: Proper HTTP methods and status codes  
✅ **Documentation**: Auto-generated interactive API docs  

## 🔄 Next Steps

### **Immediate Improvements**
1. **Add JWT Authentication**: Replace basic login with token-based auth
2. **Email Verification**: Implement actual email sending and verification
3. **Password Reset**: Add forgot password functionality
4. **Profile Pictures**: Add file upload capabilities

### **Advanced Features**
1. **Role-Based Access Control**: Implement permissions system
2. **Account Management**: Deactivation, suspension, admin controls
3. **Address Validation**: Integration with address verification services
4. **Audit Logging**: Track user actions and changes

### **Testing & Quality**
1. **Unit Tests**: Test services and validation logic
2. **Integration Tests**: Test complete user workflows
3. **Load Testing**: Validate performance under load
4. **Security Testing**: Penetration testing and vulnerability scans

## 💡 Key Learning Takeaways

### **Pydantic Best Practices**
- **Type hints are essential** - they enable all validation magic
- **Separate input/output models** - different needs, different models
- **Custom validators for business rules** - not just technical validation
- **Response models control API contracts** - never expose sensitive data
- **Field constraints prevent bad data** - fail fast, fail clearly

### **Service Layer Benefits**
- **Business logic centralization** - one place for all rules
- **Database abstraction** - easier testing and maintenance
- **Error handling consistency** - uniform error responses
- **Reusability** - services can be used across multiple endpoints

### **Production Architecture**
- **Dependency injection** - clean, testable code structure
- **Separation of concerns** - each layer has a single responsibility
- **Security by design** - security considerations built in from the start
- **Validation at the edge** - catch problems early in the request cycle

---

**🎯 Congratulations!** You've built a production-ready user management system with comprehensive validation, security best practices, and clean architecture. This foundation will support all future e-commerce features.

**Ready for Chapter 3?** Continue building your e-commerce API with [Product Catalog Management](../03-database-integration/README.md)!