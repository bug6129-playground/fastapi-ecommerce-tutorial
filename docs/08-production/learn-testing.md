# Tutorial A8: Testing FastAPI Applications

**Write comprehensive tests for reliable APIs** 🧪

In this tutorial, you'll learn how to test your FastAPI applications thoroughly using pytest. Testing ensures your API works correctly, prevents regressions, and gives you confidence when making changes.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ Why testing is crucial for APIs
- ✅ Setting up pytest for FastAPI testing
- ✅ Testing API endpoints with TestClient
- ✅ Testing database operations
- ✅ Testing authentication and authorization
- ✅ Test fixtures and setup/teardown
- ✅ Test coverage and best practices

## 🧠 Why Test Your API?

### **Benefits of Testing**

1. **🐛 Catch Bugs Early** - Find issues before users do
2. **🔒 Prevent Regressions** - Ensure fixes stay fixed
3. **📖 Living Documentation** - Tests show how API should work
4. **🚀 Confidence to Refactor** - Change code without fear
5. **⚡ Faster Development** - Catch issues immediately

### **Types of Tests**

```
Unit Tests ────> Integration Tests ────> End-to-End Tests
   (Fast)           (Medium)                 (Slow)
 Test one         Test multiple          Test entire
 function         components              workflow
```

## 🔧 Testing Setup

### **1. Install Dependencies**

```bash
pip install pytest pytest-asyncio httpx
```

### **2. Project Structure**

```
your_project/
├── app/
│   ├── main.py
│   ├── models.py
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Test configuration and fixtures
│   ├── test_main.py     # Test main endpoints
│   ├── test_auth.py     # Test authentication
│   └── test_database.py # Test database operations
└── pytest.ini           # pytest configuration
```

### **3. pytest.ini Configuration**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Show print statements
addopts = -v -s
```

## 📝 Basic Testing

### **1. Simple Endpoint Test**

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Your app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

# Tests
client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_read_item():
    """Test item endpoint"""
    response = client.get("/items/42")

    assert response.status_code == 200
    assert response.json() == {"item_id": 42}

def test_item_not_found():
    """Test 404 error"""
    response = client.get("/items/invalid")

    assert response.status_code == 422  # Validation error for invalid type
```

### **2. Testing POST Requests**

```python
@app.post("/items")
def create_item(name: str, price: float):
    return {"name": name, "price": price}

def test_create_item():
    """Test creating an item"""
    response = client.post(
        "/items",
        params={"name": "Test Item", "price": 29.99}
    )

    assert response.status_code == 200
    assert response.json() == {"name": "Test Item", "price": 29.99}

def test_create_item_with_json_body():
    """Test with JSON body"""
    response = client.post(
        "/items",
        json={"name": "Item", "price": 19.99}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Item"
    assert data["price"] == 19.99
```

## 🧪 Testing with Database

### **1. Test Database Setup**

```python
# conftest.py - Shared fixtures
import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database for each test"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Clean up (optional, memory database is deleted anyway)
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create TestClient with test database"""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
```

### **2. Testing Database Operations**

```python
# test_database.py
from app.models import Task

def test_create_task(client):
    """Test creating a task"""
    response = client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "completed": False
        }
    )

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["id"] is not None

def test_get_tasks(client, session):
    """Test getting all tasks"""
    # Create some test data
    task1 = Task(title="Task 1", description="Desc 1")
    task2 = Task(title="Task 2", description="Desc 2")
    session.add(task1)
    session.add(task2)
    session.commit()

    # Test endpoint
    response = client.get("/tasks")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_task_by_id(client, session):
    """Test getting a specific task"""
    # Create test data
    task = Task(title="Specific Task", description="Find me")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Test endpoint
    response = client.get(f"/tasks/{task.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Specific Task"

def test_update_task(client, session):
    """Test updating a task"""
    # Create test data
    task = Task(title="Old Title", description="Old desc")
    session.add(task)
    session.commit()
    session.refresh(task)

    # Update
    response = client.patch(
        f"/tasks/{task.id}",
        json={"title": "New Title"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Old desc"  # Unchanged

def test_delete_task(client, session):
    """Test deleting a task"""
    # Create test data
    task = Task(title="To Delete", description="Bye")
    session.add(task)
    session.commit()
    session.refresh(task)

    task_id = task.id

    # Delete
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify deleted
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
```

## 🔒 Testing Authentication

```python
# test_auth.py
from app.auth import create_access_token

def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "hashed_password" not in data  # Don't expose password!

def test_register_duplicate_username(client, session):
    """Test registering with existing username"""
    # Create first user
    client.post(
        "/register",
        json={
            "username": "duplicate",
            "email": "user1@example.com",
            "password": "pass123"
        }
    )

    # Try to create duplicate
    response = client.post(
        "/register",
        json={
            "username": "duplicate",
            "email": "user2@example.com",
            "password": "pass456"
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client):
    """Test successful login"""
    # Register user
    client.post(
        "/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "loginpass123"
        }
    )

    # Login
    response = client.post(
        "/token",
        data={  # OAuth2 uses form data, not JSON
            "username": "loginuser",
            "password": "loginpass123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """Test login with wrong password"""
    # Register user
    client.post(
        "/register",
        json={
            "username": "user",
            "email": "user@example.com",
            "password": "correctpass"
        }
    )

    # Try wrong password
    response = client.post(
        "/token",
        data={
            "username": "user",
            "password": "wrongpass"
        }
    )

    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without authentication"""
    response = client.get("/users/me")

    assert response.status_code == 401

def test_protected_endpoint_with_token(client):
    """Test accessing protected endpoint with valid token"""
    # Register and login
    client.post(
        "/register",
        json={
            "username": "protected",
            "email": "protected@example.com",
            "password": "pass123"
        }
    )

    login_response = client.post(
        "/token",
        data={"username": "protected", "password": "pass123"}
    )

    token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "protected"

def test_admin_endpoint_requires_admin(client):
    """Test that admin endpoints require admin role"""
    # Register regular user
    client.post(
        "/register",
        json={
            "username": "regular",
            "email": "regular@example.com",
            "password": "pass123"
        }
    )

    # Login
    login_response = client.post(
        "/token",
        data={"username": "regular", "password": "pass123"}
    )

    token = login_response.json()["access_token"]

    # Try to access admin endpoint
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403  # Forbidden
```

## 🎯 Advanced Testing Patterns

### **1. Parametrized Tests**

```python
import pytest

@pytest.mark.parametrize("item_id,expected_status", [
    (1, 200),
    (2, 200),
    (999, 404),
    (-1, 422),
])
def test_get_item_various_ids(client, item_id, expected_status):
    """Test get item with different IDs"""
    response = client.get(f"/items/{item_id}")
    assert response.status_code == expected_status
```

### **2. Testing Edge Cases**

```python
def test_empty_title_rejected(client):
    """Test that empty title is rejected"""
    response = client.post(
        "/tasks",
        json={"title": "", "description": "Desc"}
    )

    assert response.status_code == 422  # Validation error

def test_very_long_title_rejected(client):
    """Test that overly long title is rejected"""
    response = client.post(
        "/tasks",
        json={"title": "x" * 1000, "description": "Desc"}
    )

    assert response.status_code == 422

def test_special_characters_in_title(client):
    """Test special characters are handled"""
    response = client.post(
        "/tasks",
        json={
            "title": "Test & <Special> Characters",
            "description": "Contains: !@#$%"
        }
    )

    assert response.status_code == 201
```

### **3. Fixtures for Common Data**

```python
@pytest.fixture
def sample_user(session):
    """Create a sample user for tests"""
    from app.models import User
    from app.auth import hash_password

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, sample_user):
    """Get authentication headers"""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_with_auth_headers(client, auth_headers):
    """Test using auth_headers fixture"""
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
```

## 📊 Running Tests

### **Basic Commands**

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run only failed tests from last run
pytest --lf
```

### **Test Coverage**

```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## ✅ Testing Best Practices

### **1. Arrange-Act-Assert Pattern**

```python
def test_create_task(client):
    # Arrange - Set up test data
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }

    # Act - Perform the action
    response = client.post("/tasks", json=task_data)

    # Assert - Check the results
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

### **2. One Assert Per Test (Guideline)**

```python
# Good - Clear what failed
def test_task_has_title(client):
    response = client.get("/tasks/1")
    assert response.json()["title"] == "Expected Title"

def test_task_has_description(client):
    response = client.get("/tasks/1")
    assert response.json()["description"] == "Expected Description"

# Acceptable - Related asserts
def test_create_task_response(client):
    response = client.post("/tasks", json={"title": "Task"})
    assert response.status_code == 201
    assert "id" in response.json()  # Related to same response
```

### **3. Use Descriptive Test Names**

```python
# Good
def test_user_cannot_delete_other_users_tasks():
    pass

def test_expired_token_returns_401_unauthorized():
    pass

# Bad
def test_delete():
    pass

def test_token():
    pass
```

### **4. Test Isolation**

```python
# Each test should be independent
def test_a(client, session):
    # This test shouldn't affect test_b
    task = Task(title="Task A")
    session.add(task)
    session.commit()

def test_b(client, session):
    # This test gets fresh database
    # (because of session fixture)
    tasks = session.exec(select(Task)).all()
    assert len(tasks) == 0  # Clean database
```

## 🎯 Practice Challenges

### **Challenge 1: Comprehensive Task API Tests**
Write tests for:
- Creating tasks with all field combinations
- Updating partial fields
- Filtering tasks by status
- Pagination
- Invalid input handling

### **Challenge 2: Authentication Test Suite**
Create tests for:
- Password requirements validation
- Token expiration
- Refresh token flow
- Role-based access control

### **Challenge 3: Integration Tests**
Build end-to-end tests for:
- User registration → login → create post → add comment
- Admin creates product → User adds to cart → Creates order
- User uploads file → File is retrievable → File can be deleted

## ❓ Troubleshooting

**Q: Tests fail but API works in browser?**
A: Check that test database is properly set up. Use `pytest -s` to see print statements.

**Q: Tests are slow!**
A: Use in-memory SQLite for tests, not real database. Consider pytest-xdist for parallel execution.

**Q: How do I test async endpoints?**
A: Use `pytest-asyncio` and mark tests with `@pytest.mark.asyncio`.

**Q: Database state persists between tests!**
A: Ensure your session fixture creates a fresh database for each test.

## ➡️ Congratulations! 🎉

You've completed all 8 chapters of **Path A: FastAPI Concepts**!

### **What You've Learned:**
1. ✅ FastAPI Basics
2. ✅ Data Validation with Pydantic
3. ✅ CRUD Operations
4. ✅ Database Integration
5. ✅ File Uploads & Search
6. ✅ Data Relationships
7. ✅ Authentication & Security
8. ✅ Testing

### **What's Next?**

**🏗️ Build a Real Project - Path B:**
Apply everything you learned by building a complete e-commerce API!
Start with **[Tutorial B1: E-Commerce Foundation](../01-getting-started/apply-ecommerce.md)**

**🚀 Or Continue Learning:**
- Deploy your APIs to the cloud
- Add advanced features (caching, queues, websockets)
- Explore microservices architecture
- Build a frontend for your API

**💼 Show Off Your Skills:**
- Build portfolio projects
- Contribute to open source
- Share your knowledge with others

---

## 📚 Summary

**What you learned:**
- ✅ Testing fundamentals and benefits
- ✅ pytest setup and configuration
- ✅ Testing API endpoints with TestClient
- ✅ Database testing with fixtures
- ✅ Authentication testing
- ✅ Test coverage and best practices

**Key takeaways:**
1. Write tests as you develop, not after
2. Use fixtures for common setup code
3. Test both success and failure cases
4. Aim for high test coverage (>80%)
5. Keep tests fast and isolated

Excellent work! You now know how to build production-ready APIs with FastAPI. 🎉🚀

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A8*
