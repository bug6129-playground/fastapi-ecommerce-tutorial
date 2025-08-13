"""
User Service Layer
==================

Business logic for user management operations.
This service handles user registration, authentication, profile management,
and all business rules related to users.

Author: bug6129
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from ..models.user import User, UserCreate, UserUpdate, Address, UserRole, UserStatus
from ..schemas.user import (
    UserRegistration, UserResponse, UserRegistrationResponse, 
    AddressCreate, AddressResponse, UserProfileUpdate
)
from ..utils.security import hash_password, verify_password, generate_verification_token, sanitize_email
from fastapi import HTTPException, status

class UserService:
    """
    Service class for user-related business operations.
    
    This class encapsulates all user management logic including:
    - User registration and validation
    - Email verification
    - Profile management
    - Address management
    - Business rule enforcement
    """
    
    def __init__(self, db: Session):
        """
        Initialize the user service with a database session.
        
        Args:
            db: SQLModel database session
        """
        self.db = db
    
    async def register_user(self, user_data: UserRegistration) -> UserRegistrationResponse:
        """
        Register a new user with comprehensive validation.
        
        Args:
            user_data: User registration data from the API
            
        Returns:
            UserRegistrationResponse with user data and verification info
            
        Raises:
            HTTPException: If email already exists or validation fails
        """
        # Check if email already exists
        existing_user = await self.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
            )
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Create user model for database
        db_user = User(
            email=sanitize_email(user_data.email),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=hashed_password,
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            newsletter_subscribed=user_data.newsletter_subscribed,
            marketing_emails=user_data.marketing_emails,
            role=UserRole.CUSTOMER,
            status=UserStatus.PENDING,  # Require email verification
            is_email_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Create response
        user_response = UserResponse.from_orm(db_user)
        
        return UserRegistrationResponse(
            message="Registration successful! Please check your email to verify your account.",
            user=user_response,
            verification_required=True
        )
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User object if found, None otherwise
        """
        email = sanitize_email(email)
        statement = select(User).where(User.email == email)
        result = self.db.exec(statement)
        return result.first()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User object if found, None otherwise
        """
        statement = select(User).where(User.id == user_id)
        result = self.db.exec(statement)
        return result.first()
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login time
        user.last_login_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        
        return user
    
    async def update_user_profile(self, user_id: int, update_data: UserProfileUpdate) -> UserResponse:
        """
        Update user profile information.
        
        Args:
            user_id: ID of user to update
            update_data: Profile update data
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    async def verify_email(self, user_id: int, verification_token: str) -> UserResponse:
        """
        Verify user's email address.
        
        Args:
            user_id: User ID
            verification_token: Email verification token
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found or token invalid
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # In a real app, you'd validate the token here
        # For this tutorial, we'll just mark as verified
        user.is_email_verified = True
        user.status = UserStatus.ACTIVE
        user.updated_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    async def deactivate_user(self, user_id: int) -> UserResponse:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            Updated user response
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.status = UserStatus.SUSPENDED
        user.updated_at = datetime.utcnow()
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    async def add_user_address(self, user_id: int, address_data: AddressCreate) -> AddressResponse:
        """
        Add a new address for a user.
        
        Args:
            user_id: User ID
            address_data: Address creation data
            
        Returns:
            Created address response
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # If this is set as default, unset other default addresses
        if address_data.is_default:
            await self._unset_default_addresses(user_id)
        
        # Create address
        db_address = Address(
            user_id=user_id,
            street_address=address_data.street_address,
            apartment=address_data.apartment,
            city=address_data.city,
            state_province=address_data.state_province,
            postal_code=address_data.postal_code,
            country=address_data.country,
            is_default=address_data.is_default,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(db_address)
        self.db.commit()
        self.db.refresh(db_address)
        
        return AddressResponse.from_orm(db_address)
    
    async def get_user_addresses(self, user_id: int) -> List[AddressResponse]:
        """
        Get all addresses for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user addresses
        """
        statement = select(Address).where(Address.user_id == user_id)
        result = self.db.exec(statement)
        addresses = result.all()
        
        return [AddressResponse.from_orm(addr) for addr in addresses]
    
    async def _unset_default_addresses(self, user_id: int) -> None:
        """
        Internal method to unset all default addresses for a user.
        
        Args:
            user_id: User ID
        """
        statement = select(Address).where(
            Address.user_id == user_id,
            Address.is_default == True
        )
        result = self.db.exec(statement)
        addresses = result.all()
        
        for address in addresses:
            address.is_default = False
            address.updated_at = datetime.utcnow()
            self.db.add(address)
        
        self.db.commit()
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics and metrics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
            
        Raises:
            HTTPException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get address count
        address_count = len(await self.get_user_addresses(user_id))
        
        # Calculate account age
        account_age_days = (datetime.utcnow() - user.created_at).days
        
        return {
            "user_id": user_id,
            "account_age_days": account_age_days,
            "email_verified": user.is_email_verified,
            "status": user.status,
            "role": user.role,
            "address_count": address_count,
            "newsletter_subscribed": user.newsletter_subscribed,
            "marketing_emails": user.marketing_emails,
            "last_login": user.last_login_at,
            "profile_completion": self._calculate_profile_completion(user)
        }
    
    def _calculate_profile_completion(self, user: User) -> int:
        """
        Calculate profile completion percentage.
        
        Args:
            user: User object
            
        Returns:
            Profile completion percentage (0-100)
        """
        total_fields = 7  # Basic profile fields
        completed_fields = 2  # email and name are always present
        
        if user.phone:
            completed_fields += 1
        if user.date_of_birth:
            completed_fields += 1
        if user.is_email_verified:
            completed_fields += 1
        # Could add more fields like bio, avatar, etc.
        
        return int((completed_fields / total_fields) * 100)

# Factory function for dependency injection
def get_user_service(db: Session) -> UserService:
    """
    Factory function to create UserService instance.
    
    Args:
        db: Database session
        
    Returns:
        UserService instance
    """
    return UserService(db)