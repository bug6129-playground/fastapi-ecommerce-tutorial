"""
CRUD Operations Fundamentals - Task Manager API
===============================================

This example demonstrates essential CRUD (Create, Read, Update, Delete) operations
using FastAPI with in-memory storage. Perfect for understanding HTTP methods and
basic API patterns before moving to database integration.

Key Concepts Demonstrated:
- HTTP methods: GET, POST, PUT, DELETE
- Path parameters and request bodies
- Response status codes
- Error handling
- In-memory data storage
- List operations and filtering

Author: bug6129
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="CRUD Fundamentals - Task Manager",
    description="Learn CRUD operations through a simple task management API",
    version="1.0.0"
)

# =============================================================================
# 1. DATA MODELS - Defining Our Task Structure
# =============================================================================

class TaskStatus(str, Enum):
    """Task status enumeration for type safety."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskBase(BaseModel):
    """Base task model with shared fields."""
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Task description", max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Current task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")

class TaskCreate(TaskBase):
    """Model for creating new tasks."""
    pass

class TaskUpdate(BaseModel):
    """Model for updating existing tasks (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None

class Task(TaskBase):
    """Complete task model with ID and timestamps."""
    id: int = Field(..., description="Unique task identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Learn FastAPI CRUD operations",
                "description": "Complete the tutorial on basic CRUD operations",
                "status": "todo",
                "priority": "high",
                "due_date": "2024-12-31T23:59:59",
                "created_at": "2024-01-15T10:00:00",
                "updated_at": "2024-01-15T10:00:00"
            }
        }

# =============================================================================
# 2. IN-MEMORY STORAGE - Simple Data Store
# =============================================================================

# In-memory task storage (in production, you'd use a database)
tasks_db: List[Task] = []
next_task_id = 1

# Sample data for demonstration
def create_sample_tasks():
    """Create some sample tasks for demonstration."""
    global next_task_id
    
    sample_tasks = [
        TaskCreate(
            title="Set up development environment",
            description="Install Python, FastAPI, and set up project structure",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH
        ),
        TaskCreate(
            title="Learn Pydantic models",
            description="Understand data validation and serialization",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM
        ),
        TaskCreate(
            title="Master CRUD operations",
            description="Implement Create, Read, Update, Delete functionality",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=datetime(2024, 12, 31, 23, 59, 59)
        ),
        TaskCreate(
            title="Add database integration",
            description="Replace in-memory storage with SQLModel database",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM
        ),
        TaskCreate(
            title="Write unit tests",
            description="Create comprehensive test suite for the API",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW
        )
    ]
    
    for task_data in sample_tasks:
        task = Task(
            id=next_task_id,
            **task_data.dict(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        tasks_db.append(task)
        next_task_id += 1

# Initialize with sample data
create_sample_tasks()

# =============================================================================
# 3. HELPER FUNCTIONS - Utility Functions
# =============================================================================

def find_task_by_id(task_id: int) -> Optional[Task]:
    """Find a task by its ID."""
    return next((task for task in tasks_db if task.id == task_id), None)

def get_task_index(task_id: int) -> int:
    """Get the index of a task in the tasks list."""
    for i, task in enumerate(tasks_db):
        if task.id == task_id:
            return i
    return -1

# =============================================================================
# 4. API ENDPOINTS - CRUD Operations
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API information and available endpoints."""
    return {
        "message": "Task Manager API - CRUD Fundamentals",
        "description": "Learn CRUD operations through task management",
        "endpoints": {
            "GET /tasks": "List all tasks (with optional filtering)",
            "POST /tasks": "Create a new task",
            "GET /tasks/{id}": "Get a specific task by ID",
            "PUT /tasks/{id}": "Update a task completely",
            "PATCH /tasks/{id}": "Update specific task fields",
            "DELETE /tasks/{id}": "Delete a task"
        },
        "total_tasks": len(tasks_db),
        "documentation": "/docs"
    }

# =============================================================================
# READ OPERATIONS - Getting Data
# =============================================================================

@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def get_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks to return"),
    skip: int = Query(0, ge=0, description="Number of tasks to skip")
):
    """
    Get all tasks with optional filtering and pagination.
    
    This endpoint demonstrates:
    - Query parameters for filtering
    - Pagination with limit and skip
    - List operations
    - Optional filtering logic
    """
    filtered_tasks = tasks_db
    
    # Apply status filter
    if status:
        filtered_tasks = [task for task in filtered_tasks if task.status == status]
    
    # Apply priority filter
    if priority:
        filtered_tasks = [task for task in filtered_tasks if task.priority == priority]
    
    # Apply pagination
    paginated_tasks = filtered_tasks[skip:skip + limit]
    
    return paginated_tasks

@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(task_id: int):
    """
    Get a specific task by its ID.
    
    This endpoint demonstrates:
    - Path parameters
    - Single item retrieval
    - 404 error handling
    """
    task = find_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    return task

# =============================================================================
# CREATE OPERATIONS - Adding New Data
# =============================================================================

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task_data: TaskCreate):
    """
    Create a new task.
    
    This endpoint demonstrates:
    - POST method for creation
    - Request body validation
    - Auto-generated IDs
    - 201 Created status code
    - Timestamps
    """
    global next_task_id
    
    # Create new task with auto-generated ID and timestamps
    new_task = Task(
        id=next_task_id,
        **task_data.dict(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Add to storage
    tasks_db.append(new_task)
    next_task_id += 1
    
    return new_task

# =============================================================================
# UPDATE OPERATIONS - Modifying Existing Data
# =============================================================================

@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task_complete(task_id: int, task_data: TaskCreate):
    """
    Completely update a task (replaces all fields).
    
    This endpoint demonstrates:
    - PUT method for complete updates
    - Path parameters with request body
    - Complete resource replacement
    - Updated timestamps
    """
    task_index = get_task_index(task_id)
    if task_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    # Get the existing task to preserve ID and created_at
    existing_task = tasks_db[task_index]
    
    # Create updated task (complete replacement)
    updated_task = Task(
        id=existing_task.id,
        **task_data.dict(),
        created_at=existing_task.created_at,
        updated_at=datetime.now()
    )
    
    # Replace in storage
    tasks_db[task_index] = updated_task
    
    return updated_task

@app.patch("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task_partial(task_id: int, task_data: TaskUpdate):
    """
    Partially update a task (only provided fields).
    
    This endpoint demonstrates:
    - PATCH method for partial updates
    - Optional field updates
    - Preserving unchanged fields
    - Conditional field updates
    """
    task_index = get_task_index(task_id)
    if task_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    existing_task = tasks_db[task_index]
    
    # Update only provided fields
    update_data = task_data.dict(exclude_unset=True)
    
    # Create updated task preserving unchanged fields
    updated_task = existing_task.copy(update={
        **update_data,
        "updated_at": datetime.now()
    })
    
    # Replace in storage
    tasks_db[task_index] = updated_task
    
    return updated_task

# =============================================================================
# DELETE OPERATIONS - Removing Data
# =============================================================================

@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: int):
    """
    Delete a task.
    
    This endpoint demonstrates:
    - DELETE method
    - Resource removal
    - Success confirmation
    - 404 handling for non-existent resources
    """
    task_index = get_task_index(task_id)
    if task_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    # Remove from storage
    deleted_task = tasks_db.pop(task_index)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Task '{deleted_task.title}' has been deleted successfully",
            "deleted_task_id": task_id
        }
    )

# =============================================================================
# ADDITIONAL ENDPOINTS - Bonus Features
# =============================================================================

@app.get("/tasks/status/{status}", response_model=List[Task], tags=["Tasks"])
async def get_tasks_by_status(status: TaskStatus):
    """
    Get all tasks with a specific status.
    
    Alternative endpoint design for status filtering.
    """
    filtered_tasks = [task for task in tasks_db if task.status == status]
    return filtered_tasks

@app.patch("/tasks/{task_id}/status", response_model=Task, tags=["Tasks"])
async def update_task_status(task_id: int, new_status: TaskStatus):
    """
    Update only the status of a task.
    
    Demonstrates specific field update endpoint.
    """
    task_index = get_task_index(task_id)
    if task_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    existing_task = tasks_db[task_index]
    updated_task = existing_task.copy(update={
        "status": new_status,
        "updated_at": datetime.now()
    })
    
    tasks_db[task_index] = updated_task
    return updated_task

@app.get("/tasks/stats", tags=["Statistics"])
async def get_task_statistics():
    """
    Get task statistics.
    
    Demonstrates data aggregation and analysis.
    """
    total_tasks = len(tasks_db)
    
    if total_tasks == 0:
        return {"message": "No tasks found"}
    
    # Count by status
    status_counts = {}
    for status in TaskStatus:
        status_counts[status.value] = len([t for t in tasks_db if t.status == status])
    
    # Count by priority
    priority_counts = {}
    for priority in TaskPriority:
        priority_counts[priority.value] = len([t for t in tasks_db if t.priority == priority])
    
    # Find overdue tasks
    now = datetime.now()
    overdue_tasks = [
        t for t in tasks_db 
        if t.due_date and t.due_date < now and t.status != TaskStatus.COMPLETED
    ]
    
    return {
        "total_tasks": total_tasks,
        "status_breakdown": status_counts,
        "priority_breakdown": priority_counts,
        "overdue_tasks": len(overdue_tasks),
        "completion_rate": round(
            (status_counts.get("completed", 0) / total_tasks) * 100, 2
        ) if total_tasks > 0 else 0
    }

@app.delete("/tasks", tags=["Tasks"])
async def delete_all_tasks():
    """
    Delete all tasks (bulk operation).
    
    Demonstrates bulk operations and confirmation.
    """
    deleted_count = len(tasks_db)
    tasks_db.clear()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"All {deleted_count} tasks have been deleted",
            "deleted_count": deleted_count
        }
    )

@app.post("/tasks/reset", tags=["Tasks"])
async def reset_tasks():
    """
    Reset to sample data.
    
    Useful for testing and demonstrations.
    """
    global next_task_id
    tasks_db.clear()
    next_task_id = 1
    create_sample_tasks()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Tasks reset to sample data",
            "total_tasks": len(tasks_db)
        }
    )

# Health check
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Task Manager API - CRUD Fundamentals",
        "total_tasks": len(tasks_db),
        "timestamp": datetime.now()
    }

# Main execution
if __name__ == "__main__":
    import uvicorn
    print("🚀 CRUD Fundamentals - Task Manager API")
    print("=" * 50)
    print("This tutorial demonstrates CRUD operations through task management.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Tasks: http://localhost:8000/tasks")
    print("   • Stats: http://localhost:8000/tasks/stats")
    print("")
    print("📚 What you'll learn:")
    print("   • GET - Reading data (with filtering and pagination)")
    print("   • POST - Creating new resources")
    print("   • PUT - Complete resource updates")
    print("   • PATCH - Partial resource updates")
    print("   • DELETE - Removing resources")
    print("   • Error handling and status codes")
    print("   • Query parameters and path parameters")
    print("")
    print("🎯 Try these operations:")
    print("   1. GET /tasks - See all tasks")
    print("   2. POST /tasks - Create a new task")
    print("   3. PUT /tasks/1 - Update task completely")
    print("   4. PATCH /tasks/1 - Update task partially")
    print("   5. DELETE /tasks/1 - Delete a task")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)