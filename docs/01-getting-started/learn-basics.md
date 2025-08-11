# Tutorial A: FastAPI Basics

**Learn FastAPI fundamentals with simple, focused examples** 📚

In this tutorial, you'll learn core FastAPI concepts through bite-sized examples that are easy to understand and experiment with. Perfect for getting familiar with the framework before diving into complex projects.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ How to create and run a FastAPI application
- ✅ How to define API endpoints with different HTTP methods
- ✅ How to use path and query parameters
- ✅ How FastAPI's automatic documentation works
- ✅ Basic async/await concepts in web APIs

## ⚡ Quick Setup

```bash
# Navigate to the examples directory
cd examples/01-hello-world

# Install dependencies (if not done already)
pip install "fastapi[standard]"

# Run the example
python main.py
# Then: uvicorn main:app --reload
```

## 📝 Code Example

Let's examine the simple hello world example:

```python
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
```

## 🧪 Try It Yourself

1. **Run the application:**
   ```bash
   cd examples/01-hello-world
   python main.py
   ```

2. **Test these endpoints:**
   - http://localhost:8000 - Basic hello
   - http://localhost:8000/hello/YourName - Path parameter
   - http://localhost:8000/greet?name=Alice&enthusiastic=true - Query parameters
   - http://localhost:8000/items/42?q=search&short=true - Mixed parameters

3. **Explore the documentation:**
   - http://localhost:8000/docs - Interactive Swagger UI
   - http://localhost:8000/redoc - Alternative documentation

## 🔍 Key Concepts Explained

### 1. **FastAPI Instance**
```python
app = FastAPI(title="My API", description="API description", version="1.0.0")
```
- Creates your application object
- Metadata is used for auto-generated documentation
- This is where you configure global settings

### 2. **Route Decorators**
```python
@app.get("/path")          # Handle GET requests
@app.post("/path")         # Handle POST requests  
@app.put("/path")          # Handle PUT requests
@app.delete("/path")       # Handle DELETE requests
```
- Decorators register your function as a request handler
- The path defines what URL triggers this function

### 3. **Path Parameters**
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # user_id comes from the URL path
```
- Defined with `{parameter_name}` in the path
- Automatically extracted from URL and passed to function
- Type hints provide automatic validation

### 4. **Query Parameters**
```python
async def search(q: str = None, limit: int = 10):
    # q and limit come from ?q=value&limit=20
```
- Function parameters that aren't in the path become query parameters
- Default values make them optional
- Type hints provide automatic validation

### 5. **Async Functions**
```python
async def my_endpoint():
    return {"message": "Hello"}
```
- `async def` makes your function asynchronous
- Allows handling multiple requests concurrently
- You can also use regular `def` functions

## 🎯 Practice Challenges

Try these exercises to reinforce your learning:

### Challenge 1: Personal Info API
Create endpoints for:
- `GET /profile/{username}` - Get user profile
- `GET /profile/{username}/age` - Get just the age
- `GET /search` - Search profiles with query parameters

### Challenge 2: Calculator API
Create endpoints for:
- `GET /add/{a}/{b}` - Add two numbers
- `GET /calculate` - Calculator with query params (operation, a, b)

### Challenge 3: Customize Documentation
Experiment with FastAPI metadata:
```python
app = FastAPI(
    title="Your Custom API",
    description="Your description with **markdown**!",
    version="2.0.0",
    contact={"name": "Your Name"},
    license_info={"name": "MIT"},
)
```

## 🔧 Common Patterns

### Pattern 1: Resource with Optional Details
```python
@app.get("/posts/{post_id}")
async def get_post(post_id: int, include_comments: bool = False):
    post = {"id": post_id, "title": "Sample Post"}
    if include_comments:
        post["comments"] = ["Comment 1", "Comment 2"]
    return post
```

### Pattern 2: Search with Pagination
```python
@app.get("/search")
async def search_items(q: str, page: int = 1, size: int = 10):
    return {
        "query": q,
        "page": page,
        "size": size,
        "results": ["item1", "item2"]  # Mock results
    }
```

## ❓ Troubleshooting

**Q: Why use `async def` instead of `def`?**
A: `async def` allows FastAPI to handle multiple requests concurrently, improving performance. You can use regular `def` too, but `async` is recommended.

**Q: What if I make a typo in the URL?**
A: FastAPI will return a 404 Not Found error automatically. Check your browser's developer tools for the exact error.

**Q: How do I make a parameter required?**
A: Don't provide a default value. For example: `name: str` (required) vs `name: str = "default"` (optional).

**Q: Can I have multiple path parameters?**
A: Yes! Example: `@app.get("/users/{user_id}/posts/{post_id}")`

## ➡️ What's Next?

You've learned the basics! In **Tutorial A2: [Pydantic Fundamentals](../02-data-models/learn-pydantic.md)**, you'll discover:

- 📝 **Request and Response Models** - Structure your API data
- ✅ **Data Validation** - Automatic input validation
- 🔒 **Type Safety** - Catch errors before they happen
- 📊 **JSON Schema** - Auto-generated API documentation

Or jump to **Tutorial B1: [E-Commerce Foundation](apply-ecommerce.md)** to start building a real application!

---

## 📚 Summary

**What you learned:**
- ✅ Creating FastAPI applications
- ✅ Defining GET endpoints with decorators
- ✅ Using path parameters `{param}`
- ✅ Using query parameters with defaults
- ✅ Auto-generated API documentation
- ✅ Basic async/await concepts

**Key takeaways:**
1. FastAPI makes API creation incredibly simple
2. Type hints provide automatic validation and documentation
3. The interactive docs (`/docs`) are perfect for testing
4. Path parameters are required, query parameters can be optional
5. FastAPI handles the boring stuff so you focus on business logic

Great job! You now understand FastAPI fundamentals. 🎉

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A1*