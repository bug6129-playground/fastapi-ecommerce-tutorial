# FastAPI Basics - Hello World Example

**Simple FastAPI example to learn the fundamentals** 🚀

## 🎯 What This Example Teaches

- Creating FastAPI applications
- Basic GET endpoints
- Path and query parameters
- Auto-generated documentation
- Async function basics

## 🚀 How to Run

1. **Navigate to this directory:**
   ```bash
   cd examples/01-hello-world
   ```

2. **Install FastAPI (if not done already):**
   ```bash
   pip install "fastapi[standard]"
   ```

3. **Run the application:**
   ```bash
   # Method 1: Direct run (includes instructions)
   python main.py
   
   # Method 2: Manual uvicorn command
   uvicorn main:app --reload
   ```

4. **Visit your API:**
   - **API**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Try These Endpoints

| Endpoint | Example | What it teaches |
|----------|---------|-----------------|
| `GET /` | http://localhost:8000 | Basic endpoint |
| `GET /hello/{name}` | http://localhost:8000/hello/Alice | Path parameters |
| `GET /greet` | http://localhost:8000/greet?name=Bob&enthusiastic=true | Query parameters |
| `GET /users/{user_id}/posts/{post_id}` | http://localhost:8000/users/1/posts/42 | Multiple path params |
| `GET /items/{item_id}` | http://localhost:8000/items/1?q=search&short=true | Mixed parameters |
| `GET /health` | http://localhost:8000/health | Health check pattern |

## 🎓 Key Learning Points

### 1. **FastAPI App Creation**
```python
app = FastAPI(
    title="My API",
    description="API description", 
    version="1.0.0"
)
```

### 2. **Route Decorators**
```python
@app.get("/")           # GET requests to root
@app.post("/items")     # POST requests to /items
```

### 3. **Path Parameters**
```python
@app.get("/hello/{name}")
async def greet(name: str):  # name comes from URL path
```

### 4. **Query Parameters**
```python
async def search(q: str = None):  # q comes from ?q=value
```

### 5. **Type Validation**
FastAPI automatically validates types:
- `/users/123` ✅ (123 is valid int)
- `/users/abc` ❌ (abc is not valid int)

## 🔄 Next Steps

After understanding this example:

1. **Explore the interactive docs** at http://localhost:8000/docs
2. **Try modifying the code** - add your own endpoints
3. **Experiment with different types** - try `float`, `bool`, etc.
4. **Move to Tutorial A2** to learn about data models

## 💡 Pro Tips

- Always use type hints - they enable FastAPI's magic
- Use meaningful function names - they show up in documentation  
- Add docstrings - they become part of your API docs
- Use `async def` for better performance
- The `/docs` endpoint is your best friend for testing

---

**Ready for more?** Check out [Tutorial A2: Pydantic Fundamentals](../../docs/02-data-models/learn-pydantic.md) to learn about data validation and request/response models!

*Author: bug6129 | FastAPI Basics Example*