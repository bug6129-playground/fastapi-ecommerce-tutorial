"""
Testing Fundamentals - Calculator API
=====================================

This example demonstrates testing concepts for FastAPI applications.
Learn how to write unit tests, integration tests, test authentication,
database operations, and implement comprehensive test coverage through
a calculator and data processing API.

Key Concepts Demonstrated:
- Unit testing with pytest
- FastAPI test client usage
- Database testing with test databases
- Authentication testing
- Mocking external dependencies
- Test fixtures and parametrization
- Test coverage and reporting
- Error testing and edge cases

Author: bug6129
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import math
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create FastAPI app
app = FastAPI(
    title="Testing Fundamentals - Calculator API",
    description="Learn testing through a calculator and data processing API",
    version="1.0.0"
)

# =============================================================================
# 1. DATA MODELS - Calculator and Operations
# =============================================================================

class OperationType(str, Enum):
    """Operation type enumeration."""
    BASIC = "basic"         # +, -, *, /
    SCIENTIFIC = "scientific"  # sqrt, pow, log
    STATISTICAL = "statistical"  # mean, median, mode

class CalculationBase(SQLModel):
    """Base calculation model."""
    operation: str = Field(..., description="Operation performed", max_length=50)
    operands: str = Field(..., description="Input values as JSON string")
    result: float = Field(..., description="Calculation result")
    operation_type: OperationType = Field(..., description="Type of operation")

class Calculation(CalculationBase, table=True):
    """Calculation history database table."""
    
    __tablename__ = "calculations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_session: Optional[str] = Field(None, description="User session identifier")

class CalculationResponse(CalculationBase):
    """Response model for calculation results."""
    id: int
    created_at: datetime
    user_session: Optional[str]

# Request/Response models for different operations
class BasicOperationRequest(BaseModel):
    """Request for basic arithmetic operations."""
    operation: str = Field(..., description="Operation: add, subtract, multiply, divide")
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")

class ScientificOperationRequest(BaseModel):
    """Request for scientific operations."""
    operation: str = Field(..., description="Operation: sqrt, power, log, sin, cos, tan")
    value: float = Field(..., description="Input value")
    base: Optional[float] = Field(None, description="Base for power/log operations")

class StatisticalOperationRequest(BaseModel):
    """Request for statistical operations."""
    operation: str = Field(..., description="Operation: mean, median, mode, std_dev")
    values: List[float] = Field(..., description="List of values", min_items=1)

class OperationResult(BaseModel):
    """Generic operation result."""
    result: float
    operation: str
    operands: Dict[str, Any]
    operation_type: OperationType
    calculation_id: Optional[int] = None

# =============================================================================
# 2. BUSINESS LOGIC - Calculator Operations
# =============================================================================

class CalculatorService:
    """
    Calculator service with business logic.
    
    This class contains the core calculation logic that we'll test thoroughly.
    Separated from FastAPI routes for easier unit testing.
    """
    
    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract second number from first."""
        return a - b
    
    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers."""
        return a * b
    
    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide first number by second."""
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        return a / b
    
    @staticmethod
    def square_root(value: float) -> float:
        """Calculate square root."""
        if value < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return math.sqrt(value)
    
    @staticmethod
    def power(base: float, exponent: float) -> float:
        """Raise base to the power of exponent."""
        try:
            return math.pow(base, exponent)
        except OverflowError:
            raise ValueError("Result is too large to represent")
    
    @staticmethod
    def logarithm(value: float, base: float = math.e) -> float:
        """Calculate logarithm."""
        if value <= 0:
            raise ValueError("Logarithm input must be positive")
        if base <= 0 or base == 1:
            raise ValueError("Logarithm base must be positive and not equal to 1")
        
        if base == math.e:
            return math.log(value)
        else:
            return math.log(value) / math.log(base)
    
    @staticmethod
    def sine(value: float) -> float:
        """Calculate sine (value in radians)."""
        return math.sin(value)
    
    @staticmethod
    def cosine(value: float) -> float:
        """Calculate cosine (value in radians)."""
        return math.cos(value)
    
    @staticmethod
    def tangent(value: float) -> float:
        """Calculate tangent (value in radians)."""
        return math.tan(value)

class StatisticsService:
    """
    Statistics service for data analysis.
    
    Contains statistical operations for testing data processing scenarios.
    """
    
    @staticmethod
    def mean(values: List[float]) -> float:
        """Calculate arithmetic mean."""
        if not values:
            raise ValueError("Cannot calculate mean of empty list")
        return sum(values) / len(values)
    
    @staticmethod
    def median(values: List[float]) -> float:
        """Calculate median."""
        if not values:
            raise ValueError("Cannot calculate median of empty list")
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            return sorted_values[n // 2]
    
    @staticmethod
    def mode(values: List[float]) -> float:
        """Calculate mode (most frequent value)."""
        if not values:
            raise ValueError("Cannot calculate mode of empty list")
        
        frequency = {}
        for value in values:
            frequency[value] = frequency.get(value, 0) + 1
        
        max_frequency = max(frequency.values())
        modes = [value for value, freq in frequency.items() if freq == max_frequency]
        
        if len(modes) == len(set(values)):
            raise ValueError("No mode found - all values appear with equal frequency")
        
        return modes[0]  # Return first mode if multiple
    
    @staticmethod
    def standard_deviation(values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            raise ValueError("Need at least 2 values for standard deviation")
        
        mean_val = StatisticsService.mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

# =============================================================================
# 3. DATABASE SETUP
# =============================================================================

DATABASE_URL = "sqlite:///calculator_test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session

# Initialize database
create_db_and_tables()

# =============================================================================
# 4. EXTERNAL SERVICE SIMULATION
# =============================================================================

class WeatherService:
    """
    Simulated external weather service.
    
    This represents an external dependency that we'll mock in tests.
    """
    
    @staticmethod
    def get_temperature(city: str) -> float:
        """Get temperature for a city (simulated external API call)."""
        # Simulate different responses for testing
        temperatures = {
            "New York": 22.5,
            "London": 15.0,
            "Tokyo": 28.0,
            "Sydney": 20.0
        }
        
        if city not in temperatures:
            raise ValueError(f"Weather data not available for {city}")
        
        return temperatures[city]
    
    @staticmethod
    def is_service_available() -> bool:
        """Check if weather service is available."""
        # Simulate service availability
        return True

# =============================================================================
# 5. API ENDPOINTS - Calculator Operations
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API information and testing examples."""
    return {
        "message": "Calculator API - Testing Fundamentals",
        "description": "Learn testing through calculator and data processing operations",
        "features": {
            "basic_operations": ["add", "subtract", "multiply", "divide"],
            "scientific_operations": ["sqrt", "power", "log", "sin", "cos", "tan"],
            "statistical_operations": ["mean", "median", "mode", "std_dev"],
            "external_services": ["weather"]
        },
        "testing_examples": {
            "unit_tests": "Test individual functions in isolation",
            "integration_tests": "Test complete API endpoints",
            "database_tests": "Test data persistence and retrieval",
            "error_tests": "Test error handling and edge cases"
        },
        "endpoints": {
            "basic": "/calculate/basic",
            "scientific": "/calculate/scientific", 
            "statistical": "/calculate/statistical",
            "history": "/calculations/history",
            "weather": "/external/weather/{city}"
        },
        "documentation": "/docs"
    }

# =============================================================================
# BASIC CALCULATOR ENDPOINTS
# =============================================================================

@app.post("/calculate/basic", response_model=OperationResult, tags=["Calculator"])
async def calculate_basic(
    request: BasicOperationRequest,
    session: Session = Depends(get_session),
    user_session: Optional[str] = Query(None, description="User session ID for history tracking")
):
    """
    Perform basic arithmetic operations.
    
    This endpoint demonstrates:
    - Input validation
    - Business logic separation
    - Error handling
    - Database integration
    - Result formatting
    """
    calc = CalculatorService()
    
    # Map operation names to methods
    operations = {
        "add": calc.add,
        "subtract": calc.subtract,
        "multiply": calc.multiply,
        "divide": calc.divide
    }
    
    if request.operation not in operations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported operation: {request.operation}"
        )
    
    try:
        # Perform calculation
        result = operations[request.operation](request.a, request.b)
        
        # Store in database
        calculation = Calculation(
            operation=request.operation,
            operands=f'{{"a": {request.a}, "b": {request.b}}}',
            result=result,
            operation_type=OperationType.BASIC,
            user_session=user_session,
            created_at=datetime.utcnow()
        )
        
        session.add(calculation)
        session.commit()
        session.refresh(calculation)
        
        return OperationResult(
            result=result,
            operation=request.operation,
            operands={"a": request.a, "b": request.b},
            operation_type=OperationType.BASIC,
            calculation_id=calculation.id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during calculation"
        )

# =============================================================================
# SCIENTIFIC CALCULATOR ENDPOINTS
# =============================================================================

@app.post("/calculate/scientific", response_model=OperationResult, tags=["Calculator"])
async def calculate_scientific(
    request: ScientificOperationRequest,
    session: Session = Depends(get_session),
    user_session: Optional[str] = Query(None)
):
    """
    Perform scientific operations.
    
    Demonstrates more complex validation and error handling scenarios.
    """
    calc = CalculatorService()
    
    try:
        result = None
        operands = {"value": request.value}
        
        if request.operation == "sqrt":
            result = calc.square_root(request.value)
        
        elif request.operation == "power":
            if request.base is None:
                raise HTTPException(400, "Base parameter required for power operation")
            result = calc.power(request.value, request.base)
            operands["base"] = request.base
        
        elif request.operation == "log":
            if request.base is not None:
                result = calc.logarithm(request.value, request.base)
                operands["base"] = request.base
            else:
                result = calc.logarithm(request.value)  # Natural log
        
        elif request.operation == "sin":
            result = calc.sine(request.value)
        
        elif request.operation == "cos":
            result = calc.cosine(request.value)
        
        elif request.operation == "tan":
            result = calc.tangent(request.value)
        
        else:
            raise HTTPException(400, f"Unsupported scientific operation: {request.operation}")
        
        # Store calculation
        calculation = Calculation(
            operation=request.operation,
            operands=str(operands).replace("'", '"'),
            result=result,
            operation_type=OperationType.SCIENTIFIC,
            user_session=user_session,
            created_at=datetime.utcnow()
        )
        
        session.add(calculation)
        session.commit()
        session.refresh(calculation)
        
        return OperationResult(
            result=result,
            operation=request.operation,
            operands=operands,
            operation_type=OperationType.SCIENTIFIC,
            calculation_id=calculation.id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Scientific calculation failed")

# =============================================================================
# STATISTICAL OPERATIONS ENDPOINTS
# =============================================================================

@app.post("/calculate/statistical", response_model=OperationResult, tags=["Statistics"])
async def calculate_statistical(
    request: StatisticalOperationRequest,
    session: Session = Depends(get_session),
    user_session: Optional[str] = Query(None)
):
    """
    Perform statistical operations.
    
    Demonstrates testing with list inputs and complex data processing.
    """
    stats = StatisticsService()
    
    operations = {
        "mean": stats.mean,
        "median": stats.median,
        "mode": stats.mode,
        "std_dev": stats.standard_deviation
    }
    
    if request.operation not in operations:
        raise HTTPException(400, f"Unsupported statistical operation: {request.operation}")
    
    try:
        result = operations[request.operation](request.values)
        
        # Store calculation
        calculation = Calculation(
            operation=request.operation,
            operands=f'{{"values": {request.values}}}',
            result=result,
            operation_type=OperationType.STATISTICAL,
            user_session=user_session,
            created_at=datetime.utcnow()
        )
        
        session.add(calculation)
        session.commit()
        session.refresh(calculation)
        
        return OperationResult(
            result=result,
            operation=request.operation,
            operands={"values": request.values},
            operation_type=OperationType.STATISTICAL,
            calculation_id=calculation.id
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# =============================================================================
# CALCULATION HISTORY ENDPOINTS
# =============================================================================

@app.get("/calculations/history", response_model=List[CalculationResponse], tags=["History"])
async def get_calculation_history(
    session: Session = Depends(get_session),
    user_session: Optional[str] = Query(None, description="Filter by user session"),
    operation_type: Optional[OperationType] = Query(None, description="Filter by operation type"),
    limit: int = Query(50, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    Get calculation history.
    
    Demonstrates database querying with filters and pagination.
    """
    query = select(Calculation)
    
    if user_session:
        query = query.where(Calculation.user_session == user_session)
    
    if operation_type:
        query = query.where(Calculation.operation_type == operation_type)
    
    query = query.order_by(Calculation.created_at.desc()).offset(skip).limit(limit)
    calculations = session.exec(query).all()
    
    return [
        CalculationResponse(
            id=calc.id,
            operation=calc.operation,
            operands=calc.operands,
            result=calc.result,
            operation_type=calc.operation_type,
            created_at=calc.created_at,
            user_session=calc.user_session
        )
        for calc in calculations
    ]

@app.get("/calculations/{calculation_id}", response_model=CalculationResponse, tags=["History"])
async def get_calculation(calculation_id: int, session: Session = Depends(get_session)):
    """Get a specific calculation by ID."""
    calculation = session.get(Calculation, calculation_id)
    if not calculation:
        raise HTTPException(404, "Calculation not found")
    
    return CalculationResponse(
        id=calculation.id,
        operation=calculation.operation,
        operands=calculation.operands,
        result=calculation.result,
        operation_type=calculation.operation_type,
        created_at=calculation.created_at,
        user_session=calculation.user_session
    )

@app.delete("/calculations/{calculation_id}", tags=["History"])
async def delete_calculation(calculation_id: int, session: Session = Depends(get_session)):
    """Delete a calculation from history."""
    calculation = session.get(Calculation, calculation_id)
    if not calculation:
        raise HTTPException(404, "Calculation not found")
    
    session.delete(calculation)
    session.commit()
    
    return {"message": f"Calculation {calculation_id} deleted successfully"}

# =============================================================================
# EXTERNAL SERVICE ENDPOINTS (For Testing External Dependencies)
# =============================================================================

@app.get("/external/weather/{city}", tags=["External Services"])
async def get_weather(city: str):
    """
    Get weather information for a city.
    
    This endpoint demonstrates:
    - External service integration
    - Mocking external dependencies in tests
    - Error handling for external failures
    """
    try:
        # Check service availability
        if not WeatherService.is_service_available():
            raise HTTPException(503, "Weather service is currently unavailable")
        
        temperature = WeatherService.get_temperature(city)
        
        return {
            "city": city,
            "temperature_celsius": temperature,
            "temperature_fahrenheit": round((temperature * 9/5) + 32, 1),
            "service": "WeatherService",
            "timestamp": datetime.utcnow()
        }
        
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(503, "Weather service error")

# =============================================================================
# UTILITY AND TESTING ENDPOINTS
# =============================================================================

@app.get("/stats", tags=["Statistics"])
async def get_api_statistics(session: Session = Depends(get_session)):
    """Get API usage statistics."""
    
    # Count calculations by type
    basic_count = len(session.exec(
        select(Calculation).where(Calculation.operation_type == OperationType.BASIC)
    ).all())
    
    scientific_count = len(session.exec(
        select(Calculation).where(Calculation.operation_type == OperationType.SCIENTIFIC)
    ).all())
    
    statistical_count = len(session.exec(
        select(Calculation).where(Calculation.operation_type == OperationType.STATISTICAL)
    ).all())
    
    # Most used operations
    all_calculations = session.exec(select(Calculation)).all()
    operation_counts = {}
    for calc in all_calculations:
        operation_counts[calc.operation] = operation_counts.get(calc.operation, 0) + 1
    
    # Sort by usage
    popular_operations = sorted(operation_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "total_calculations": len(all_calculations),
        "by_type": {
            "basic": basic_count,
            "scientific": scientific_count,
            "statistical": statistical_count
        },
        "popular_operations": popular_operations[:5],
        "unique_sessions": len(set(calc.user_session for calc in all_calculations if calc.user_session)),
        "database_url": DATABASE_URL.replace("sqlite:///", "")
    }

@app.post("/test/error", tags=["Testing"])
async def test_error_handling(error_type: str = Query(..., description="Type of error to simulate")):
    """
    Endpoint for testing error handling scenarios.
    
    This is specifically designed for testing different error conditions.
    """
    if error_type == "400":
        raise HTTPException(400, "Bad request - test error")
    elif error_type == "401":
        raise HTTPException(401, "Unauthorized - test error")
    elif error_type == "404":
        raise HTTPException(404, "Not found - test error")
    elif error_type == "500":
        raise HTTPException(500, "Internal server error - test error")
    elif error_type == "timeout":
        import time
        time.sleep(10)  # Simulate timeout
        return {"message": "This should timeout"}
    elif error_type == "exception":
        raise Exception("Unhandled exception for testing")
    else:
        return {"message": f"Error type '{error_type}' not recognized", "available_types": ["400", "401", "404", "500", "timeout", "exception"]}

@app.post("/test/reset-db", tags=["Testing"])
async def reset_database(session: Session = Depends(get_session)):
    """
    Reset database for testing purposes.
    
    WARNING: This deletes all calculation history!
    """
    # Delete all calculations
    calculations = session.exec(select(Calculation)).all()
    for calc in calculations:
        session.delete(calc)
    session.commit()
    
    return {
        "message": "Database reset successfully",
        "deleted_calculations": len(calculations)
    }

# Health check
@app.get("/health", tags=["System"])
async def health_check(session: Session = Depends(get_session)):
    """Health check with system information."""
    try:
        # Test database connection
        calculation_count = len(session.exec(select(Calculation)).all())
        
        # Test external service
        weather_available = WeatherService.is_service_available()
        
        return {
            "status": "healthy",
            "service": "Calculator API - Testing Fundamentals",
            "database": {
                "status": "connected",
                "calculation_count": calculation_count
            },
            "external_services": {
                "weather": "available" if weather_available else "unavailable"
            },
            "features": {
                "basic_calculator": True,
                "scientific_calculator": True,
                "statistics": True,
                "history": True
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
        )

# Main execution
if __name__ == "__main__":
    import uvicorn
    print("🚀 Testing Fundamentals - Calculator API")
    print("=" * 55)
    print("This tutorial demonstrates testing through calculator operations.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Stats: http://localhost:8000/stats")
    print("")
    print("🧮 Calculator Features:")
    print("   • Basic: add, subtract, multiply, divide")
    print("   • Scientific: sqrt, power, log, sin, cos, tan")
    print("   • Statistical: mean, median, mode, std_dev")
    print("   • History: track and retrieve calculations")
    print("")
    print("🧪 Testing Features:")
    print("   • Business logic separation for unit testing")
    print("   • Database integration testing")
    print("   • External service mocking")
    print("   • Error handling scenarios")
    print("   • Edge case handling")
    print("")
    print("📚 What you'll learn:")
    print("   • Unit testing with pytest")
    print("   • FastAPI test client usage")
    print("   • Database testing strategies")
    print("   • Mocking external dependencies")
    print("   • Test fixtures and parametrization")
    print("   • Error testing and validation")
    print("")
    print("🎯 Try these operations:")
    print("   1. POST /calculate/basic - Test basic arithmetic")
    print("   2. POST /calculate/scientific - Test scientific functions")
    print("   3. POST /calculate/statistical - Test data analysis")
    print("   4. GET /calculations/history - View calculation history")
    print("   5. GET /external/weather/London - Test external service")
    print("")
    print("💾 Database: calculator_test.db")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 55)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)