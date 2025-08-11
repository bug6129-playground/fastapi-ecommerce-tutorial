# Tutorial B: E-Commerce Foundation

**Build the foundation of a real e-commerce API** 🛍️

In this tutorial, you'll create the foundational structure of an e-commerce API that we'll build throughout this course. You'll set up professional project architecture, configuration management, and core API endpoints.

## 🎯 Learning Objectives

By the end of this tutorial, you'll have:
- ✅ Professional e-commerce API project structure
- ✅ YAML-based configuration system
- ✅ Core API endpoints for health checks and info
- ✅ Proper documentation and metadata
- ✅ Foundation ready for user management, products, and orders

## 🏗️ What We're Building

We're creating the foundation for a complete e-commerce API that will eventually include:
- **User Management** - Registration, authentication, profiles
- **Product Catalog** - Products, categories, inventory management
- **Shopping Cart** - Add items, manage quantities, checkout
- **Order Processing** - Order creation, tracking, fulfillment
- **Customer Support** - Help tickets, customer service

## ⚡ Quick Setup

```bash
# Navigate to the e-commerce app directory
cd ecommerce-app

# Install dependencies (if not done already)
pip install "fastapi[standard]" PyYAML

# Run the application
python -m uvicorn app.main:app --reload
```

## 📁 Project Structure Overview

```
ecommerce-app/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   └── (more modules as we progress...)
├── config.yaml              # Application configuration
├── requirements.txt         # Dependencies
└── README.md               # Project documentation
```

## 🛠️ Step 1: Configuration System

First, let's create a flexible configuration system using YAML:

### ecommerce-app/config.yaml

```yaml
# FastAPI E-Commerce API - Configuration
# =====================================

# Application Information
app:
  name: "FastAPI E-Commerce API"
  version: "1.0.0"
  description: "A comprehensive e-commerce API built with FastAPI"
  environment: "development"
  debug: true

# Server Configuration
server:
  host: "127.0.0.1"
  port: 8000
  reload: true

# API Documentation
docs:
  title: "FastAPI E-Commerce API"
  description: |
    A comprehensive e-commerce API built with FastAPI for learning and production.
    
    ## Features
    - 👥 User Management - Registration, authentication, profiles
    - 🛍️ Product Catalog - Products, categories, inventory
    - 🛒 Shopping Cart - Add items, manage quantities
    - 📦 Order Processing - Checkout, payment, fulfillment
    - 🎧 Customer Support - Help tickets, communication
    
    ## Getting Started
    1. Register a new user account
    2. Browse the product catalog  
    3. Add items to your shopping cart
    4. Complete the checkout process
    5. Track your order status
    
  version: "1.0.0"
  contact:
    name: "bug6129"
    email: "support@ecommerce-api.com"
  license:
    name: "MIT License"
    url: "https://opensource.org/licenses/MIT"

# CORS Configuration
cors:
  allowed_origins:
    - "http://localhost:3000"
    - "http://localhost:8080"
    - "http://127.0.0.1:3000"
  allowed_methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  allowed_headers:
    - "*"
  allow_credentials: true

# Feature Flags (we'll implement these in future tutorials)
features:
  enable_user_registration: true
  enable_product_catalog: true
  enable_shopping_cart: true
  enable_order_processing: true
  enable_customer_support: true

# Business Configuration
business:
  currency: "USD"
  tax_rate: 0.08  # 8% tax rate
  free_shipping_threshold: 50.00
  max_cart_items: 100
  order_timeout_minutes: 30

# Development Settings
development:
  create_sample_data: true
  log_sql_queries: false
  cors_allow_all: true
```

**Why YAML configuration?**
- ✅ Easy to read and modify
- ✅ No code changes needed for configuration updates
- ✅ Environment-specific settings
- ✅ Version control friendly

## 🔧 Step 2: Configuration Management

Create the configuration loader:

### ecommerce-app/app/config.py

```python
"""
E-Commerce API Configuration Management
======================================

This module handles loading and managing configuration from YAML files.
It provides type-safe configuration classes and easy access to settings.

Author: bug6129
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration settings."""
    name: str
    version: str
    description: str
    environment: str
    debug: bool


class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str
    port: int
    reload: bool


class DocsConfig(BaseModel):
    """API documentation configuration."""
    title: str
    description: str
    version: str
    contact: Dict[str, str]
    license: Dict[str, str]


class CorsConfig(BaseModel):
    """CORS configuration settings."""
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    allow_credentials: bool


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    enable_user_registration: bool
    enable_product_catalog: bool
    enable_shopping_cart: bool
    enable_order_processing: bool
    enable_customer_support: bool


class BusinessConfig(BaseModel):
    """Business logic configuration."""
    currency: str
    tax_rate: float
    free_shipping_threshold: float
    max_cart_items: int
    order_timeout_minutes: int


class DevelopmentConfig(BaseModel):
    """Development-specific configuration."""
    create_sample_data: bool
    log_sql_queries: bool
    cors_allow_all: bool


class Settings(BaseModel):
    """Main configuration class that combines all settings."""
    app: AppConfig
    server: ServerConfig
    docs: DocsConfig
    cors: CorsConfig
    features: FeaturesConfig
    business: BusinessConfig
    development: DevelopmentConfig

    @classmethod
    def load_from_yaml(cls, config_file: str = "config.yaml") -> "Settings":
        """
        Load configuration from YAML file.
        
        Args:
            config_file: Path to the YAML configuration file
            
        Returns:
            Settings: Loaded configuration
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file '{config_file}' not found")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app.environment.lower() == "production"


# Global settings instance
settings = Settings.load_from_yaml()
```

## 🚀 Step 3: Main Application

Create the main FastAPI application:

### ecommerce-app/app/main.py

```python
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
            "users": "Coming in Tutorial 2!",
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
```

## 📋 Step 4: Dependencies and Package Files

### ecommerce-app/requirements.txt

```txt
# FastAPI E-Commerce API Dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
PyYAML==6.0.1
pydantic==2.5.0
```

### ecommerce-app/app/__init__.py

```python
"""
FastAPI E-Commerce API Package
=============================

This package contains the complete e-commerce API application built with FastAPI.

Author: bug6129
"""

__version__ = "1.0.0"
__author__ = "bug6129"
__description__ = "A comprehensive FastAPI e-commerce API for learning"
```

## 🧪 Testing Your E-Commerce Foundation

1. **Navigate to the e-commerce app:**
   ```bash
   cd ecommerce-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Test the endpoints:**

   | Endpoint | Purpose | What to expect |
   |----------|---------|----------------|
   | `GET /` | API info | Overview of your e-commerce API |
   | `GET /health` | Health check | System health status |
   | `GET /status` | API status | Detailed status information |
   | `GET /system` | System info | Configuration details (dev only) |
   | `GET /docs` | Interactive docs | Beautiful Swagger UI |

5. **Explore the documentation:**
   - Visit http://localhost:8000/docs
   - Notice how professional and detailed it looks
   - Try the "Try it out" feature on each endpoint

## 🔍 Key Concepts Explained

### 1. **Configuration Management**
```yaml
app:
  name: "FastAPI E-Commerce API"
  version: "1.0.0"
```
- All settings in one YAML file
- Easy to modify without code changes
- Type-safe with Pydantic validation

### 2. **Professional API Structure**
```python
app = FastAPI(
    title=settings.docs.title,
    description=settings.docs.description,
    # All metadata from configuration
)
```
- Rich metadata for documentation
- Contact information and licensing
- Environment-aware configuration

### 3. **CORS Middleware**
```python
app.add_middleware(CORSMiddleware, ...)
```
- Enables frontend applications to connect
- Configurable origins and methods
- Production-ready security settings

### 4. **Structured Endpoints with Tags**
```python
@app.get("/health", tags=["System"])
```
- Tags organize endpoints in documentation
- Clear separation of concerns
- Professional API organization

### 5. **Feature Flags**
```yaml
features:
  enable_user_registration: true
  enable_product_catalog: true
```
- Easy feature toggling
- Gradual rollout capability
- Environment-specific features

## 🎯 What Makes This Professional?

1. **📝 Rich Documentation**: Detailed descriptions, contact info, licensing
2. **⚙️ Configuration Management**: YAML-based, environment-aware
3. **🏷️ Organized Endpoints**: Proper tags, clear naming, consistent responses
4. **🔒 Security Ready**: CORS middleware, environment separation
5. **📊 Monitoring Ready**: Health checks, status endpoints, startup/shutdown events
6. **🎛️ Feature Flags**: Easy feature management and rollout
7. **📦 Proper Structure**: Clean separation, professional organization

## ✨ Configuration Flexibility

Want to change the port? Just edit `config.yaml`:

```yaml
server:
  port: 3000  # Changed from 8000 to 3000
```

Want to add new CORS origins? Easy:

```yaml
cors:
  allowed_origins:
    - "http://localhost:3000"
    - "https://my-frontend.com"  # Added new origin
```

No code changes required! 🎉

## 🔮 What's Coming Next

In future tutorials, we'll add to this foundation:

- **Tutorial B2**: User registration and authentication system
- **Tutorial B3**: Product catalog with categories and inventory
- **Tutorial B4**: Shopping cart and session management
- **Tutorial B5**: Order processing and payment integration
- **Tutorial B6**: Customer support and help desk system

Each tutorial builds on this foundation, creating a complete e-commerce platform.

## 📚 Summary

**What you built:**
- ✅ Professional e-commerce API foundation
- ✅ YAML-based configuration system
- ✅ Rich API documentation and metadata
- ✅ System health and status endpoints
- ✅ CORS and security middleware
- ✅ Feature flag system for future development
- ✅ Professional project structure

**Key takeaways:**
1. Configuration in YAML files keeps code flexible
2. Rich metadata creates professional documentation
3. Tags and organization matter for large APIs
4. Health checks are essential for production systems
5. Feature flags enable gradual development and rollout

Great job! You now have a solid foundation for building a complete e-commerce API. 🎉

---

## ➡️ What's Next?

Continue building your e-commerce API with **Tutorial B2: [User Management System](../02-data-models/apply-user-system.md)**, where you'll add:

- User registration and login
- Profile management
- Email validation
- Password security
- JWT authentication preparation

Or explore **Tutorial A2: [Pydantic Fundamentals](../02-data-models/learn-pydantic.md)** to learn more about data validation and models!

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial B1*