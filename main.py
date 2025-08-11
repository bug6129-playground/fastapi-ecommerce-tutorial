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