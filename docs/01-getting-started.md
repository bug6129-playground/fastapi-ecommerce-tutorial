# Chapter 1: Getting Started with FastAPI

**Welcome to your FastAPI learning journey!** 🚀

In this first chapter, you'll set up your development environment, understand what FastAPI is, and create your very first API. By the end of this chapter, you'll have a working FastAPI application running on your machine.

## 📚 What You'll Learn

- What is FastAPI and why it's awesome
- Setting up your development environment
- Creating your first FastAPI application
- Understanding the project structure
- Running and testing your API
- Exploring auto-generated documentation

## 🤔 What is FastAPI?

FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. Here's why it's amazing:

### ⚡ Key Benefits

1. **Very Fast**: On par with NodeJS and Go performance
2. **Fast to Code**: Increase development speed by 200% to 300%
3. **Fewer Bugs**: Reduce about 40% of human errors
4. **Intuitive**: Great editor support with auto-completion
5. **Easy**: Designed to be easy to use and learn
6. **Short**: Minimize code duplication
7. **Robust**: Get production-ready code with automatic documentation
8. **Standards-based**: Based on OpenAPI and JSON Schema

### 🆚 FastAPI vs Others

| Feature | FastAPI | Flask | Django REST |
|---------|---------|-------|-------------|
| Performance | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Auto Documentation | ✅ Built-in | ❌ Manual | ❌ Manual |
| Type Safety | ✅ Native | ❌ Optional | ❌ Optional |
| Async Support | ✅ Native | ✅ Added later | ✅ Added later |
| Modern Python | ✅ Python 3.8+ | ✅ Any Python | ✅ Any Python |

## 🛠️ Development Environment Setup

### Step 1: Verify Python Installation

First, make sure you have Python 3.8 or higher installed:

```bash
# Check Python version
python --version
# or
python3 --version

# Should output something like: Python 3.9.x or higher
```

**Don't have Python?** Download it from [python.org](https://www.python.org/downloads/)

### Step 2: Choose Your Setup Method

#### Option A: VS Code Setup (Recommended)

**Why VS Code?**
- Excellent Python support
- Built-in terminal
- Great debugging tools
- Extensions for FastAPI development

**Steps:**
1. **Download and install VS Code**: [code.visualstudio.com](https://code.visualstudio.com/)
2. **Install Python Extension**: 
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Python" by Microsoft
   - Click Install

3. **Create your project:**
   ```bash
   # Create project directory
   mkdir fastapi-ecommerce-tutorial
   cd fastapi-ecommerce-tutorial
   
   # Open in VS Code
   code .
   ```

4. **Set up Python environment:**
   - Press `Ctrl+Shift+P` (Cmd+Shift+P on Mac)
   - Type "Python: Create Environment"
   - Select "Venv"
   - Choose your Python interpreter
   - VS Code will create and activate the virtual environment

#### Option B: Command Line Setup

```bash
# Create project directory
mkdir fastapi-ecommerce-tutorial
cd fastapi-ecommerce-tutorial

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install FastAPI

```bash
# Install FastAPI with all standard dependencies
pip install "fastapi[standard]"

# This installs:
# - FastAPI framework
# - Uvicorn (ASGI server)
# - Python-multipart (for forms and file uploads)
# - Email-validator (for email validation)
```

**What did we just install?**
- **FastAPI**: The main framework
- **Uvicorn**: The server that runs your FastAPI app
- **Standard extras**: Common dependencies you'll need

### Step 4: Verify Installation

```bash
# Check FastAPI version
python -c "import fastapi; print(fastapi.__version__)"

# Check Uvicorn
python -c "import uvicorn; print('Uvicorn installed successfully')"
```

## 🎯 Your First FastAPI Application

Now let's create your first FastAPI application! We'll start simple and build up.

### Step 1: Create the Main Application File

Create a new file called `main.py` in your project directory:

```python
"""
Your First FastAPI Application
=============================

This is a simple "Hello World" FastAPI application that demonstrates
the basic structure and key concepts of FastAPI.

Key Concepts Demonstrated:
- Creating a FastAPI instance
- Defining route handlers with decorators
- Using async functions
- Automatic API documentation generation
- Type hints for better code quality

Author: bug6129
"""

from fastapi import FastAPI

# Create a FastAPI instance
# This is the main application object that will handle all requests
app = FastAPI(
    title="My First FastAPI App",
    description="A simple FastAPI application for learning",
    version="1.0.0",
)

# Define a route handler for the root endpoint
# The @app.get() decorator tells FastAPI this function handles GET requests to "/"
@app.get("/")
async def read_root():
    """
    Root endpoint - returns a welcome message.
    
    This is your API's homepage. When someone visits your API's root URL,
    they'll see this message.
    
    Returns:
        dict: A welcome message with status information
    """
    return {
        "message": "Hello, World!",
        "status": "API is running successfully",
        "version": "1.0.0",
        "framework": "FastAPI"
    }

# Define another endpoint that accepts a path parameter
@app.get("/hello/{name}")
async def say_hello(name: str):
    """
    Personalized greeting endpoint.
    
    This endpoint demonstrates path parameters - the {name} in the URL
    becomes a parameter to your function.
    
    Args:
        name (str): The name to greet (from the URL path)
        
    Returns:
        dict: A personalized greeting message
        
    Example:
        GET /hello/Alice -> {"message": "Hello, Alice!", "name": "Alice"}
    """
    return {
        "message": f"Hello, {name}!",
        "name": name,
        "endpoint": "personalized_greeting"
    }

# Define an endpoint that accepts query parameters
@app.get("/greet")
async def greet_with_query(name: str = "World", age: int = None):
    """
    Greeting endpoint with query parameters.
    
    This endpoint demonstrates query parameters - optional parameters
    that can be passed in the URL after a question mark.
    
    Args:
        name (str): Name to greet (default: "World")
        age (int, optional): Age of the person being greeted
        
    Returns:
        dict: Greeting message with optional age information
        
    Examples:
        GET /greet -> {"message": "Hello, World!"}
        GET /greet?name=Alice -> {"message": "Hello, Alice!"}
        GET /greet?name=Bob&age=25 -> {"message": "Hello, Bob!", "age": 25}
    """
    response = {
        "message": f"Hello, {name}!",
        "name": name
    }
    
    # Add age to response if provided
    if age is not None:
        response["age"] = age
        response["message"] = f"Hello, {name}! Nice to know you're {age} years old."
    
    return response

# Define a health check endpoint (common in production APIs)
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    This endpoint is commonly used by monitoring systems and load balancers
    to check if your API is running and healthy.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "FastAPI E-Commerce Tutorial",
        "version": "1.0.0"
    }

# If this file is run directly (not imported), show helpful information
if __name__ == "__main__":
    print("🚀 FastAPI Application Created!")
    print("=" * 40)
    print("To run this application:")
    print("1. Make sure you're in the project directory")
    print("2. Run: uvicorn main:app --reload")
    print("3. Open your browser to: http://localhost:8000")
    print("4. Check the API docs: http://localhost:8000/docs")
    print("=" * 40)
```

### Step 2: Run Your Application

Now let's run your FastAPI application:

```bash
# Run the application with auto-reload (for development)
uvicorn main:app --reload

# You should see output like:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [12345] using StatReload
# INFO:     Started server process [12346]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Command Breakdown:**
- `uvicorn`: The ASGI server that runs FastAPI apps
- `main:app`: Import the `app` object from the `main.py` file
- `--reload`: Automatically restart the server when code changes

### Step 3: Test Your API

Open your web browser and visit these URLs:

1. **Root endpoint**: http://localhost:8000
   ```json
   {
     "message": "Hello, World!",
     "status": "API is running successfully",
     "version": "1.0.0",
     "framework": "FastAPI"
   }
   ```

2. **Personalized greeting**: http://localhost:8000/hello/YourName
   ```json
   {
     "message": "Hello, YourName!",
     "name": "YourName",
     "endpoint": "personalized_greeting"
   }
   ```

3. **Query parameters**: http://localhost:8000/greet?name=Alice&age=25
   ```json
   {
     "message": "Hello, Alice! Nice to know you're 25 years old.",
     "name": "Alice",
     "age": 25
   }
   ```

4. **Health check**: http://localhost:8000/health
   ```json
   {
     "status": "healthy",
     "service": "FastAPI E-Commerce Tutorial",
     "version": "1.0.0"
   }
   ```

## 📖 Exploring Auto-Generated Documentation

One of FastAPI's coolest features is automatic API documentation! 

### Interactive Documentation (Swagger UI)

Visit: **http://localhost:8000/docs**

You'll see a beautiful, interactive API documentation where you can:
- 📋 See all your endpoints
- 📝 Read endpoint descriptions
- 🧪 Test endpoints directly in the browser
- 📊 See request/response schemas

**Try it out:**
1. Click on any endpoint to expand it
2. Click "Try it out"
3. Enter parameters if needed
4. Click "Execute"
5. See the response directly in the browser!

### Alternative Documentation (ReDoc)

Visit: **http://localhost:8000/redoc**

This provides a different, more readable documentation style that's great for sharing with team members or API consumers.

### OpenAPI Schema

Visit: **http://localhost:8000/openapi.json**

This shows the raw OpenAPI schema that describes your entire API. This can be imported into tools like Postman, Insomnia, or used to generate client libraries.

## 🏗️ Understanding the Code Structure

Let's break down what we just created:

### 1. Imports and App Creation
```python
from fastapi import FastAPI

app = FastAPI(
    title="My First FastAPI App",
    description="A simple FastAPI application for learning",
    version="1.0.0",
)
```

- **FastAPI import**: Gets the main FastAPI class
- **App instance**: Creates your application with metadata for documentation

### 2. Route Decorators
```python
@app.get("/")
async def read_root():
```

- **`@app.get("/"`**: Decorator that registers this function as a GET handler for the root path
- **`async def`**: Makes the function asynchronous (can handle multiple requests concurrently)
- **Function name**: Can be anything, but should be descriptive

### 3. Path Parameters
```python
@app.get("/hello/{name}")
async def say_hello(name: str):
```

- **`{name}`**: Path parameter that becomes a function argument
- **Type hint `str`**: Tells FastAPI to expect a string and validates it

### 4. Query Parameters
```python
@app.get("/greet")
async def greet_with_query(name: str = "World", age: int = None):
```

- **Function parameters**: Automatically become query parameters
- **Default values**: Make parameters optional
- **Type hints**: Provide validation and documentation

## 🎉 Congratulations!

You've successfully:
✅ Set up your FastAPI development environment  
✅ Created your first FastAPI application  
✅ Learned about path and query parameters  
✅ Explored automatic API documentation  
✅ Understood the basic FastAPI structure  

## 🔄 Quick Recap

**What we covered:**
1. **FastAPI basics**: What it is and why it's great
2. **Environment setup**: Python, virtual environment, VS Code
3. **First application**: Simple API with multiple endpoints
4. **Documentation**: Automatic Swagger and ReDoc generation
5. **Key concepts**: Decorators, async functions, type hints

## 🎯 Practice Challenges

Before moving to the next chapter, try these exercises:

### Challenge 1: Add More Endpoints
Add these new endpoints to your `main.py`:

```python
# Add a goodbye endpoint
@app.get("/goodbye/{name}")
async def say_goodbye(name: str):
    return {"message": f"Goodbye, {name}! See you later!"}

# Add a math endpoint that adds two numbers
@app.get("/add")
async def add_numbers(a: int, b: int):
    result = a + b
    return {"a": a, "b": b, "result": result, "operation": "addition"}
```

### Challenge 2: Experiment with Parameters
1. Create an endpoint that accepts both path and query parameters
2. Try different data types (int, float, bool)
3. Make some parameters required and others optional

### Challenge 3: Customize Your Documentation
Update your FastAPI app creation to include more metadata:

```python
app = FastAPI(
    title="Your Custom API Name",
    description="Your custom description here",
    version="1.0.0",
    contact={
        "name": "Your Name",
        "email": "your.email@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
```

## 🚦 Troubleshooting

### Common Issues and Solutions

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Make sure your virtual environment is activated and FastAPI is installed:
```bash
pip install "fastapi[standard]"
```

**Problem**: `Port already in use`
**Solution**: Use a different port:
```bash
uvicorn main:app --reload --port 8001
```

**Problem**: Changes not reflecting
**Solution**: Make sure you're using the `--reload` flag and saving your files

**Problem**: VS Code not showing Python autocomplete
**Solution**: 
1. Install the Python extension
2. Select the correct Python interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
3. Choose the interpreter from your virtual environment

## ➡️ What's Next?

In [Chapter 2: FastAPI Fundamentals](02-fundamentals.md), you'll learn:

- **Request and Response Models**: Using Pydantic for data validation
- **HTTP Methods**: POST, PUT, DELETE endpoints
- **Request Body Handling**: Working with JSON data
- **Error Handling**: Proper HTTP status codes and error responses
- **Dependency Injection**: FastAPI's powerful dependency system

**Ready to continue?** Great work completing Chapter 1! 🎉

---

### 📚 Additional Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [HTTP Status Codes Reference](https://httpstatuses.com/)
- [REST API Best Practices](https://restfulapi.net/rest-api-design-tutorial-with-example/)

### 💡 Pro Tips

1. **Always use type hints** - They make your code self-documenting and enable FastAPI's magic
2. **Use meaningful function names** - They become part of your API documentation
3. **Add docstrings** - They appear in the auto-generated documentation
4. **Test as you go** - Use the `/docs` endpoint to test your API immediately
5. **Keep it simple** - Start with basic endpoints and add complexity gradually

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Chapter 1 of 8*