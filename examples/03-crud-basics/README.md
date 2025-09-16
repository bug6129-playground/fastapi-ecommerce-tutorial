# CRUD Operations Fundamentals

**Learn HTTP methods and basic CRUD operations through a Task Manager API** 📋

This example demonstrates essential CRUD (Create, Read, Update, Delete) operations using FastAPI with in-memory storage. Perfect for understanding HTTP methods and API patterns before moving to database integration.

## 🎯 What You'll Learn

- **HTTP Methods**: GET, POST, PUT, PATCH, DELETE
- **Path Parameters**: Accessing URL segments as function parameters
- **Query Parameters**: Optional filtering and pagination
- **Request Bodies**: Sending data in POST/PUT requests
- **Response Models**: Structured API responses
- **Status Codes**: Proper HTTP status code usage
- **Error Handling**: 404 errors and validation errors
- **In-Memory Storage**: Simple data persistence patterns

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- Understanding concepts: 30 minutes
- Hands-on practice: 45 minutes
- Experimentation: 15 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]"
```

### Run the Example

```bash
# Navigate to this directory
cd examples/03-crud-basics

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Task List**: http://localhost:8000/tasks
- **Statistics**: http://localhost:8000/tasks/stats

## 📚 Key Concepts Explained

### 1. HTTP Methods and Their Purpose

| Method | Purpose | Example | Idempotent |
|--------|---------|---------|------------|
| `GET` | Retrieve data | `GET /tasks` | ✅ Yes |
| `POST` | Create new resource | `POST /tasks` | ❌ No |
| `PUT` | Replace entire resource | `PUT /tasks/1` | ✅ Yes |
| `PATCH` | Update part of resource | `PATCH /tasks/1` | ❌ No |
| `DELETE` | Remove resource | `DELETE /tasks/1` | ✅ Yes |

### 2. Path Parameters

```python
@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    # task_id comes from the URL path
    # GET /tasks/5 -> task_id = 5
```

### 3. Query Parameters

```python
@app.get("/tasks")
async def get_tasks(
    status: Optional[TaskStatus] = None,  # ?status=completed
    limit: int = 100                      # ?limit=10
):
    # GET /tasks?status=completed&limit=10
```

### 4. Request Bodies

```python
@app.post("/tasks")
async def create_task(task_data: TaskCreate):
    # task_data comes from request body (JSON)
```

## 🎮 Hands-On Exercises

### Exercise 1: Basic CRUD Operations

1. **Create a Task**:
   ```bash
   curl -X POST "http://localhost:8000/tasks" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "Learn FastAPI",
          "description": "Complete CRUD tutorial",
          "priority": "high"
        }'
   ```

2. **Get All Tasks**:
   ```bash
   curl "http://localhost:8000/tasks"
   ```

3. **Get Specific Task**:
   ```bash
   curl "http://localhost:8000/tasks/1"
   ```

4. **Update Task Completely**:
   ```bash
   curl -X PUT "http://localhost:8000/tasks/1" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "Master FastAPI",
          "description": "Become expert in FastAPI",
          "status": "in_progress",
          "priority": "urgent"
        }'
   ```

5. **Update Task Partially**:
   ```bash
   curl -X PATCH "http://localhost:8000/tasks/1" \
        -H "Content-Type: application/json" \
        -d '{"status": "completed"}'
   ```

6. **Delete Task**:
   ```bash
   curl -X DELETE "http://localhost:8000/tasks/1"
   ```

### Exercise 2: Filtering and Pagination

1. **Filter by Status**:
   ```bash
   curl "http://localhost:8000/tasks?status=todo"
   ```

2. **Filter by Priority**:
   ```bash
   curl "http://localhost:8000/tasks?priority=high"
   ```

3. **Pagination**:
   ```bash
   curl "http://localhost:8000/tasks?limit=2&skip=0"  # First 2 tasks
   curl "http://localhost:8000/tasks?limit=2&skip=2"  # Next 2 tasks
   ```

4. **Combined Filters**:
   ```bash
   curl "http://localhost:8000/tasks?status=todo&priority=high&limit=5"
   ```

### Exercise 3: Interactive API Testing

Use the automatic documentation at http://localhost:8000/docs to:

1. **Try all endpoints** using the interactive interface
2. **Explore request/response schemas** in the documentation
3. **Test error scenarios** (e.g., accessing non-existent task ID)
4. **View example data** for each endpoint

## 🔍 Code Structure Walkthrough

### 1. Data Models (`TaskBase`, `TaskCreate`, `TaskUpdate`, `Task`)
- **Separation of concerns**: Different models for different operations
- **Validation**: Built-in Pydantic validation for all fields
- **Enums**: Type-safe status and priority values

### 2. In-Memory Storage
```python
tasks_db: List[Task] = []  # Simple list for storage
next_task_id = 1           # Auto-incrementing ID counter
```

### 3. Helper Functions
```python
def find_task_by_id(task_id: int) -> Optional[Task]:
    """Utility function for task lookup"""

def get_task_index(task_id: int) -> int:
    """Get list index for updates/deletes"""
```

### 4. CRUD Endpoints

**Create (POST)**:
```python
@app.post("/tasks", status_code=201)
async def create_task(task_data: TaskCreate):
    # Generate ID, add timestamps, store task
```

**Read (GET)**:
```python
@app.get("/tasks")
async def get_tasks(status: Optional[TaskStatus] = None):
    # Filter, paginate, return tasks

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    # Find by ID, return single task or 404
```

**Update (PUT/PATCH)**:
```python
@app.put("/tasks/{task_id}")      # Complete replacement
@app.patch("/tasks/{task_id}")    # Partial update
```

**Delete (DELETE)**:
```python
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    # Find, remove, confirm deletion
```

## 🎯 Real-World Patterns Demonstrated

### 1. **Error Handling**
```python
if not task:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found"
    )
```

### 2. **Timestamps**
```python
created_at=datetime.now(),
updated_at=datetime.now()
```

### 3. **Pagination**
```python
paginated_tasks = filtered_tasks[skip:skip + limit]
```

### 4. **Status Codes**
- `200 OK` - Successful GET, PUT, PATCH, DELETE
- `201 Created` - Successful POST
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Validation errors

## 🧪 Testing Your Understanding

### Challenge 1: Add New Fields
Add these fields to the Task model:
- `assigned_to: Optional[str]` - Who's responsible
- `estimated_hours: Optional[int]` - Time estimate
- `tags: List[str]` - Task categories

### Challenge 2: Add New Endpoints
Create these additional endpoints:
- `GET /tasks/priority/{priority}` - Filter by priority
- `PUT /tasks/{task_id}/assign` - Assign task to someone
- `GET /tasks/overdue` - Find overdue tasks

### Challenge 3: Add Validation
Add custom validators:
- Due date must be in the future
- High priority tasks require a description
- Title must not contain profanity

### Challenge 4: Bulk Operations
Implement:
- `POST /tasks/bulk` - Create multiple tasks
- `PATCH /tasks/bulk-status` - Update status of multiple tasks
- `DELETE /tasks/bulk` - Delete multiple tasks by IDs

## 🔗 What's Next?

After mastering CRUD operations, you're ready for:

1. **Database Integration** (Example 04) - Replace in-memory storage with SQLModel
2. **File Handling** (Example 05) - Add file upload capabilities
3. **Relationships** (Example 06) - Connect related data models
4. **Authentication** (Example 07) - Protect your API endpoints

## 💡 Key Takeaways

- **CRUD is fundamental** - All APIs need these basic operations
- **HTTP methods have meaning** - Use the right method for each operation
- **Validation is automatic** - Pydantic handles request/response validation
- **Error handling matters** - Always provide meaningful error messages
- **Documentation is free** - FastAPI generates interactive docs automatically

## 🐛 Common Pitfalls

1. **Wrong HTTP Methods**: Don't use GET for data modification
2. **Missing Error Handling**: Always handle cases where resources don't exist
3. **Inconsistent Status Codes**: Use standard HTTP status codes correctly
4. **No Validation**: Always validate input data
5. **Poor Naming**: Use clear, RESTful endpoint names

---

**Ready to connect to a real database? Continue with [Example 04: Database Integration](../04-database-simple/)!** 💾