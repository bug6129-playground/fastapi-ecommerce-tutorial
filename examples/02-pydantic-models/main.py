"""
Pydantic Fundamentals - Complete Examples
========================================

This example demonstrates core Pydantic concepts for FastAPI development:
- Basic model creation and validation
- Custom validators and error handling
- Request/Response patterns
- Advanced validation techniques

Run this file to see all examples in action and test the interactive API.

Author: bug6129
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, EmailStr
from fastapi import FastAPI, HTTPException, status

# Create FastAPI app for interactive testing
app = FastAPI(
    title="Pydantic Fundamentals Tutorial",
    description="Learn Pydantic data validation through interactive examples",
    version="1.0.0"
)

# =============================================================================
# 1. BASIC MODELS - The Foundation of FastAPI Data Handling
# =============================================================================

class UserProfile(BaseModel):
    """
    Basic user profile model demonstrating fundamental Pydantic concepts.
    
    Key Concepts:
    - Type hints for automatic validation
    - Optional fields with defaults
    - Field descriptions for auto-generated docs
    """
    name: str = Field(..., description="Full name of the user", min_length=2)
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., description="User age", ge=13, le=120)
    is_active: bool = Field(default=True, description="Whether user account is active")
    bio: Optional[str] = Field(None, description="Optional user biography", max_length=500)
    
    class Config:
        """Pydantic configuration for this model."""
        # Generate example data for API documentation
        schema_extra = {
            "example": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "age": 25,
                "is_active": True,
                "bio": "Software developer who loves FastAPI and Python"
            }
        }

# =============================================================================
# 2. VALIDATION & CUSTOM VALIDATORS - Ensuring Data Quality
# =============================================================================

class ProductStatus(str, Enum):
    """Enum for product status - provides type safety and validation."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class Product(BaseModel):
    """
    Product model demonstrating advanced validation techniques.
    
    Advanced Concepts:
    - Custom validators
    - Enum fields for controlled values
    - Cross-field validation
    - Data transformation
    """
    name: str = Field(..., description="Product name", min_length=3, max_length=100)
    price: float = Field(..., description="Product price in USD", gt=0)
    category: str = Field(..., description="Product category")
    status: ProductStatus = Field(default=ProductStatus.ACTIVE, description="Product status")
    tags: List[str] = Field(default=[], description="Product tags for search")
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        """Custom validator: Product names should be clean."""
        if any(char in v for char in ['<', '>', '{', '}', '[', ']']):
            raise ValueError('Product name cannot contain special characters')
        return v.title()  # Capitalize each word
    
    @validator('category')
    def category_must_be_valid(cls, v):
        """Custom validator: Only allow specific categories."""
        allowed_categories = ['electronics', 'clothing', 'books', 'home', 'sports']
        if v.lower() not in allowed_categories:
            raise ValueError(f'Category must be one of: {", ".join(allowed_categories)}')
        return v.lower()
    
    @validator('tags')
    def clean_tags(cls, v):
        """Custom validator: Clean and deduplicate tags."""
        # Remove empty strings, convert to lowercase, remove duplicates
        return list(set(tag.lower().strip() for tag in v if tag.strip()))
    
    @validator('price')
    def round_price(cls, v):
        """Custom validator: Round price to 2 decimal places."""
        return round(v, 2)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "wireless bluetooth headphones",
                "price": 99.99,
                "category": "electronics",
                "status": "active",
                "tags": ["bluetooth", "wireless", "audio", "headphones"],
                "description": "High-quality wireless headphones with noise cancellation"
            }
        }

# =============================================================================
# 3. NESTED MODELS & RELATIONSHIPS - Complex Data Structures
# =============================================================================

class Address(BaseModel):
    """Address model for demonstrating nested structures."""
    street: str = Field(..., description="Street address", max_length=200)
    city: str = Field(..., description="City name", max_length=100)
    state: str = Field(..., description="State or province", max_length=100)
    postal_code: str = Field(..., description="Postal/ZIP code", max_length=20)
    country: str = Field(default="USA", description="Country name")
    
    @validator('postal_code')
    def validate_postal_code(cls, v):
        """Simple postal code validation (US format)."""
        import re
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid postal code format (use XXXXX or XXXXX-XXXX)')
        return v

class OrderItem(BaseModel):
    """Individual item in an order."""
    product_name: str = Field(..., description="Name of the ordered product")
    quantity: int = Field(..., description="Quantity ordered", ge=1)
    unit_price: float = Field(..., description="Price per unit", gt=0)
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this item."""
        return round(self.quantity * self.unit_price, 2)

class Order(BaseModel):
    """
    Complex order model demonstrating nested relationships.
    
    Advanced Concepts:
    - Nested models (Address, OrderItem)
    - Lists of models
    - Computed properties
    - Root validators for cross-field validation
    """
    order_id: str = Field(..., description="Unique order identifier")
    customer_email: EmailStr = Field(..., description="Customer email address")
    items: List[OrderItem] = Field(..., description="List of ordered items", min_items=1)
    shipping_address: Address = Field(..., description="Shipping address")
    order_date: datetime = Field(default_factory=datetime.now, description="Order timestamp")
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('order_id')
    def validate_order_id(cls, v):
        """Validate order ID format."""
        import re
        if not re.match(r'^ORD-\d{8}$', v):
            raise ValueError('Order ID must be in format: ORD-XXXXXXXX')
        return v
    
    @validator('items')
    def validate_items_not_empty(cls, v):
        """Ensure order has at least one item."""
        if not v:
            raise ValueError('Order must contain at least one item')
        return v
    
    @property
    def total_amount(self) -> float:
        """Calculate total order amount."""
        return round(sum(item.total_price for item in self.items), 2)
    
    @property
    def item_count(self) -> int:
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items)
    
    class Config:
        schema_extra = {
            "example": {
                "order_id": "ORD-12345678",
                "customer_email": "customer@example.com",
                "items": [
                    {
                        "product_name": "Wireless Headphones",
                        "quantity": 1,
                        "unit_price": 99.99
                    },
                    {
                        "product_name": "Phone Case",
                        "quantity": 2,
                        "unit_price": 19.99
                    }
                ],
                "shipping_address": {
                    "street": "123 Main Street",
                    "city": "Anytown",
                    "state": "CA",
                    "postal_code": "12345",
                    "country": "USA"
                },
                "notes": "Please handle with care"
            }
        }

# =============================================================================
# 4. RESPONSE MODELS - Structuring API Outputs
# =============================================================================

class UserResponse(BaseModel):
    """Response model for user data (excludes sensitive information)."""
    name: str
    email: str
    age: int
    is_active: bool
    bio: Optional[str]
    member_since: datetime = Field(default_factory=datetime.now)

class ProductResponse(BaseModel):
    """Response model for product data with computed fields."""
    name: str
    price: float
    category: str
    status: ProductStatus
    tags: List[str]
    description: Optional[str]
    is_available: bool = True
    
    @validator('is_available', pre=True, always=True)
    def compute_availability(cls, v, values):
        """Compute availability based on status."""
        status = values.get('status')
        return status in [ProductStatus.ACTIVE]

class OrderResponse(BaseModel):
    """Response model for order data with computed totals."""
    order_id: str
    customer_email: str
    items: List[OrderItem]
    shipping_address: Address
    order_date: datetime
    total_amount: float
    item_count: int
    notes: Optional[str]

# =============================================================================
# 5. API ENDPOINTS - Putting It All Together
# =============================================================================

@app.get("/", tags=["Demo"])
async def root():
    """API root with information about available endpoints."""
    return {
        "message": "Pydantic Fundamentals Tutorial API",
        "available_endpoints": {
            "users": "/users/ (POST, GET)",
            "products": "/products/ (POST, GET)",
            "orders": "/orders/ (POST, GET)",
            "examples": "/examples/ (GET)",
        },
        "documentation": "/docs"
    }

# User endpoints demonstrating basic validation
@app.post("/users/", response_model=UserResponse, tags=["Users"])
async def create_user(user: UserProfile):
    """
    Create a new user profile.
    
    This endpoint demonstrates:
    - Request body validation with Pydantic
    - Automatic error responses for invalid data
    - Response model that excludes sensitive fields
    """
    # In a real app, you'd save to database here
    response_data = user.dict()
    response_data['member_since'] = datetime.now()
    return UserResponse(**response_data)

@app.get("/users/example", response_model=UserResponse, tags=["Users"])
async def get_example_user():
    """Get an example user for testing purposes."""
    example_user = UserProfile(
        name="John Doe",
        email="john@example.com",
        age=30,
        bio="Example user for demonstration purposes"
    )
    response_data = example_user.dict()
    response_data['member_since'] = datetime.now()
    return UserResponse(**response_data)

# Product endpoints demonstrating advanced validation
@app.post("/products/", response_model=ProductResponse, tags=["Products"])
async def create_product(product: Product):
    """
    Create a new product.
    
    This endpoint demonstrates:
    - Custom validators in action
    - Enum validation
    - List field validation
    - Data transformation during validation
    """
    # The custom validators will automatically clean and validate the data
    response_data = product.dict()
    return ProductResponse(**response_data)

@app.get("/products/example", response_model=ProductResponse, tags=["Products"])
async def get_example_product():
    """Get an example product for testing purposes."""
    example_product = Product(
        name="amazing wireless headphones",
        price=149.99,
        category="ELECTRONICS",  # Will be converted to lowercase
        tags=["bluetooth", "WIRELESS", " audio ", "bluetooth"],  # Will be cleaned
        description="High-quality headphones with excellent sound"
    )
    return ProductResponse(**example_product.dict())

# Order endpoints demonstrating nested models
@app.post("/orders/", response_model=OrderResponse, tags=["Orders"])
async def create_order(order: Order):
    """
    Create a new order.
    
    This endpoint demonstrates:
    - Nested model validation
    - List validation
    - Custom validators for complex fields
    - Computed properties in response
    """
    response_data = order.dict()
    response_data['total_amount'] = order.total_amount
    response_data['item_count'] = order.item_count
    return OrderResponse(**response_data)

@app.get("/orders/example", response_model=OrderResponse, tags=["Orders"])
async def get_example_order():
    """Get an example order for testing purposes."""
    example_order = Order(
        order_id="ORD-87654321",
        customer_email="customer@test.com",
        items=[
            OrderItem(product_name="Laptop", quantity=1, unit_price=999.99),
            OrderItem(product_name="Mouse", quantity=2, unit_price=25.50)
        ],
        shipping_address=Address(
            street="456 Oak Avenue",
            city="Springfield",
            state="IL",
            postal_code="62701"
        ),
        notes="Rush delivery requested"
    )
    
    response_data = example_order.dict()
    response_data['total_amount'] = example_order.total_amount
    response_data['item_count'] = example_order.item_count
    return OrderResponse(**response_data)

# Educational endpoints
@app.get("/examples/validation-errors", tags=["Examples"])
async def validation_error_examples():
    """
    Examples of common validation errors and how to avoid them.
    
    This endpoint provides educational content about Pydantic validation.
    """
    return {
        "validation_examples": {
            "user_errors": {
                "invalid_email": "Use valid email format: user@example.com",
                "age_too_young": "Age must be at least 13",
                "age_too_old": "Age must be at most 120",
                "name_too_short": "Name must be at least 2 characters"
            },
            "product_errors": {
                "invalid_price": "Price must be greater than 0",
                "invalid_category": "Category must be one of: electronics, clothing, books, home, sports",
                "special_chars_in_name": "Product name cannot contain < > { } [ ]"
            },
            "order_errors": {
                "invalid_order_id": "Order ID must be in format: ORD-XXXXXXXX",
                "invalid_postal_code": "Use format: 12345 or 12345-6789",
                "empty_items": "Order must contain at least one item"
            }
        },
        "tips": [
            "Always use type hints - they enable Pydantic validation",
            "Use Field() for additional validation constraints",
            "Custom validators run after basic type validation",
            "Pydantic automatically converts compatible types",
            "Use response models to control API output"
        ]
    }

@app.get("/examples/model-features", tags=["Examples"])
async def model_features_examples():
    """
    Examples of advanced Pydantic model features.
    """
    return {
        "pydantic_features": {
            "field_validation": {
                "min_length": "Field(min_length=3) - minimum string length",
                "max_length": "Field(max_length=100) - maximum string length", 
                "ge": "Field(ge=0) - greater than or equal to",
                "gt": "Field(gt=0) - greater than",
                "le": "Field(le=100) - less than or equal to",
                "lt": "Field(lt=100) - less than"
            },
            "custom_validators": {
                "pre": "@validator('field', pre=True) - runs before type validation",
                "always": "@validator('field', always=True) - always runs even if field not provided",
                "each_item": "@validator('list_field', each_item=True) - validates each item in list"
            },
            "model_config": {
                "schema_extra": "Add example data for API docs",
                "allow_population_by_field_name": "Allow using field names or aliases",
                "validate_assignment": "Re-validate when fields are changed after creation"
            }
        }
    }

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Pydantic Fundamentals Tutorial",
        "timestamp": datetime.now()
    }

# Main execution
if __name__ == "__main__":
    import uvicorn
    print("🚀 Pydantic Fundamentals Tutorial")
    print("=" * 40)
    print("This tutorial demonstrates Pydantic concepts through interactive examples.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Examples: http://localhost:8000/examples/validation-errors")
    print("")
    print("📚 What you'll learn:")
    print("   • Basic model creation and validation")
    print("   • Custom validators and error handling")
    print("   • Nested models and relationships")
    print("   • Request/Response patterns")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 40)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)