"""
FastAPI E-Commerce API - Main Application
========================================

This is the main entry point for the e-commerce API. It sets up the FastAPI
application with proper configuration, CORS, and foundational endpoints.

Author: bug6129
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import create_db_and_tables
from .routers import users

# Create FastAPI application with configuration from YAML
app = FastAPI(
    title=settings.docs.title,
    description=settings.docs.description,
    version=settings.docs.version,
    contact=settings.docs.contact,
    license_info=settings.docs.license,
    debug=settings.app.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
)

# Include routers
app.include_router(users.router)

# Root endpoint - API information
@app.get("/", tags=["System"])
async def api_info():
    """
    Get API information and status.
    
    This endpoint provides basic information about the API,
    including version, features, and current status.
    
    Returns:
        dict: API information and status
    """
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "description": settings.app.description,
        "status": "running",
        "environment": settings.app.environment,
        "features": {
            "user_registration": settings.features.enable_user_registration,
            "product_catalog": settings.features.enable_product_catalog,
            "shopping_cart": settings.features.enable_shopping_cart,
            "order_processing": settings.features.enable_order_processing,
            "customer_support": settings.features.enable_customer_support,
        },
        "business": {
            "currency": settings.business.currency,
            "free_shipping_threshold": settings.business.free_shipping_threshold,
        },
        "docs": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        }
    }

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    This endpoint is used by monitoring systems, load balancers,
    and container orchestration systems to check API health.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": settings.app.name,
        "version": settings.app.version,
        "environment": settings.app.environment,
        "checks": {
            "api": "ok",
            "configuration": "ok",
            # We'll add database, cache, etc. in future tutorials
        }
    }

# System information endpoint (useful for debugging)
@app.get("/system", tags=["System"])
async def system_info():
    """
    Get system configuration information.
    
    This endpoint provides detailed system information for debugging
    and administrative purposes. Only enabled in development mode.
    
    Returns:
        dict: System configuration details
    """
    if not settings.is_development:
        return {"message": "System info only available in development mode"}
    
    return {
        "app": settings.app.dict(),
        "server": settings.server.dict(),
        "features": settings.features.dict(),
        "business": settings.business.dict(),
        "development": settings.development.dict(),
    }

# API status endpoint
@app.get("/status", tags=["System"])
async def api_status():
    """
    Get detailed API status information.
    
    This endpoint provides current status of various API components
    and features. Useful for monitoring and administrative dashboards.
    
    Returns:
        dict: Detailed API status
    """
    return {
        "timestamp": "2024-01-01T12:00:00Z",  # We'll make this dynamic later
        "uptime": "Just started!",  # We'll calculate real uptime later
        "version": settings.app.version,
        "environment": settings.app.environment,
        "features_enabled": [
            feature for feature, enabled in settings.features.dict().items() 
            if enabled
        ],
        "endpoints_available": {
            "system": ["/", "/health", "/system", "/status"],
            "users": ["/users/register", "/users/login", "/users/{id}", "/users/{id}/profile"],
            "products": "Coming in Tutorial 5!",
            "orders": "Coming in Tutorial 6!",
        },
        "configuration": {
            "currency": settings.business.currency,
            "tax_rate": f"{settings.business.tax_rate * 100}%",
            "free_shipping": f"${settings.business.free_shipping_threshold}",
            "max_cart_items": settings.business.max_cart_items,
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    This function runs when the FastAPI application starts up.
    We'll use it for initialization tasks like database connections,
    cache setup, etc. in future tutorials.
    """
    print(f"🚀 Starting {settings.app.name} v{settings.app.version}")
    print(f"🌍 Environment: {settings.app.environment}")
    print(f"🔧 Debug mode: {settings.app.debug}")
    
    # Initialize database tables
    create_db_and_tables()
    print("📊 Database tables initialized")
    
    if settings.development.create_sample_data:
        print("📊 Sample data creation enabled (will implement in future tutorials)")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    This function runs when the FastAPI application shuts down.
    We'll use it for cleanup tasks like closing database connections,
    etc. in future tutorials.
    """
    print(f"🛑 Shutting down {settings.app.name}")