# Tutorial A2: Pydantic Fundamentals

**Master data validation and modeling with Pydantic** 📝

Pydantic is the backbone of FastAPI's automatic data validation, serialization, and documentation generation. In this tutorial, you'll learn to create robust data models that ensure your API handles data correctly and provides excellent developer experience.

## 🎯 Learning Objectives

By the end of this tutorial, you'll be able to:
- ✅ Create Pydantic models with proper type hints and validation
- ✅ Use built-in field validators and constraints effectively
- ✅ Write custom validators for complex business logic
- ✅ Handle nested models and complex data relationships
- ✅ Design proper request/response model patterns
- ✅ Debug and handle validation errors gracefully

## 🧠 Why Pydantic Matters for FastAPI

### **The FastAPI Magic**
```python
@app.post("/users/")
async def create_user(user: UserModel):  # ← Pydantic model
    return user  # FastAPI handles everything!
```

**What FastAPI does automatically**:
- 🔍 **Validates** incoming JSON against your model
- 📚 **Generates documentation** from your model
- ❌ **Returns helpful errors** for invalid data
- 🔄 **Serializes** responses to JSON
- 🎯 **Provides type hints** for your IDE

### **Without Pydantic vs With Pydantic**

**❌ Without Pydantic** (manual validation):
```python
@app.post("/users/")
async def create_user(request: Request):
    data = await request.json()
    
    # Manual validation (error-prone!)
    if "email" not in data:
        raise HTTPException(400, "Missing email")
    if "@" not in data["email"]:
        raise HTTPException(400, "Invalid email")
    if data.get("age", 0) < 13:
        raise HTTPException(400, "Age must be at least 13")
    
    # Hope we didn't miss anything...
    return data
```

**✅ With Pydantic** (automatic validation):
```python
class User(BaseModel):
    email: EmailStr
    age: int = Field(..., ge=13)

@app.post("/users/")
async def create_user(user: User):
    return user  # Done! All validation handled automatically
```

## 🏗️ Pydantic Fundamentals

### **1. Basic Model Creation**

```python
from pydantic import BaseModel, Field
from typing import Optional

class UserProfile(BaseModel):
    """Basic user profile demonstrating core Pydantic concepts."""
    
    # Required field with type validation
    name: str
    
    # Field with validation constraints
    age: int = Field(..., ge=13, le=120, description="User age")
    
    # Optional field with default
    bio: Optional[str] = None
    
    # Field with default value
    is_active: bool = True
```

**Key Concepts**:
- **Type hints** enable automatic validation
- **Field()** adds constraints and metadata
- **Optional** fields can be None or omitted
- **Default values** provide fallbacks

### **2. Field Validation & Constraints**

```python
from pydantic import EmailStr, HttpUrl

class Product(BaseModel):
    # String constraints
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=1000)
    
    # Numeric constraints  
    price: float = Field(..., gt=0, description="Price in USD")
    discount: float = Field(0, ge=0, le=1, description="Discount as decimal")
    
    # Special types
    contact_email: EmailStr  # Validates email format
    website: HttpUrl         # Validates URL format
    
    # Enum for controlled values
    from enum import Enum
    class Category(str, Enum):
        ELECTRONICS = "electronics"
        CLOTHING = "clothing"
        BOOKS = "books"
    
    category: Category
```

**Available Constraints**:
- **String**: `min_length`, `max_length`, `regex`
- **Numeric**: `gt`, `ge`, `lt`, `le` (greater/less than/equal)
- **List**: `min_items`, `max_items`
- **All Fields**: `description`, `example`, `title`

### **3. Custom Validators**

```python
from pydantic import validator
import re

class User(BaseModel):
    username: str
    email: str
    phone: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Username must be alphanumeric."""
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()  # Transform to lowercase
    
    @validator('email')
    def email_must_be_valid(cls, v):
        """Custom email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('phone')
    def phone_format(cls, v):
        """Format phone number."""
        if v is None:
            return v
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', v)
        
        # Validate US phone number format
        if len(digits) != 10:
            raise ValueError('Phone must be 10 digits')
        
        # Format as (XXX) XXX-XXXX
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
```

**Validator Features**:
- **Transform data** during validation
- **Access to other fields** via `values` parameter
- **Run before or after** type validation
- **Chain multiple validators** for same field

### **4. Nested Models & Relationships**

```python
from typing import List
from datetime import datetime

class Address(BaseModel):
    """Address model for nested usage."""
    street: str
    city: str
    state: str = Field(..., min_length=2, max_length=2)
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')

class OrderItem(BaseModel):
    """Individual item in an order."""
    product_name: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    
    # Computed property
    @property
    def total_price(self) -> float:
        return round(self.quantity * self.unit_price, 2)

class Order(BaseModel):
    """Complex order with nested models."""
    order_id: str
    customer_email: EmailStr
    
    # Nested single model
    shipping_address: Address
    
    # List of nested models
    items: List[OrderItem] = Field(..., min_items=1)
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Root validator for cross-field validation
    @validator('order_id')
    def validate_order_id(cls, v):
        if not v.startswith('ORD-'):
            raise ValueError('Order ID must start with ORD-')
        return v
    
    # Computed properties
    @property
    def total_amount(self) -> float:
        return sum(item.total_price for item in self.items)
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
```

### **5. Request/Response Model Patterns**

```python
# Input Models (What API accepts)
class UserCreate(BaseModel):
    """Model for user creation requests."""
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str

class UserUpdate(BaseModel):
    """Model for user update requests (all optional)."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None

# Output Models (What API returns)
class UserResponse(BaseModel):
    """Model for user responses (no sensitive data)."""
    id: int
    username: str
    email: str
    full_name: str
    bio: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        # Allow reading from ORM models
        orm_mode = True

# Using in FastAPI endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    # user.password is available here but won't be in response
    hashed_password = hash_password(user.password)
    # ... save to database ...
    return UserResponse(**user_data)
```

**Key Patterns**:
- **Separate input/output models** for security and clarity
- **Optional fields** for updates
- **Computed fields** in responses
- **No sensitive data** in response models

## 🧪 Practical Examples

Let's work through complete examples you can run and test:

### **Example 1: Simple Blog Post**

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class BlogPost(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=50)
    author: str
    tags: List[str] = []
    published: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('title')
    def title_must_be_capitalized(cls, v):
        return v.title()
    
    @validator('tags')
    def clean_tags(cls, v):
        # Remove empty tags and duplicates
        return list(set(tag.strip().lower() for tag in v if tag.strip()))

# Test the model
post = BlogPost(
    title="learning fastapi with pydantic",
    content="This is a comprehensive guide to using Pydantic with FastAPI...",
    author="Developer",
    tags=["fastapi", "pydantic", "", "python", "FastAPI"]  # Note duplicates and empty
)

print(post.title)  # "Learning Fastapi With Pydantic"
print(post.tags)   # ["fastapi", "pydantic", "python"] - cleaned!
```

### **Example 2: E-commerce Product**

```python
from enum import Enum
from decimal import Decimal

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive" 
    OUT_OF_STOCK = "out_of_stock"

class Product(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    sku: str = Field(..., regex=r'^[A-Z]{3}-\d{4}$')
    price: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    status: ProductStatus = ProductStatus.ACTIVE
    categories: List[str] = Field(default=[], max_items=5)
    
    @validator('name')
    def clean_product_name(cls, v):
        # Remove extra spaces and capitalize
        return ' '.join(word.capitalize() for word in v.split())
    
    @validator('categories')
    def validate_categories(cls, v):
        allowed = ['electronics', 'clothing', 'books', 'home', 'sports']
        for category in v:
            if category.lower() not in allowed:
                raise ValueError(f'Invalid category: {category}')
        return [c.lower() for c in v]

# Test the model
product = Product(
    name="wireless   bluetooth  headphones",
    sku="ELE-1234",
    price="99.99",
    categories=["Electronics", "AUDIO"]
)

print(product.name)  # "Wireless Bluetooth Headphones"
print(product.categories)  # ["electronics", "audio"]
```

## 🔧 Hands-On Exercises

### **Exercise 1: User Registration Model**

Create a user registration model with these requirements:
- Username: 3-20 characters, alphanumeric only
- Email: Valid email format
- Password: At least 8 characters, must contain uppercase, lowercase, and digit
- Age: 13-120
- Terms accepted: Must be True

```python
# Your solution here
class UserRegistration(BaseModel):
    # Add your fields and validators
    pass

# Test with valid data
user = UserRegistration(
    username="johndoe123",
    email="john@example.com", 
    password="SecurePass1",
    age=25,
    terms_accepted=True
)
```

### **Exercise 2: Order Processing Model**

Create models for an order system:
- Customer info (name, email, phone)
- Multiple items (name, price, quantity)
- Shipping address
- Order total calculation

```python
# Your solution here - create Customer, Item, Address, and Order models
```

### **Exercise 3: API Response Model**

Create a response model that:
- Excludes sensitive fields from input model
- Adds computed fields (like full_name from first_name + last_name)
- Includes metadata (created_at, updated_at)

## 🚨 Common Pitfalls & Solutions

### **❌ Pitfall 1: Missing Type Hints**
```python
class User(BaseModel):
    name = "default"  # No validation happens!
```

**✅ Solution**: Always use type hints
```python
class User(BaseModel):
    name: str = "default"  # Now validates as string
```

### **❌ Pitfall 2: Mutable Defaults**
```python
class User(BaseModel):
    tags: List[str] = []  # Dangerous! Shared between instances
```

**✅ Solution**: Use Field with default_factory
```python
class User(BaseModel):
    tags: List[str] = Field(default_factory=list)
```

### **❌ Pitfall 3: Not Handling None Values**
```python
@validator('email')
def validate_email(cls, v):
    return v.lower()  # Crashes if v is None!
```

**✅ Solution**: Check for None first
```python
@validator('email')
def validate_email(cls, v):
    if v is None:
        return v
    return v.lower()
```

### **❌ Pitfall 4: Validator Order Issues**
```python
# Wrong order - type validation might fail before custom validator
@validator('price', pre=True)
def convert_price(cls, v):
    return float(v) if isinstance(v, str) else v
```

**✅ Solution**: Use pre=True for data conversion
```python
@validator('price', pre=True)  # Runs before type validation
def convert_price(cls, v):
    if isinstance(v, str):
        return float(v)
    return v
```

## 🎓 Advanced Tips

### **1. Model Configuration**
```python
class User(BaseModel):
    name: str
    email: str
    
    class Config:
        # Validate assignment after model creation
        validate_assignment = True
        
        # Use enum values in schema
        use_enum_values = True
        
        # Allow population by field name or alias
        allow_population_by_field_name = True
        
        # Example for documentation
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
```

### **2. Field Aliases**
```python
class User(BaseModel):
    user_name: str = Field(..., alias="username")
    email_address: str = Field(..., alias="email")
    
    class Config:
        allow_population_by_field_name = True

# Can use either field name or alias
user = User(username="john", email="john@example.com")  # Using aliases
user = User(user_name="john", email_address="john@example.com")  # Using field names
```

### **3. Dynamic Models**
```python
from pydantic import create_model

# Create models programmatically
DynamicUser = create_model(
    'DynamicUser',
    name=(str, ...),
    age=(int, Field(ge=0, le=120))
)
```

## 🔄 What's Next?

### **Ready to Apply These Concepts?**

Now that you understand Pydantic fundamentals, choose your learning path:

**🎯 Path A - Continue with Examples:**
Practice these concepts with hands-on code examples:

1. **[Example 02: Pydantic Models](../../examples/02-pydantic-models/)** - Complete the Pydantic tutorial with working code
2. **[Example 03: CRUD Operations](../../examples/03-crud-basics/)** - Use models in API endpoints
3. **[Example 04: Database Integration](../../examples/04-database-simple/)** - Connect models to databases

**🏗️ Path B - Build Real Project:**
Apply these concepts in a production e-commerce system:

1. **[Tutorial B2: User Management System](apply-user-system.md)** - See how these concepts work in a real API

**🧪 Practice More:**
Try the exercises above and create your own models with custom validation.

### **Key Takeaways**:
- **Type hints are essential** - they enable all of Pydantic's magic
- **Start simple** - basic validation covers 80% of use cases
- **Custom validators** for business logic and data cleaning
- **Separate models** for input/output to maintain clean API contracts
- **Test your models** - invalid data should be caught early

---

**🎯 Ready to practice with working code? Continue with [Example 02: Pydantic Models](../../examples/02-pydantic-models/)!**

*Remember: Pydantic is powerful but intuitive. Start with basic models and add complexity as needed. The automatic validation and documentation make it worth the learning investment!*