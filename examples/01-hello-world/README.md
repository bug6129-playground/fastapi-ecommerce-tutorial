# FastAPI Basics - Hello World

**Learn FastAPI fundamentals through simple endpoint examples** 🚀

This example introduces you to FastAPI basics through a simple Hello World application. Learn how to create your first API, handle different types of parameters, and understand FastAPI's automatic documentation generation.

## 🎯 What You'll Learn

- **FastAPI Applications**: Creating and configuring FastAPI instances
- **Basic Routing**: GET endpoints with decorators
- **Path Parameters**: Extracting values from URL paths
- **Query Parameters**: Handling optional URL parameters
- **Type Validation**: Automatic validation and conversion
- **API Documentation**: Auto-generated interactive docs
- **Async Functions**: Basic async/await patterns

## ⏱️ Time Commitment

**Estimated Time: 1 hour**

- Setup and basics: 20 minutes
- Parameter handling: 25 minutes
- Documentation exploration: 15 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]"
```

### Run the Example

```bash
# Navigate to this directory
cd examples/01-hello-world

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📚 Key Concepts Explained

### 1. FastAPI Application Setup

```python
from fastapi import FastAPI

app = FastAPI(
    title="My First FastAPI App",
    description="A simple FastAPI application for learning",
    version="1.0.0",
)
```

### 2. Route Decorators

```python
@app.get("/")           # Handle GET requests to root
@app.post("/items")     # Handle POST requests to /items
@app.put("/items/{id}") # Handle PUT requests with path parameter
```

### 3. Path Parameters

```python
@app.get("/hello/{name}")
async def say_hello(name: str):
    # 'name' automatically extracted from URL
    # GET /hello/Alice -> name = "Alice"
    return {"message": f"Hello, {name}!"}
```

### 4. Query Parameters

```python
@app.get("/greet")
async def greet_with_query(
    name: str = "World",        # Default value
    age: int = None            # Optional parameter
):
    # GET /greet?name=Alice&age=25
    return {"message": f"Hello, {name}!", "age": age}
```

## 🎮 Hands-On Exercises

### Exercise 1: Explore Existing Endpoints

1. **Basic Hello World**:
   ```bash
   curl "http://localhost:8000/"
   ```

2. **Path Parameters**:
   ```bash
   curl "http://localhost:8000/hello/YourName"
   ```

3. **Query Parameters**:
   ```bash
   curl "http://localhost:8000/greet?name=Alice&age=25"
   ```

4. **Health Check**:
   ```bash
   curl "http://localhost:8000/health"
   ```

### Exercise 2: Interactive Documentation

1. **Explore Swagger UI**:
   - Visit http://localhost:8000/docs
   - Try the "Try it out" button on different endpoints
   - Notice automatic type validation

2. **Alternative Documentation**:
   - Visit http://localhost:8000/redoc
   - Compare the two documentation styles

### Exercise 3: Add Your Own Endpoints

1. **Add a new endpoint** to `main.py`:
   ```python
   @app.get("/calculate/{operation}")
   async def simple_calculator(
       operation: str,
       a: float = Query(..., description="First number"),
       b: float = Query(..., description="Second number")
   ):
       if operation == "add":
           return {"result": a + b}
       elif operation == "multiply":
           return {"result": a * b}
       else:
           return {"error": "Unsupported operation"}
   ```

2. **Test your endpoint**:
   ```bash
   curl "http://localhost:8000/calculate/add?a=5&b=3"
   ```

## 🔍 Code Structure Walkthrough

### 1. Application Configuration

```python
# Create FastAPI instance with metadata
app = FastAPI(
    title="My First FastAPI App",      # Shows in docs
    description="Description here",    # Shows in docs  
    version="1.0.0",                  # API version
)
```

### 2. Route Handlers

```python
@app.get("/")                    # Route decorator
async def read_root():           # Async function (recommended)
    """Docstring becomes API documentation."""
    return {"message": "Hello, World!"}
```

### 3. Parameter Types

| Type | Example | FastAPI Behavior |
|------|---------|------------------|
| `str` | `name: str` | No conversion |
| `int` | `user_id: int` | String → int, validates |
| `float` | `price: float` | String → float, validates |
| `bool` | `active: bool` | "true"/"1" → True |

### 4. Error Handling

FastAPI automatically handles:
- Type conversion errors (400 Bad Request)
- Missing required parameters (422 Unprocessable Entity)
- Invalid path parameters (404 Not Found)

## 🎯 FastAPI Features Demonstrated

### 1. **Automatic Validation**

```python
# This endpoint validates automatically:
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # user_id is guaranteed to be an integer
    return {"user_id": user_id}

# Try: /users/abc → 422 Validation Error
# Try: /users/123 → 200 Success
```

### 2. **Interactive Documentation**

- **Swagger UI** (`/docs`): Test endpoints directly
- **ReDoc** (`/redoc`): Clean, readable documentation  
- **OpenAPI Schema** (`/openapi.json`): Machine-readable spec

### 3. **Type Hints Integration**

```python
# Type hints enable:
async def endpoint(name: str, age: int, active: bool = True):
    # - Automatic validation
    # - Editor autocompletion  
    # - Documentation generation
    # - Error messages
    pass
```

## 🧪 Testing Your Understanding

### Challenge 1: Add More Endpoints
Create endpoints for:
- `GET /square/{number}` - Return number squared
- `GET /reverse` - Reverse a string from query parameter
- `GET /user-info/{user_id}` - Return user info with query filters

### Challenge 2: Add Validation
Enhance endpoints with:
- Parameter constraints (min/max values)
- Custom descriptions for parameters
- Different response formats

### Challenge 3: Error Scenarios
Test what happens with:
- Invalid parameter types
- Missing required parameters
- Very large numbers
- Special characters in strings

## 🔗 What's Next?

After mastering the basics, you're ready for:

1. **Data Models** (Example 02) - Learn Pydantic for data validation
2. **CRUD Operations** (Example 03) - Handle POST, PUT, DELETE requests
3. **Database Integration** (Example 04) - Connect to databases
4. **Advanced Features** - File uploads, authentication, testing

## 💡 Key Takeaways

- **Type hints are essential** - They enable FastAPI's automatic validation
- **Documentation is free** - FastAPI generates interactive docs automatically
- **Async is recommended** - Use `async def` for better performance
- **Parameters are flexible** - Path, query, and body parameters work seamlessly
- **Validation is automatic** - FastAPI handles type conversion and validation

## 🐛 Common Pitfalls

1. **Missing type hints**: Without them, FastAPI can't provide validation
2. **Forgetting async**: Use `async def` instead of `def` for endpoints
3. **Not using `/docs`**: The interactive documentation is your best debugging tool
4. **Ignoring error responses**: Always test with invalid inputs
5. **Hardcoded values**: Use parameters instead of hardcoded responses

## 🔧 Development Tips

### Quick Testing

```bash
# Test endpoints quickly with curl
curl "http://localhost:8000/hello/test"
curl "http://localhost:8000/greet?name=Alice"

# Or use the interactive docs at /docs
# Click "Try it out" to test any endpoint
```

### Debugging

```python
# Add print statements for debugging
@app.get("/debug/{value}")
async def debug_endpoint(value: str):
    print(f"Received: {value}")  # Shows in terminal
    return {"received": value}
```

---

**Ready to learn data validation? Continue with [Example 02: Pydantic Models](../02-pydantic-models/)!** 📝