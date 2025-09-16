# Testing Fundamentals

**Learn comprehensive testing strategies through a Calculator API** 🧪

This example demonstrates essential testing concepts for FastAPI applications. Learn how to write unit tests, integration tests, database tests, mock external services, and implement comprehensive test coverage through a calculator and data processing API.

## 🎯 What You'll Learn

- **Unit Testing**: Test individual functions in isolation
- **Integration Testing**: Test complete API endpoints
- **Database Testing**: Test data persistence and retrieval
- **Mocking**: Replace external dependencies for isolated testing
- **Test Fixtures**: Set up and tear down test environments
- **Parametrized Tests**: Test multiple scenarios efficiently
- **Error Testing**: Validate error handling and edge cases
- **Test Coverage**: Measure and improve test completeness

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- Testing concepts: 20 minutes
- Unit tests: 25 minutes
- Integration tests: 25 minutes
- Advanced testing: 20 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]" sqlmodel pytest pytest-cov httpx
```

### Run the Example

```bash
# Navigate to this directory
cd examples/08-testing

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Run the Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=main

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run specific test file
pytest test_main.py

# Run specific test function
pytest test_main.py::TestCalculatorService::test_add_positive_numbers
```

## 📚 Key Concepts Explained

### 1. Test Categories

| Type | Purpose | Example | Isolation |
|------|---------|---------|-----------|
| **Unit** | Test individual functions | `test_add_positive_numbers()` | ✅ High |
| **Integration** | Test complete workflows | `test_add_endpoint()` | ❌ Low |
| **Database** | Test data persistence | `test_calculation_stored()` | ⚖️ Medium |
| **End-to-End** | Test user scenarios | Full user workflow | ❌ Low |

### 2. Test Structure (AAA Pattern)

```python
def test_add_positive_numbers():
    # Arrange - Set up test data
    a, b = 5, 3
    
    # Act - Perform the operation
    result = CalculatorService.add(a, b)
    
    # Assert - Verify the result
    assert result == 8
```

### 3. FastAPI Test Client

```python
from fastapi.testclient import TestClient

def test_add_endpoint(client: TestClient):
    response = client.post(
        "/calculate/basic",
        json={"operation": "add", "a": 5, "b": 3}
    )
    assert response.status_code == 200
    assert response.json()["result"] == 8
```

### 4. Database Testing with Fixtures

```python
@pytest.fixture(name="session")
def session_fixture():
    # Create in-memory test database
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
```

## 🎮 Hands-On Exercises

### Exercise 1: Run Unit Tests

1. **Run All Unit Tests**:
   ```bash
   pytest -m unit -v
   ```

2. **Run Specific Unit Test**:
   ```bash
   pytest test_main.py::TestCalculatorService::test_add_positive_numbers -v
   ```

3. **Run Calculator Tests**:
   ```bash
   pytest test_main.py::TestCalculatorService -v
   ```

4. **Run Statistics Tests**:
   ```bash
   pytest test_main.py::TestStatisticsService -v
   ```

### Exercise 2: Run Integration Tests

1. **Test API Endpoints**:
   ```bash
   pytest test_main.py::TestBasicCalculatorAPI -v
   ```

2. **Test Error Handling**:
   ```bash
   pytest test_main.py::TestErrorHandling -v
   ```

3. **Test Parametrized Operations**:
   ```bash
   pytest test_main.py::TestBasicCalculatorAPI::test_basic_operations_parametrized -v
   ```

### Exercise 3: Database Testing

1. **Test Database Operations**:
   ```bash
   pytest test_main.py::TestCalculationHistory -v
   ```

2. **Test with Sample Data**:
   ```bash
   pytest test_main.py::TestCalculationHistory::test_filter_history_by_session -v
   ```

### Exercise 4: Mocking External Services

1. **Test Weather Service**:
   ```bash
   pytest test_main.py::TestExternalServices -v
   ```

2. **Run Test with Mock**:
   ```bash
   pytest test_main.py::TestExternalServices::test_weather_service_mocked_response -v
   ```

### Exercise 5: Coverage Analysis

1. **Generate Coverage Report**:
   ```bash
   pytest --cov=main --cov-report=html
   ```

2. **View Coverage Report**:
   ```bash
   # Open htmlcov/index.html in your browser
   open htmlcov/index.html  # macOS
   # or navigate to the file in your browser
   ```

3. **Coverage with Missing Lines**:
   ```bash
   pytest --cov=main --cov-report=term-missing
   ```

## 🔍 Code Structure Walkthrough

### 1. Test Organization

```
examples/08-testing/
├── main.py              # Application code
├── test_main.py         # Comprehensive test suite
├── pytest.ini          # Pytest configuration
└── htmlcov/            # Coverage reports (generated)
```

### 2. Test Fixtures

```python
@pytest.fixture(name="session")
def session_fixture():
    """Create isolated test database for each test."""
    # In-memory database ensures test isolation

@pytest.fixture(name="client") 
def client_fixture(session):
    """FastAPI test client with dependency override."""
    app.dependency_overrides[get_session] = lambda: session
    return TestClient(app)

@pytest.fixture
def sample_calculations(session):
    """Pre-populate database with test data."""
    # Create and return test data
```

### 3. Parametrized Testing

```python
@pytest.mark.parametrize("operation,a,b,expected", [
    ("add", 10, 5, 15),
    ("subtract", 10, 5, 5),
    ("multiply", 10, 5, 50),
    ("divide", 10, 5, 2),
])
def test_basic_operations_parametrized(client, operation, a, b, expected):
    # Single test function tests multiple scenarios
```

### 4. Mocking External Dependencies

```python
@patch.object(WeatherService, 'get_temperature')
def test_weather_service_mocked(mock_temp, client):
    mock_temp.return_value = 25.5
    
    response = client.get("/external/weather/TestCity")
    assert response.json()["temperature_celsius"] == 25.5
```

## 🧪 Testing Patterns Demonstrated

### 1. **Unit Testing Business Logic**

```python
class TestCalculatorService:
    def test_add_positive_numbers(self):
        result = CalculatorService.add(5, 3)
        assert result == 8
    
    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Division by zero"):
            CalculatorService.divide(5, 0)
```

### 2. **Integration Testing API Endpoints**

```python
class TestBasicCalculatorAPI:
    def test_add_endpoint(self, client):
        response = client.post("/calculate/basic", json={
            "operation": "add", "a": 5, "b": 3
        })
        assert response.status_code == 200
        assert response.json()["result"] == 8
```

### 3. **Database Testing**

```python
class TestCalculationHistory:
    def test_calculation_stored_in_database(self, client, session):
        # Make API call
        client.post("/calculate/basic", json={"operation": "add", "a": 10, "b": 5})
        
        # Verify database storage
        calculations = session.exec(select(Calculation)).all()
        assert len(calculations) == 1
        assert calculations[0].result == 15
```

### 4. **Error Testing**

```python
class TestErrorHandling:
    def test_malformed_json(self, client):
        response = client.post(
            "/calculate/basic",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        response = client.post("/calculate/basic", json={"operation": "add", "a": 5})
        assert response.status_code == 422
```

## 🎯 Test Categories by Complexity

### 1. **Basic Unit Tests** (Fast, Isolated)

```python
# Test pure functions
def test_add():
    assert CalculatorService.add(2, 3) == 5

def test_mean():
    assert StatisticsService.mean([1, 2, 3]) == 2
```

### 2. **API Integration Tests** (Medium, HTTP)

```python
# Test complete request/response cycle
def test_calculate_endpoint(client):
    response = client.post("/calculate/basic", json={...})
    assert response.status_code == 200
```

### 3. **Database Integration Tests** (Slower, I/O)

```python
# Test data persistence
def test_calculation_history(client, session):
    # Test database reads/writes
```

### 4. **External Service Tests** (Mock dependencies)

```python
# Test with mocked external services
@patch.object(WeatherService, 'get_temperature')
def test_weather_endpoint(mock_service, client):
    # Test external integration
```

## 🧪 Testing Your Understanding

### Challenge 1: Add New Calculator Function
1. Add a `factorial` function to `CalculatorService`
2. Write unit tests for edge cases (0!, 1!, negative numbers)
3. Create API endpoint for factorial
4. Write integration tests for the endpoint

### Challenge 2: Improve Error Testing
1. Add custom exception classes
2. Test specific exception types and messages
3. Add input validation testing
4. Test boundary conditions

### Challenge 3: Advanced Mocking
1. Mock database failures
2. Mock network timeouts
3. Create test doubles for complex scenarios
4. Test retry mechanisms

### Challenge 4: Performance Testing
1. Add timing tests for operations
2. Test with large datasets
3. Memory usage testing
4. Load testing with multiple concurrent requests

## 🔗 What's Next?

After mastering testing fundamentals:

1. **Advanced Testing** - Property-based testing, mutation testing
2. **Test Automation** - CI/CD integration, automated test runs
3. **Performance Testing** - Load testing, stress testing
4. **Security Testing** - Authentication testing, input validation
5. **Production Monitoring** - Health checks, observability

## 💡 Key Takeaways

- **Test pyramid**: More unit tests, fewer integration tests
- **Test isolation**: Each test should be independent
- **Fast feedback**: Unit tests should run quickly
- **Comprehensive coverage**: Test happy paths and error cases
- **Mock external dependencies**: Isolate system under test
- **Readable tests**: Tests serve as documentation

## 🐛 Common Testing Pitfalls

1. **Testing implementation details**: Test behavior, not internal structure
2. **Brittle tests**: Tests that break with minor code changes
3. **Slow test suite**: Too many integration tests, not enough unit tests
4. **Poor test names**: Names should describe what's being tested
5. **Missing edge cases**: Not testing boundary conditions
6. **Flaky tests**: Tests that pass/fail randomly

## 🔧 Testing Best Practices

### Writing Good Tests

```python
# Good: Descriptive name, clear test case
def test_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError, match="Division by zero"):
        CalculatorService.divide(10, 0)

# Bad: Unclear name, testing multiple things
def test_calculator():
    assert CalculatorService.add(1, 2) == 3
    assert CalculatorService.divide(10, 0)  # This will fail
```

### Test Organization

```python
class TestCalculatorService:
    """Group related tests together."""
    
    class TestBasicOperations:
        """Nest test classes for better organization."""
        
        def test_addition(self):
            pass
        
        def test_subtraction(self):
            pass
```

### Test Data Management

```python
# Use factories for test data
def create_calculation(operation="add", result=10.0):
    return Calculation(
        operation=operation,
        operands='{"a": 5, "b": 5}',
        result=result,
        operation_type=OperationType.BASIC
    )

# Use fixtures for shared setup
@pytest.fixture
def sample_calculation():
    return create_calculation()
```

### Assertion Best Practices

```python
# Good: Specific assertions
assert response.status_code == 200
assert response.json()["result"] == 8
assert "calculation_id" in response.json()

# Bad: Generic assertions
assert response  # What are we actually testing?
assert response.json()  # Could pass with any non-empty response
```

## 📊 Test Coverage Guidelines

### Coverage Targets
- **Unit Tests**: Aim for 90%+ line coverage
- **Integration Tests**: Focus on critical paths
- **End-to-End Tests**: Cover main user workflows

### What to Test
- ✅ **Business logic functions**
- ✅ **API endpoints (happy path)**
- ✅ **Error conditions**
- ✅ **Edge cases and boundaries**
- ✅ **Data validation**

### What NOT to Test
- ❌ **Third-party library code**
- ❌ **Simple getters/setters**
- ❌ **Configuration values**
- ❌ **Database ORM generated code**

---

**Congratulations!** You've completed all Tutorial A examples. **Ready for production? Explore deployment strategies and advanced topics!** 🚀