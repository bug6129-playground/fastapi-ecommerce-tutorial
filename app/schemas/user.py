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
        regex=r'^\\+?[\\d\\s\\-\\(\\)]+$'
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
    phone: Optional[str] = Field(None, regex=r'^\\+?[\\d\\s\\-\\(\\)]+$')
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
            if not re.match(r'^\\d{5}(-\\d{4})?$', v):
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