"""
FastAPI Basics - Hello World Example
===================================

This example demonstrates the fundamental concepts of FastAPI:
- Creating a FastAPI application instance
- Defining route handlers with decorators
- Using path and query parameters
- Automatic API documentation generation

Author: bug6129
"""

from fastapi import FastAPI

# Create FastAPI application instance
app = FastAPI(
    title="FastAPI Basics Tutorial",
    description="Simple examples to learn FastAPI fundamentals",
    version="1.0.0"
)

# 1. Basic GET endpoint
@app.get("/")
async def root():
    """
    Root endpoint - the simplest possible API endpoint.
    
    Returns:
        dict: A simple welcome message
    """
    return {"message": "Hello, FastAPI!"}

# 2. Path parameters
@app.get("/hello/{name}")
async def greet_person(name: str):
    """
    Endpoint with path parameter.
    
    Path parameters are part of the URL path and are required.
    FastAPI automatically extracts them and passes to your function.
    
    Args:
        name (str): The name from the URL path
        
    Returns:
        dict: Personalized greeting message
        
    Example:
        GET /hello/Alice -> {"greeting": "Hello, Alice!"}
    """
    return {"greeting": f"Hello, {name}!"}

# 3. Query parameters
@app.get("/greet")
async def greet_with_options(name: str = "World", enthusiastic: bool = False):
    """
    Endpoint with query parameters.
    
    Query parameters come after the ? in the URL and are optional
    when they have default values.
    
    Args:
        name (str): Name to greet (default: "World")
        enthusiastic (bool): Whether to add excitement (default: False)
        
    Returns:
        dict: Greeting message with options applied
        
    Examples:
        GET /greet -> {"message": "Hello, World!"}
        GET /greet?name=Bob -> {"message": "Hello, Bob!"}
        GET /greet?name=Alice&enthusiastic=true -> {"message": "Hello, Alice!!!"}
    """
    greeting = f"Hello, {name}"
    if enthusiastic:
        greeting += "!!!"
    else:
        greeting += "!"
    
    return {"message": greeting}

# 4. Multiple path parameters
@app.get("/users/{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    """
    Endpoint with multiple path parameters.
    
    Shows how to handle nested resources in REST APIs.
    FastAPI automatically validates that user_id and post_id are integers.
    
    Args:
        user_id (int): The user's ID
        post_id (int): The post's ID
        
    Returns:
        dict: Information about the user's post
    """
    return {
        "user_id": user_id,
        "post_id": post_id,
        "message": f"This is post {post_id} by user {user_id}"
    }

# 5. Mixed path and query parameters
@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str = None, short: bool = False):
    """
    Endpoint combining path and query parameters.
    
    This is a common pattern in REST APIs where you have a resource
    identified by path parameters, with optional query parameters
    for filtering or formatting.
    
    Args:
        item_id (int): The item ID (from path)
        q (str, optional): Search query (from query string)
        short (bool): Whether to return short format (from query string)
        
    Returns:
        dict: Item information with applied filters
    """
    item = {"item_id": item_id, "name": f"Item {item_id}"}
    
    if q:
        item["q"] = q
        item["description"] = f"Item {item_id} matching query: {q}"
    
    if short:
        # Return only essential fields for short format
        return {"item_id": item_id, "name": item["name"]}
    
    return item

# 6. Different HTTP methods preview (we'll learn more in next tutorial)
@app.post("/items")
async def create_item():
    """
    A preview of POST endpoints.
    
    We'll learn more about handling request bodies in the next tutorial.
    For now, this just shows that FastAPI supports all HTTP methods.
    """
    return {"message": "Item created! (We'll learn to handle data in Tutorial 2)"}

# Health check endpoint (common in production APIs)
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    This is a standard endpoint that monitoring systems use to check
    if your API is running properly.
    """
    return {"status": "healthy", "service": "FastAPI Basics Tutorial"}

# If running this file directly, provide helpful instructions
if __name__ == "__main__":
    import uvicorn
    print("🚀 FastAPI Basics Example")
    print("=" * 30)
    print("Starting server...")
    print("Visit: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Press CTRL+C to quit")
    print("=" * 30)
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)