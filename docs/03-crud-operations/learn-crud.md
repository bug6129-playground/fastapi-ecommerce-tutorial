# Tutorial A3: HTTP Methods & CRUD Operations

**Master RESTful API patterns with HTTP methods** 📋

In this tutorial, you'll learn how to implement complete CRUD (Create, Read, Update, Delete) operations using proper HTTP methods. This is essential for building RESTful APIs that follow industry standards and best practices.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ HTTP methods (GET, POST, PUT, PATCH, DELETE) and when to use each
- ✅ REST API design principles and resource-based routing
- ✅ Request body handling for data submission
- ✅ Proper HTTP status codes for different operations
- ✅ Error handling and validation in CRUD operations
- ✅ In-memory data storage patterns (before databases)

## 🧠 Understanding HTTP Methods

### **The CRUD Mapping**

| Operation | HTTP Method | Example | Purpose |
|-----------|-------------|---------|---------|
| **Create** | POST | `POST /tasks` | Create new resource |
| **Read** | GET | `GET /tasks` or `GET /tasks/{id}` | Retrieve resources |
| **Update** | PUT/PATCH | `PUT /tasks/{id}` | Update existing resource |
| **Delete** | DELETE | `DELETE /tasks/{id}` | Remove resource |

### **Method Details**

#### **GET - Retrieve Data**
```python
@app.get("/tasks")
async def get_all_tasks():
    """Get all tasks - READ operation"""
    return tasks

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """Get specific task - READ operation"""
    return task
```

**Characteristics:**
- ✅ Safe (doesn't modify data)
- ✅ Idempotent (same result every time)
- ✅ Can be cached
- ✅ Should not have request body

#### **POST - Create New Resources**
```python
@app.post("/tasks", status_code=201)
async def create_task(task: TaskCreate):
    """Create new task - CREATE operation"""
    new_task = Task(id=generate_id(), **task.dict())
    tasks.append(new_task)
    return new_task
```

**Characteristics:**
- ❌ Not safe (modifies data)
- ❌ Not idempotent (creates new resource each time)
- ✅ Requires request body
- ✅ Returns 201 Created on success

#### **PUT - Replace Entire Resource**
```python
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    """Replace entire task - UPDATE operation"""
    tasks[task_id] = Task(id=task_id, **task.dict())
    return tasks[task_id]
```

**Characteristics:**
- ❌ Not safe (modifies data)
- ✅ Idempotent (same result when repeated)
- ✅ Requires complete resource in body
- ✅ Returns 200 OK with updated resource

#### **PATCH - Partial Update**
```python
@app.patch("/tasks/{task_id}")
async def partial_update(task_id: int, updates: TaskPartial):
    """Update specific fields - PARTIAL UPDATE operation"""
    task = tasks[task_id]
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    return task
```

**Characteristics:**
- ❌ Not safe (modifies data)
- ✅ Idempotent
- ✅ Only requires fields being updated
- ✅ Returns 200 OK with updated resource

#### **DELETE - Remove Resource**
```python
@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    """Delete task - DELETE operation"""
    del tasks[task_id]
    return None  # 204 No Content
```

**Characteristics:**
- ❌ Not safe (modifies data)
- ✅ Idempotent (deleting twice has same result)
- ❌ No request body
- ✅ Returns 204 No Content (or 200 with message)

## 📝 Complete CRUD Example

Let's build a Task Manager API demonstrating all operations:

### **1. Define Data Models**

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    """Base task model with common fields"""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    completed: bool = False
    priority: int = Field(default=3, ge=1, le=5)

class TaskCreate(TaskBase):
    """Model for creating tasks (no ID needed)"""
    pass

class TaskUpdate(TaskBase):
    """Model for full updates"""
    pass

class TaskPartial(BaseModel):
    """Model for partial updates (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class Task(TaskBase):
    """Complete task model with ID and metadata"""
    id: int
    created_at: datetime
    updated_at: datetime
```

### **2. Implement CRUD Operations**

```python
from fastapi import FastAPI, HTTPException, status
from typing import List

app = FastAPI(title="Task Manager API")

# In-memory storage (temporary, until we learn databases)
tasks: dict[int, Task] = {}
next_id = 1

# CREATE - Add new task
@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """
    Create a new task.

    - **title**: Task title (required, 1-100 characters)
    - **description**: Optional task description
    - **completed**: Task completion status (default: False)
    - **priority**: Task priority 1-5 (default: 3)
    """
    global next_id

    now = datetime.now()
    new_task = Task(
        id=next_id,
        **task_data.dict(),
        created_at=now,
        updated_at=now
    )

    tasks[next_id] = new_task
    next_id += 1

    return new_task

# READ - Get all tasks
@app.get("/tasks", response_model=List[Task])
async def get_tasks(
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all tasks with optional filtering.

    - **completed**: Filter by completion status
    - **priority**: Filter by priority level
    - **skip**: Number of tasks to skip (pagination)
    - **limit**: Maximum tasks to return (pagination)
    """
    result = list(tasks.values())

    # Apply filters
    if completed is not None:
        result = [t for t in result if t.completed == completed]
    if priority is not None:
        result = [t for t in result if t.priority == priority]

    # Apply pagination
    return result[skip : skip + limit]

# READ - Get single task
@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: int):
    """
    Retrieve a specific task by ID.

    Raises 404 if task not found.
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return tasks[task_id]

# UPDATE - Replace entire task
@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_data: TaskUpdate):
    """
    Update an entire task (all fields required).

    This replaces the task completely with new data.
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    # Preserve ID and created_at, update everything else
    updated_task = Task(
        id=task_id,
        **task_data.dict(),
        created_at=tasks[task_id].created_at,
        updated_at=datetime.now()
    )

    tasks[task_id] = updated_task
    return updated_task

# UPDATE - Partial update
@app.patch("/tasks/{task_id}", response_model=Task)
async def partial_update_task(task_id: int, updates: TaskPartial):
    """
    Partially update a task (only specified fields).

    Send only the fields you want to change.
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    task = tasks[task_id]

    # Update only provided fields
    update_data = updates.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.now()

    return task

# DELETE - Remove task
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    """
    Delete a task by ID.

    Returns 204 No Content on success.
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    del tasks[task_id]
    return None
```

## 🧪 Testing CRUD Operations

### **Using the Interactive Docs** (`/docs`)

1. **Create a Task (POST)**
   ```json
   POST /tasks
   {
     "title": "Learn FastAPI",
     "description": "Complete CRUD tutorial",
     "priority": 5
   }
   ```

2. **Get All Tasks (GET)**
   ```
   GET /tasks
   ```

3. **Get Specific Task (GET)**
   ```
   GET /tasks/1
   ```

4. **Update Task (PUT)**
   ```json
   PUT /tasks/1
   {
     "title": "Master FastAPI",
     "description": "Complete all tutorials",
     "completed": false,
     "priority": 5
   }
   ```

5. **Partial Update (PATCH)**
   ```json
   PATCH /tasks/1
   {
     "completed": true
   }
   ```

6. **Delete Task (DELETE)**
   ```
   DELETE /tasks/1
   ```

### **Using cURL**

```bash
# Create
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "My Task", "priority": 4}'

# Read all
curl http://localhost:8000/tasks

# Read one
curl http://localhost:8000/tasks/1

# Update
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated", "description": "Changed", "completed": true, "priority": 5}'

# Partial update
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete
curl -X DELETE http://localhost:8000/tasks/1
```

## 🎯 HTTP Status Codes

Use the right status code for each operation:

### **Success Codes**
- **200 OK** - Successful GET, PUT, PATCH
- **201 Created** - Successful POST (resource created)
- **204 No Content** - Successful DELETE (no response body)

### **Client Error Codes**
- **400 Bad Request** - Invalid data sent by client
- **404 Not Found** - Resource doesn't exist
- **409 Conflict** - Conflict with current state (e.g., duplicate)
- **422 Unprocessable Entity** - Validation error (FastAPI default)

### **Server Error Codes**
- **500 Internal Server Error** - Something went wrong on server

### **Example Implementation**

```python
from fastapi import status

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    # Returns 201 on success
    pass

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    # Returns 204 on success
    pass

@app.get("/tasks/{id}")
async def get_task(id: int):
    if id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return tasks[id]  # Returns 200 on success
```

## 🔍 Common CRUD Patterns

### **Pattern 1: Pagination**
```python
@app.get("/items")
async def get_items(skip: int = 0, limit: int = 10):
    return items[skip : skip + limit]
```

### **Pattern 2: Filtering**
```python
@app.get("/tasks")
async def get_tasks(
    completed: Optional[bool] = None,
    priority: Optional[int] = None
):
    result = tasks
    if completed is not None:
        result = [t for t in result if t.completed == completed]
    if priority is not None:
        result = [t for t in result if t.priority == priority]
    return result
```

### **Pattern 3: Search**
```python
@app.get("/tasks/search")
async def search_tasks(q: str):
    return [
        task for task in tasks
        if q.lower() in task.title.lower()
        or (task.description and q.lower() in task.description.lower())
    ]
```

### **Pattern 4: Bulk Operations**
```python
@app.post("/tasks/bulk")
async def create_bulk_tasks(tasks: List[TaskCreate]):
    created = []
    for task_data in tasks:
        # Create each task
        created.append(create_single_task(task_data))
    return created
```

## 🎯 Practice Challenges

### **Challenge 1: Notes API**
Create a complete CRUD API for notes:
- `POST /notes` - Create note
- `GET /notes` - List all notes
- `GET /notes/{id}` - Get specific note
- `PUT /notes/{id}` - Update note
- `DELETE /notes/{id}` - Delete note
- Add filtering by tags

### **Challenge 2: Blog Posts API**
Build a blog posts API with:
- Create, read, update, delete posts
- Filter by published status
- Search by title or content
- Pagination support

### **Challenge 3: Status Management**
Extend the task API with:
- Mark multiple tasks as complete
- Archive old completed tasks
- Get task statistics (count by status/priority)

## ❓ Troubleshooting

**Q: When should I use PUT vs PATCH?**
A: Use PUT when you want to replace the entire resource (all fields required). Use PATCH when you want to update only specific fields.

**Q: Why does DELETE return 204 instead of 200?**
A: 204 No Content means the operation succeeded but there's no response body. It's more semantically correct for DELETE operations.

**Q: How do I handle duplicate resources?**
A: Return 409 Conflict status code if someone tries to create a resource that already exists.

**Q: Should GET requests ever modify data?**
A: No! GET should be "safe" - it should never change data. Use POST, PUT, PATCH, or DELETE for modifications.

## ➡️ What's Next?

Now that you understand CRUD operations, let's make the data persistent!

**🎯 Continue Path A - Concept Examples:**
1. **[Example 03: CRUD Basics](../../examples/03-crud-basics/)** - Practice what you just learned
2. **[Chapter 4: Database Integration](../04-database-integration/learn-database.md)** - Add real persistence
3. **[Example 04: Database Simple](../../examples/04-database-simple/)** - Database CRUD

**🏗️ Or Switch to Path B:**
Jump to **[Tutorial B3: User CRUD Operations](apply-user-crud.md)** to build user management in the e-commerce app!

---

## 📚 Summary

**What you learned:**
- ✅ HTTP methods (GET, POST, PUT, PATCH, DELETE)
- ✅ Complete CRUD operations implementation
- ✅ Request body handling with Pydantic models
- ✅ Proper HTTP status codes
- ✅ Error handling with HTTPException
- ✅ Common API patterns (pagination, filtering, search)

**Key takeaways:**
1. Use the right HTTP method for each operation
2. Return appropriate status codes (201 for create, 204 for delete)
3. Separate models for create, update, and response
4. Always validate input data with Pydantic
5. Handle errors gracefully with proper status codes

Great job! You now understand RESTful CRUD operations. 🎉

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A3*
