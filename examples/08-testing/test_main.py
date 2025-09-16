"""
Comprehensive Test Suite - Calculator API Testing
=================================================

This file demonstrates various testing strategies for FastAPI applications.
It covers unit tests, integration tests, database testing, mocking,
and error handling validation.

Testing Categories:
- Unit Tests: Test individual functions in isolation
- Integration Tests: Test complete API endpoints
- Database Tests: Test data persistence and retrieval
- External Service Tests: Test mocking and external dependencies
- Error Handling Tests: Test various error scenarios
- Edge Case Tests: Test boundary conditions and unusual inputs

Author: bug6129
"""

import pytest
import json
import math
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from main import (
    app, get_session, Calculation, OperationType,
    CalculatorService, StatisticsService, WeatherService
)

# =============================================================================
# 1. TEST FIXTURES AND SETUP
# =============================================================================

@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session.
    
    This fixture creates a separate in-memory database for each test,
    ensuring test isolation and preventing test interference.
    """
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a test client with database dependency override.
    
    This fixture provides a FastAPI test client with the test database
    session injected, allowing for isolated testing.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_calculations(session: Session):
    """
    Create sample calculations in the test database.
    
    This fixture provides test data for endpoints that require
    existing calculations.
    """
    calculations = [
        Calculation(
            operation="add",
            operands='{"a": 5, "b": 3}',
            result=8.0,
            operation_type=OperationType.BASIC,
            user_session="test_session_1"
        ),
        Calculation(
            operation="sqrt",
            operands='{"value": 16}',
            result=4.0,
            operation_type=OperationType.SCIENTIFIC,
            user_session="test_session_1"
        ),
        Calculation(
            operation="mean",
            operands='{"values": [1, 2, 3, 4, 5]}',
            result=3.0,
            operation_type=OperationType.STATISTICAL,
            user_session="test_session_2"
        )
    ]
    
    for calc in calculations:
        session.add(calc)
    session.commit()
    
    # Refresh to get IDs
    for calc in calculations:
        session.refresh(calc)
    
    return calculations

# =============================================================================
# 2. UNIT TESTS - Testing Business Logic in Isolation
# =============================================================================

class TestCalculatorService:
    """
    Unit tests for CalculatorService.
    
    These tests focus on the business logic without any FastAPI dependencies.
    They run fast and test edge cases thoroughly.
    """
    
    def test_add_positive_numbers(self):
        """Test addition of positive numbers."""
        result = CalculatorService.add(5, 3)
        assert result == 8
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers."""
        assert CalculatorService.add(-5, 3) == -2
        assert CalculatorService.add(-5, -3) == -8
        assert CalculatorService.add(5, -3) == 2
    
    def test_add_zero(self):
        """Test addition with zero."""
        assert CalculatorService.add(0, 5) == 5
        assert CalculatorService.add(5, 0) == 5
        assert CalculatorService.add(0, 0) == 0
    
    def test_add_large_numbers(self):
        """Test addition with large numbers."""
        result = CalculatorService.add(1e10, 2e10)
        assert result == 3e10
    
    def test_subtract_basic(self):
        """Test basic subtraction."""
        assert CalculatorService.subtract(10, 3) == 7
        assert CalculatorService.subtract(3, 10) == -7
        assert CalculatorService.subtract(-5, -3) == -2
    
    def test_multiply_basic(self):
        """Test basic multiplication."""
        assert CalculatorService.multiply(4, 5) == 20
        assert CalculatorService.multiply(-4, 5) == -20
        assert CalculatorService.multiply(-4, -5) == 20
        assert CalculatorService.multiply(0, 5) == 0
    
    def test_divide_basic(self):
        """Test basic division."""
        assert CalculatorService.divide(10, 2) == 5
        assert CalculatorService.divide(7, 2) == 3.5
        assert CalculatorService.divide(-10, 2) == -5
    
    def test_divide_by_zero(self):
        """Test division by zero error."""
        with pytest.raises(ValueError, match="Division by zero is not allowed"):
            CalculatorService.divide(5, 0)
    
    def test_square_root_positive(self):
        """Test square root of positive numbers."""
        assert CalculatorService.square_root(16) == 4
        assert CalculatorService.square_root(25) == 5
        assert CalculatorService.square_root(2) == pytest.approx(1.414213, rel=1e-5)
    
    def test_square_root_zero(self):
        """Test square root of zero."""
        assert CalculatorService.square_root(0) == 0
    
    def test_square_root_negative(self):
        """Test square root of negative number."""
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            CalculatorService.square_root(-1)
    
    def test_power_basic(self):
        """Test power calculations."""
        assert CalculatorService.power(2, 3) == 8
        assert CalculatorService.power(5, 0) == 1
        assert CalculatorService.power(10, -2) == 0.01
    
    def test_logarithm_natural(self):
        """Test natural logarithm."""
        assert CalculatorService.logarithm(math.e) == pytest.approx(1, rel=1e-10)
        assert CalculatorService.logarithm(1) == pytest.approx(0, abs=1e-10)
    
    def test_logarithm_base_10(self):
        """Test logarithm base 10."""
        assert CalculatorService.logarithm(100, 10) == pytest.approx(2, rel=1e-10)
        assert CalculatorService.logarithm(1000, 10) == pytest.approx(3, rel=1e-10)
    
    def test_logarithm_invalid_input(self):
        """Test logarithm with invalid inputs."""
        with pytest.raises(ValueError, match="Logarithm input must be positive"):
            CalculatorService.logarithm(-1)
        
        with pytest.raises(ValueError, match="Logarithm input must be positive"):
            CalculatorService.logarithm(0)
        
        with pytest.raises(ValueError, match="Logarithm base must be positive"):
            CalculatorService.logarithm(10, -1)
        
        with pytest.raises(ValueError, match="not equal to 1"):
            CalculatorService.logarithm(10, 1)
    
    def test_trigonometric_functions(self):
        """Test trigonometric functions."""
        # Test known values
        assert CalculatorService.sine(0) == pytest.approx(0, abs=1e-10)
        assert CalculatorService.sine(math.pi/2) == pytest.approx(1, rel=1e-10)
        
        assert CalculatorService.cosine(0) == pytest.approx(1, rel=1e-10)
        assert CalculatorService.cosine(math.pi/2) == pytest.approx(0, abs=1e-10)
        
        assert CalculatorService.tangent(0) == pytest.approx(0, abs=1e-10)
        assert CalculatorService.tangent(math.pi/4) == pytest.approx(1, rel=1e-10)

class TestStatisticsService:
    """Unit tests for StatisticsService."""
    
    def test_mean_basic(self):
        """Test mean calculation."""
        assert StatisticsService.mean([1, 2, 3, 4, 5]) == 3
        assert StatisticsService.mean([10, 20, 30]) == 20
        assert StatisticsService.mean([5]) == 5
    
    def test_mean_empty_list(self):
        """Test mean with empty list."""
        with pytest.raises(ValueError, match="Cannot calculate mean of empty list"):
            StatisticsService.mean([])
    
    def test_median_odd_count(self):
        """Test median with odd number of values."""
        assert StatisticsService.median([1, 3, 5]) == 3
        assert StatisticsService.median([5, 1, 3]) == 3  # Order shouldn't matter
    
    def test_median_even_count(self):
        """Test median with even number of values."""
        assert StatisticsService.median([1, 2, 3, 4]) == 2.5
        assert StatisticsService.median([10, 20]) == 15
    
    def test_median_empty_list(self):
        """Test median with empty list."""
        with pytest.raises(ValueError, match="Cannot calculate median of empty list"):
            StatisticsService.median([])
    
    def test_mode_single_mode(self):
        """Test mode with single most frequent value."""
        assert StatisticsService.mode([1, 2, 2, 3]) == 2
        assert StatisticsService.mode([5, 5, 5, 1, 2, 3]) == 5
    
    def test_mode_no_mode(self):
        """Test mode when all values appear equally."""
        with pytest.raises(ValueError, match="No mode found"):
            StatisticsService.mode([1, 2, 3, 4])
    
    def test_mode_empty_list(self):
        """Test mode with empty list."""
        with pytest.raises(ValueError, match="Cannot calculate mode of empty list"):
            StatisticsService.mode([])
    
    def test_standard_deviation_basic(self):
        """Test standard deviation calculation."""
        # Simple case where we know the answer
        values = [2, 4, 4, 4, 5, 5, 7, 9]
        result = StatisticsService.standard_deviation(values)
        assert result == pytest.approx(2.138, rel=1e-3)
    
    def test_standard_deviation_insufficient_values(self):
        """Test standard deviation with insufficient values."""
        with pytest.raises(ValueError, match="Need at least 2 values"):
            StatisticsService.standard_deviation([1])
        
        with pytest.raises(ValueError, match="Need at least 2 values"):
            StatisticsService.standard_deviation([])

# =============================================================================
# 3. INTEGRATION TESTS - Testing Complete API Endpoints
# =============================================================================

class TestBasicCalculatorAPI:
    """Integration tests for basic calculator endpoints."""
    
    def test_add_endpoint(self, client: TestClient):
        """Test the add endpoint."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": 5, "b": 3}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["result"] == 8
        assert data["operation"] == "add"
        assert data["operands"] == {"a": 5, "b": 3}
        assert data["operation_type"] == "basic"
        assert "calculation_id" in data
    
    def test_divide_by_zero_endpoint(self, client: TestClient):
        """Test division by zero through API."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "divide", "a": 5, "b": 0}
        )
        assert response.status_code == 400
        assert "Division by zero" in response.json()["detail"]
    
    def test_invalid_operation(self, client: TestClient):
        """Test invalid operation through API."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "invalid", "a": 5, "b": 3}
        )
        assert response.status_code == 400
        assert "Unsupported operation" in response.json()["detail"]
    
    @pytest.mark.parametrize("operation,a,b,expected", [
        ("add", 10, 5, 15),
        ("subtract", 10, 5, 5),
        ("multiply", 10, 5, 50),
        ("divide", 10, 5, 2),
    ])
    def test_basic_operations_parametrized(self, client: TestClient, operation, a, b, expected):
        """Test multiple basic operations using parametrization."""
        response = client.post(
            "/calculate/basic",
            json={"operation": operation, "a": a, "b": b}
        )
        assert response.status_code == 200
        assert response.json()["result"] == expected

class TestScientificCalculatorAPI:
    """Integration tests for scientific calculator endpoints."""
    
    def test_square_root_endpoint(self, client: TestClient):
        """Test square root endpoint."""
        response = client.post(
            "/calculate/scientific",
            json={"operation": "sqrt", "value": 16}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 4
    
    def test_power_endpoint(self, client: TestClient):
        """Test power endpoint."""
        response = client.post(
            "/calculate/scientific",
            json={"operation": "power", "value": 2, "base": 3}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 8
    
    def test_power_missing_base(self, client: TestClient):
        """Test power endpoint without base parameter."""
        response = client.post(
            "/calculate/scientific",
            json={"operation": "power", "value": 2}
        )
        assert response.status_code == 400
        assert "Base parameter required" in response.json()["detail"]
    
    def test_square_root_negative(self, client: TestClient):
        """Test square root of negative number."""
        response = client.post(
            "/calculate/scientific",
            json={"operation": "sqrt", "value": -1}
        )
        assert response.status_code == 400

class TestStatisticalCalculatorAPI:
    """Integration tests for statistical calculator endpoints."""
    
    def test_mean_endpoint(self, client: TestClient):
        """Test mean calculation endpoint."""
        response = client.post(
            "/calculate/statistical",
            json={"operation": "mean", "values": [1, 2, 3, 4, 5]}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 3
    
    def test_median_endpoint(self, client: TestClient):
        """Test median calculation endpoint."""
        response = client.post(
            "/calculate/statistical",
            json={"operation": "median", "values": [1, 3, 2, 5, 4]}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 3
    
    def test_empty_values_list(self, client: TestClient):
        """Test statistical operation with empty values list."""
        response = client.post(
            "/calculate/statistical",
            json={"operation": "mean", "values": []}
        )
        assert response.status_code == 422  # Validation error for min_items=1

# =============================================================================
# 4. DATABASE TESTS - Testing Data Persistence
# =============================================================================

class TestCalculationHistory:
    """Tests for calculation history and database operations."""
    
    def test_calculation_stored_in_database(self, client: TestClient, session: Session):
        """Test that calculations are stored in the database."""
        # Perform a calculation
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": 10, "b": 5}
        )
        assert response.status_code == 200
        
        # Check that calculation was stored
        calculations = session.exec(select(Calculation)).all()
        assert len(calculations) == 1
        
        calc = calculations[0]
        assert calc.operation == "add"
        assert calc.result == 15
        assert calc.operation_type == OperationType.BASIC
    
    def test_get_calculation_history(self, client: TestClient, sample_calculations):
        """Test retrieving calculation history."""
        response = client.get("/calculations/history")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        assert all("id" in calc for calc in data)
        assert all("operation" in calc for calc in data)
    
    def test_filter_history_by_session(self, client: TestClient, sample_calculations):
        """Test filtering history by user session."""
        response = client.get("/calculations/history?user_session=test_session_1")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2  # Two calculations for test_session_1
    
    def test_filter_history_by_type(self, client: TestClient, sample_calculations):
        """Test filtering history by operation type."""
        response = client.get("/calculations/history?operation_type=basic")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["operation_type"] == "basic"
    
    def test_get_specific_calculation(self, client: TestClient, sample_calculations):
        """Test getting a specific calculation by ID."""
        calc_id = sample_calculations[0].id
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == calc_id
        assert data["operation"] == "add"
    
    def test_get_nonexistent_calculation(self, client: TestClient):
        """Test getting a calculation that doesn't exist."""
        response = client.get("/calculations/99999")
        assert response.status_code == 404
    
    def test_delete_calculation(self, client: TestClient, sample_calculations):
        """Test deleting a calculation."""
        calc_id = sample_calculations[0].id
        response = client.delete(f"/calculations/{calc_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 404

# =============================================================================
# 5. EXTERNAL SERVICE TESTS - Testing Mocked Dependencies
# =============================================================================

class TestExternalServices:
    """Tests for external service integrations and mocking."""
    
    def test_weather_service_success(self, client: TestClient):
        """Test successful weather service call."""
        response = client.get("/external/weather/London")
        assert response.status_code == 200
        
        data = response.json()
        assert data["city"] == "London"
        assert "temperature_celsius" in data
        assert "temperature_fahrenheit" in data
    
    def test_weather_service_unknown_city(self, client: TestClient):
        """Test weather service with unknown city."""
        response = client.get("/external/weather/UnknownCity")
        assert response.status_code == 404
        assert "not available" in response.json()["detail"]
    
    @patch.object(WeatherService, 'is_service_available')
    def test_weather_service_unavailable(self, mock_available, client: TestClient):
        """Test weather service when it's unavailable."""
        mock_available.return_value = False
        
        response = client.get("/external/weather/London")
        assert response.status_code == 503
        assert "unavailable" in response.json()["detail"]
    
    @patch.object(WeatherService, 'get_temperature')
    def test_weather_service_mocked_response(self, mock_temp, client: TestClient):
        """Test weather service with mocked temperature."""
        mock_temp.return_value = 25.5
        
        response = client.get("/external/weather/TestCity")
        assert response.status_code == 200
        
        data = response.json()
        assert data["temperature_celsius"] == 25.5
        assert data["temperature_fahrenheit"] == 77.9  # (25.5 * 9/5) + 32

# =============================================================================
# 6. ERROR HANDLING TESTS - Testing Various Error Scenarios
# =============================================================================

class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_malformed_json(self, client: TestClient):
        """Test handling of malformed JSON."""
        response = client.post(
            "/calculate/basic",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_required_fields(self, client: TestClient):
        """Test handling of missing required fields."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": 5}  # Missing 'b'
        )
        assert response.status_code == 422
    
    def test_invalid_data_types(self, client: TestClient):
        """Test handling of invalid data types."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": "not_a_number", "b": 5}
        )
        assert response.status_code == 422
    
    def test_test_error_endpoints(self, client: TestClient):
        """Test the dedicated error testing endpoints."""
        # Test 400 error
        response = client.post("/test/error?error_type=400")
        assert response.status_code == 400
        
        # Test 404 error
        response = client.post("/test/error?error_type=404")
        assert response.status_code == 404
        
        # Test 500 error
        response = client.post("/test/error?error_type=500")
        assert response.status_code == 500

# =============================================================================
# 7. PERFORMANCE TESTS - Basic Performance Validation
# =============================================================================

class TestPerformance:
    """Basic performance tests."""
    
    def test_calculation_performance(self, client: TestClient):
        """Test that calculations complete within reasonable time."""
        import time
        
        start_time = time.time()
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": 1000, "b": 2000}
        )
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should complete in less than 1 second
    
    def test_multiple_calculations(self, client: TestClient):
        """Test multiple calculations in sequence."""
        operations = [
            {"operation": "add", "a": 1, "b": 2},
            {"operation": "multiply", "a": 3, "b": 4},
            {"operation": "divide", "a": 10, "b": 2},
            {"operation": "subtract", "a": 8, "b": 3}
        ]
        
        for operation in operations:
            response = client.post("/calculate/basic", json=operation)
            assert response.status_code == 200

# =============================================================================
# 8. EDGE CASE TESTS - Testing Boundary Conditions
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_very_large_numbers(self, client: TestClient):
        """Test calculations with very large numbers."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": 1e15, "b": 2e15}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 3e15
    
    def test_very_small_numbers(self, client: TestClient):
        """Test calculations with very small numbers."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "add", "a": 1e-15, "b": 2e-15}
        )
        assert response.status_code == 200
        assert response.json()["result"] == pytest.approx(3e-15)
    
    def test_infinity_handling(self, client: TestClient):
        """Test handling of infinity values."""
        response = client.post(
            "/calculate/basic",
            json={"operation": "divide", "a": 1e308, "b": 1e-308}
        )
        assert response.status_code == 200
        # Result should be a very large number (possibly infinity)
    
    def test_statistical_operations_single_value(self, client: TestClient):
        """Test statistical operations with single value."""
        response = client.post(
            "/calculate/statistical",
            json={"operation": "mean", "values": [42]}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 42
    
    def test_statistical_operations_large_dataset(self, client: TestClient):
        """Test statistical operations with large dataset."""
        values = list(range(1000))  # 0 to 999
        response = client.post(
            "/calculate/statistical",
            json={"operation": "mean", "values": values}
        )
        assert response.status_code == 200
        assert response.json()["result"] == 499.5  # Mean of 0 to 999

# =============================================================================
# 9. UTILITY TESTS - Testing Utility Endpoints
# =============================================================================

class TestUtilityEndpoints:
    """Tests for utility and system endpoints."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test the root information endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "features" in data
        assert "testing_examples" in data
    
    def test_health_check(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "features" in data
    
    def test_stats_endpoint(self, client: TestClient, sample_calculations):
        """Test the statistics endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_calculations" in data
        assert "by_type" in data
        assert data["total_calculations"] == 3
    
    def test_database_reset(self, client: TestClient, sample_calculations):
        """Test database reset functionality."""
        # Verify we have data
        response = client.get("/calculations/history")
        assert len(response.json()) == 3
        
        # Reset database
        response = client.post("/test/reset-db")
        assert response.status_code == 200
        assert response.json()["deleted_calculations"] == 3
        
        # Verify data is gone
        response = client.get("/calculations/history")
        assert len(response.json()) == 0

# =============================================================================
# 10. PYTEST CONFIGURATION AND CUSTOM MARKERS
# =============================================================================

# Custom pytest markers (add to pytest.ini or pyproject.toml)
pytestmark = [
    pytest.mark.unit,    # For unit tests
    pytest.mark.integration,  # For integration tests
    pytest.mark.database,     # For database tests
    pytest.mark.external,     # For external service tests
]

# Run specific test categories:
# pytest -m unit                    # Run only unit tests
# pytest -m integration             # Run only integration tests
# pytest -m "not external"          # Run all tests except external service tests
# pytest --cov=main                 # Run with coverage report