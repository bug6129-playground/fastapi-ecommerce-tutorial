"""
User API Endpoints
==================

FastAPI router for user-related endpoints including registration,
authentication, profile management, and address management.

Author: bug6129
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from pydantic import ValidationError

from ..schemas.user import (
    UserRegistration, UserResponse, UserRegistrationResponse,
    UserProfileUpdate, AddressCreate, AddressResponse,
    ValidationErrorResponse, ValidationErrorDetail
)
from ..services.user_service import UserService, get_user_service
from ..database import get_session

# Create router with prefix and tags
router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    responses={
        400: {"description": "Validation Error"},
        404: {"description": "User Not Found"},
        500: {"description": "Internal Server Error"}
    }
)

# =============================================================================
# USER REGISTRATION & AUTHENTICATION
# =============================================================================

@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="""
    Register a new user account with comprehensive validation.
    
    **Features:**
    - Email uniqueness validation
    - Password strength requirements
    - Phone number formatting
    - Age verification (13+ years)
    - Terms acceptance validation
    
    **Business Rules:**
    - Email must be unique across all users
    - Password must contain uppercase, lowercase, and digit
    - Phone numbers are automatically formatted
    - Users start with PENDING status until email verification
    """
)
async def register_user(
    user_data: UserRegistration,
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_session)
):
    """
    Register a new user account.
    
    This endpoint demonstrates:
    - Comprehensive input validation using Pydantic
    - Business logic separation in service layer
    - Proper error handling and responses
    - Password security best practices
    """
    try:
        result = await user_service.register_user(user_data)
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions (like email already exists)
        raise
    
    except ValidationError as e:
        # Handle Pydantic validation errors
        details = []
        for error in e.errors():
            details.append(ValidationErrorDetail(
                field=".".join(str(loc) for loc in error["loc"]),
                message=error["msg"],
                invalid_value=str(error.get("input", ""))
            ))
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ValidationErrorResponse(details=details).dict()
        )
    
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post(
    "/login",
    response_model=Dict[str, Any],
    summary="User Login",
    description="""
    Authenticate user with email and password.
    
    **Note:** This is a simplified login for educational purposes.
    In production, you would implement JWT tokens, OAuth, or similar.
    """
)
async def login_user(
    email: str,
    password: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Authenticate user credentials.
    
    This is a basic authentication example. In production:
    - Implement JWT tokens or sessions
    - Add rate limiting for login attempts
    - Log authentication events
    - Handle account lockouts
    """
    user = await user_service.authenticate_user(email, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}. Please contact support."
        )
    
    return {
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "status": user.status
    }

# =============================================================================
# USER PROFILE MANAGEMENT
# =============================================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get User Profile",
    description="""
    Retrieve user profile information by user ID.
    
    **Returns:**
    - Complete user profile (excluding sensitive data)
    - Account status and verification info
    - Preference settings
    """
)
async def get_user_profile(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get user profile by ID.
    
    This endpoint demonstrates:
    - Path parameter validation
    - Service layer integration
    - Response model filtering
    """
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse.from_orm(user)

@router.put(
    "/{user_id}/profile",
    response_model=UserResponse,
    summary="Update User Profile",
    description="""
    Update user profile information.
    
    **Features:**
    - Partial updates (only send fields you want to change)
    - Input validation and cleaning
    - Automatic timestamp updates
    
    **Validation:**
    - Names are capitalized automatically
    - Phone numbers are formatted
    - All business rules are enforced
    """
)
async def update_user_profile(
    user_id: int,
    update_data: UserProfileUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update user profile information.
    
    This endpoint demonstrates:
    - Partial model updates
    - Business rule validation
    - Data transformation
    """
    try:
        updated_user = await user_service.update_user_profile(user_id, update_data)
        return updated_user
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {str(e)}"
        )

@router.post(
    "/{user_id}/verify-email",
    response_model=UserResponse,
    summary="Verify Email Address",
    description="""
    Verify user's email address using verification token.
    
    **Process:**
    1. User receives verification email with token
    2. User clicks link or enters token
    3. Account status changes from PENDING to ACTIVE
    """
)
async def verify_email(
    user_id: int,
    verification_token: str,
    user_service: UserService = Depends(get_user_service)
):
    """
    Verify user's email address.
    
    In production, this would:
    - Validate the token against stored value
    - Check token expiration
    - Log verification events
    """
    try:
        verified_user = await user_service.verify_email(user_id, verification_token)
        return verified_user
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email verification failed: {str(e)}"
        )

@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    summary="Deactivate User Account",
    description="""
    Deactivate a user account (soft delete).
    
    **Note:** This changes status to SUSPENDED rather than deleting data.
    In production, implement proper data retention policies.
    """
)
async def deactivate_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Deactivate user account.
    
    This demonstrates soft deletion - preserving data while
    preventing account usage.
    """
    try:
        deactivated_user = await user_service.deactivate_user(user_id)
        return deactivated_user
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deactivation failed: {str(e)}"
        )

# =============================================================================
# ADDRESS MANAGEMENT
# =============================================================================

@router.post(
    "/{user_id}/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add User Address",
    description="""
    Add a new shipping/billing address for a user.
    
    **Features:**
    - Postal code validation by country
    - Default address management
    - Address formatting
    """
)
async def add_user_address(
    user_id: int,
    address_data: AddressCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Add a new address for a user.
    
    This endpoint demonstrates:
    - Nested data validation
    - Business rule enforcement (default addresses)
    - Geographic data handling
    """
    try:
        new_address = await user_service.add_user_address(user_id, address_data)
        return new_address
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Address creation failed: {str(e)}"
        )

@router.get(
    "/{user_id}/addresses",
    response_model=List[AddressResponse],
    summary="Get User Addresses",
    description="""
    Retrieve all addresses for a user.
    
    **Returns:**
    - List of user addresses
    - Default address marked
    - Formatted address strings
    """
)
async def get_user_addresses(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get all addresses for a user.
    
    This demonstrates:
    - List response models
    - Related data retrieval
    - Computed properties in responses
    """
    try:
        addresses = await user_service.get_user_addresses(user_id)
        return addresses
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve addresses: {str(e)}"
        )

# =============================================================================
# USER STATISTICS & ANALYTICS
# =============================================================================

@router.get(
    "/{user_id}/stats",
    response_model=Dict[str, Any],
    summary="Get User Statistics",
    description="""
    Get user account statistics and metrics.
    
    **Includes:**
    - Account age and activity
    - Profile completion percentage
    - Address count
    - Verification status
    """
)
async def get_user_stats(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """
    Get user statistics and metrics.
    
    This demonstrates:
    - Complex data aggregation
    - Computed metrics
    - Analytics endpoints
    """
    try:
        stats = await user_service.get_user_stats(user_id)
        return stats
    
    except HTTPException:
        raise
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user stats: {str(e)}"
        )

# =============================================================================
# EXAMPLE & TESTING ENDPOINTS
# =============================================================================

@router.get(
    "/examples/registration-data",
    summary="Get Example Registration Data",
    description="Get example data for testing user registration",
    tags=["Examples"]
)
async def get_example_registration_data():
    """
    Provide example registration data for testing.
    
    This helps developers understand the expected data format
    and test the API endpoints.
    """
    return {
        "valid_example": {
            "email": "alice.developer@example.com",
            "first_name": "Alice",
            "last_name": "Developer",
            "password": "SecurePass123",
            "confirm_password": "SecurePass123",
            "phone": "555-123-4567",
            "newsletter_subscribed": True,
            "marketing_emails": False,
            "terms_accepted": True
        },
        "invalid_examples": {
            "weak_password": {
                "password": "weak",
                "issue": "Password too short and missing requirements"
            },
            "invalid_email": {
                "email": "not-an-email",
                "issue": "Invalid email format"
            },
            "terms_not_accepted": {
                "terms_accepted": False,
                "issue": "Terms must be accepted"
            }
        },
        "validation_tips": [
            "Password must contain uppercase, lowercase, and digit",
            "Phone numbers are automatically formatted",
            "Names are automatically capitalized",
            "Email addresses are normalized to lowercase"
        ]
    }

@router.get(
    "/examples/address-data", 
    summary="Get Example Address Data",
    description="Get example data for testing address creation",
    tags=["Examples"]
)
async def get_example_address_data():
    """
    Provide example address data for testing.
    """
    return {
        "valid_example": {
            "street_address": "123 Main Street",
            "apartment": "Apt 4B",
            "city": "Springfield",
            "state_province": "Illinois",
            "postal_code": "62701",
            "country": "USA",
            "is_default": True
        },
        "validation_rules": {
            "postal_code": "Must be in format 12345 or 12345-6789 for USA",
            "is_default": "Only one address can be default per user",
            "street_address": "Minimum 5 characters required"
        }
    }