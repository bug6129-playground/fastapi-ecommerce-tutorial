# Pydantic Fundamentals

**Master data validation and modeling with Pydantic** 📝

This example teaches you essential Pydantic skills for creating robust, validated data models in FastAPI. Learn through hands-on examples that progress from simple to advanced validation concepts.

## 🎯 What You'll Learn

- **Basic Models**: Creating Pydantic models with type hints
- **Field Validation**: Using built-in validators and constraints
- **Custom Validators**: Writing your own validation logic
- **Nested Models**: Handling complex data relationships
- **Request/Response Patterns**: Structuring API data flow
- **Error Handling**: Managing validation errors gracefully

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- Setup and basic models: 20 minutes
- Validation and custom validators: 30 minutes  
- Nested models and relationships: 25 minutes
- Request/Response patterns: 15 minutes

## 🚀 Quick Start

### Step 1: Navigate to this example
```bash
cd examples/02-pydantic-models
```

### Step 2: Install dependencies
```bash
# Install FastAPI and Pydantic with email validation
pip install "fastapi[standard]" "pydantic[email]"
```

### Step 3: Run the interactive tutorial
```bash
python main.py
```

### Step 4: Explore the API
- **Interactive Docs**: http://localhost:8000/docs
- **Validation Examples**: http://localhost:8000/examples/validation-errors
- **Model Features**: http://localhost:8000/examples/model-features

## 📚 Tutorial Structure

### 1. **Basic Models** (UserProfile)
**Learn**: Foundation of Pydantic data modeling
```python
class UserProfile(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    age: int = Field(..., ge=13, le=120)
```

**Key Concepts**:
- Type hints for automatic validation
- Field constraints (min_length, ge, le)
- Optional fields with defaults
- EmailStr for email validation

### 2. **Advanced Validation** (Product)
**Learn**: Custom validation logic and data transformation
```python
@validator('name')
def clean_name(cls, v):
    return v.title()  # Capitalize each word
```

**Key Concepts**:
- Custom validators with @validator
- Enum fields for controlled values
- Cross-field validation
- Data transformation during validation

### 3. **Nested Models** (Order, Address, OrderItem)
**Learn**: Complex data structures and relationships
```python
class Order(BaseModel):
    items: List[OrderItem]
    shipping_address: Address
```

**Key Concepts**:
- Nested model composition
- List validation
- Computed properties
- Root validators

### 4. **Request/Response Models**
**Learn**: API data flow patterns
```python
# Input model (accepts all fields)
class UserProfile(BaseModel): ...

# Output model (selective fields)  
class UserResponse(BaseModel): ...
```

**Key Concepts**:
- Separation of input/output models
- Response model filtering
- Computed response fields

## 🧪 Hands-On Exercises

### Exercise 1: Basic User Model
Create a simple user model and test validation:

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    age: int = Field(..., ge=13)
```

**Test it**: Create users with valid and invalid data

### Exercise 2: Custom Validation
Add a custom validator to clean usernames:

```python
@validator('username')
def clean_username(cls, v):
    # Remove spaces, convert to lowercase
    return v.replace(' ', '').lower()
```

**Test it**: Try usernames with spaces and uppercase letters

### Exercise 3: Nested Model
Create a blog post model with nested author:

```python
class Author(BaseModel):
    name: str
    email: EmailStr

class BlogPost(BaseModel):
    title: str
    content: str
    author: Author
    tags: List[str] = []
```

**Test it**: Create posts with nested author data

## 🔍 Interactive API Testing

### Using the Swagger UI (`/docs`)

1. **Try the `/users/` endpoint**:
   - Click "Try it out"
   - Enter valid user data
   - See successful validation
   - Try invalid data to see errors

2. **Test the `/products/` endpoint**:
   - Notice how custom validators clean data
   - Try invalid categories and see errors
   - Watch tags get deduplicated

3. **Experiment with `/orders/`**:
   - Create complex nested orders
   - See how validation works at all levels
   - Test postal code validation

### Understanding Validation Errors

Try these invalid inputs to see Pydantic errors:

```json
// Invalid user (age too young)
{
  "name": "Kid",
  "email": "kid@example.com", 
  "age": 10
}

// Invalid product (bad category)
{
  "name": "Test Product",
  "price": 29.99,
  "category": "invalid_category"
}
```

## 🎓 Key Learning Outcomes

After completing this tutorial, you'll understand:

✅ **How to create Pydantic models** with proper type hints  
✅ **How to add validation constraints** using Field()  
✅ **How to write custom validators** for complex rules  
✅ **How to handle nested data structures** with confidence  
✅ **How to separate input/output models** for clean APIs  
✅ **How to debug validation errors** effectively  

## 💡 Pro Tips

### 1. **Type Hints Are Essential**
```python
# Good - enables validation
name: str

# Bad - no validation
name
```

### 2. **Use Field() for Constraints**
```python
# Good - clear constraints
age: int = Field(..., ge=13, le=120)

# Okay but less clear
age: int  # Manual validation needed
```

### 3. **Custom Validators for Business Logic**
```python
@validator('username')
def username_must_be_unique(cls, v):
    # Check database, clean data, etc.
    return v.lower().strip()
```

### 4. **Separate Request/Response Models**
```python
class UserCreate(BaseModel):  # Input - has password
    username: str
    password: str

class UserResponse(BaseModel):  # Output - no password
    username: str
    created_at: datetime
```

## 🚨 Common Pitfalls

### ❌ **Missing Type Hints**
```python
class User(BaseModel):
    name = "default"  # Won't validate!
```

### ❌ **Not Using Field() for Constraints**
```python
# This won't prevent negative ages!
class User(BaseModel):
    age: int
```

### ❌ **Ignoring Validator Order**
```python
# Validators run in definition order
@validator('email')  # Runs first
def clean_email(cls, v): ...

@validator('email')  # Runs second  
def validate_domain(cls, v): ...
```

## 🔗 What's Next?

After mastering Pydantic fundamentals, you're ready for:

1. **CRUD Operations** (Example 03) - Use models in API endpoints
2. **Database Integration** (Example 04) - Connect models to databases  
3. **File Handling** (Example 05) - Validate file uploads
4. **Advanced Patterns** - Complex validation scenarios

## 💡 Key Takeaways

- **Type hints enable validation** - Pydantic uses them for automatic validation
- **Field() adds constraints** - min_length, ge, le for additional validation
- **Custom validators handle business logic** - Complex validation rules
- **Nested models represent relationships** - Complex data structures
- **Response models control output** - Separate input and output schemas

## 🐛 Common Pitfalls

1. **Missing type hints**: Without them, Pydantic can't validate
2. **Not using Field() constraints**: Basic validation should use built-in validators
3. **Validator naming issues**: Validator function names must match field names
4. **Forgetting exclude_unset**: Use `dict(exclude_unset=True)` for partial updates
5. **Complex validators**: Keep validation logic simple and focused

## 🔧 Development Tips

### Model Design

```python
# Good: Clear field names and constraints
class User(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    age: int = Field(..., ge=13, le=120, description="User age")

# Bad: Unclear names and no validation
class User(BaseModel):
    e: str
    a: int
```

### Validation Messages

```python
@validator('username')
def username_alphanumeric(cls, v):
    if not v.isalnum():
        raise ValueError('Username must be alphanumeric')
    return v
```

### Response Models

```python
# Separate input and output models
class UserCreate(BaseModel):    # Input: has password
    username: str
    password: str

class UserResponse(BaseModel):  # Output: no password
    id: int
    username: str
    created_at: datetime
```

---

**Ready to use models in API operations? Continue with [Example 03: CRUD Basics](../03-crud-basics/)!** ⚡