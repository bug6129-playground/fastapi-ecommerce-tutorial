# FastAPI E-Commerce API

**A comprehensive e-commerce API built with FastAPI** 🛍️

This is the complete e-commerce application that you build throughout the FastAPI tutorial. It demonstrates professional API development practices, clean architecture, and real-world e-commerce functionality.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Visit the API:**
   - **API Root**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc

## 🏗️ What's Included

### Core System Endpoints
- `GET /` - API information and features
- `GET /health` - Health check for monitoring
- `GET /status` - Detailed system status
- `GET /system` - Configuration details (development only)

### Planned Features (Built Throughout Tutorials)
- **👥 User Management** - Registration, authentication, profiles
- **🛍️ Product Catalog** - Products, categories, inventory
- **🛒 Shopping Cart** - Add items, manage quantities
- **📦 Order Processing** - Checkout, payment, fulfillment
- **🎧 Customer Support** - Help tickets, communication

## ⚙️ Configuration

All settings are managed through `config.yaml`. Edit this file to customize:

```yaml
# Change server port
server:
  port: 3000  # Default: 8000

# Enable/disable features  
features:
  enable_user_registration: true
  enable_product_catalog: true

# Business settings
business:
  currency: "USD"
  tax_rate: 0.08
  free_shipping_threshold: 50.00
```

## 🎓 Learning Path

This application is built progressively through the tutorial:

1. **Tutorial B1** ✅ - Foundation and configuration (you are here)
2. **Tutorial B2** - User management system
3. **Tutorial B3** - Product catalog and categories
4. **Tutorial B4** - Shopping cart and sessions
5. **Tutorial B5** - Order processing and tracking
6. **Tutorial B6** - Authentication and security
7. **Tutorial B7** - Customer support system
8. **Tutorial B8** - Production deployment

## 📚 Project Structure

```
ecommerce-app/
├── app/                    # Main application package
│   ├── __init__.py        # Package info
│   ├── main.py            # FastAPI app and routes
│   ├── config.py          # Configuration management
│   ├── models/            # Database models (coming soon)
│   ├── routers/           # API route handlers (coming soon)
│   ├── schemas/           # Request/response models (coming soon)
│   ├── services/          # Business logic (coming soon)
│   └── utils/             # Utilities (coming soon)
├── tests/                 # Test suite (coming soon)
├── config.yaml            # Application configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Development

### Adding New Features

1. Update `config.yaml` feature flags
2. Add new endpoints to appropriate router
3. Update documentation and tests
4. Follow the tutorial progression

### Configuration Management

- All settings in `config.yaml`
- Type-safe configuration with Pydantic
- Environment-specific overrides
- No code changes needed for configuration updates

## 🧪 API Testing

Use the interactive documentation at http://localhost:8000/docs to:

- Explore all endpoints
- Test API responses
- See request/response schemas
- Try different parameters

## 📖 Documentation

- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔒 Security Features

- CORS middleware for frontend integration
- Environment-aware configuration
- Development vs production settings
- Feature flags for controlled rollouts

## 🎯 Business Logic

Current business rules (configurable in `config.yaml`):

- Currency: USD
- Tax rate: 8%
- Free shipping threshold: $50.00
- Maximum cart items: 100
- Order timeout: 30 minutes

## ➡️ What's Next?

Continue with **Tutorial B2: User Management System** to add:

- User registration and login
- Profile management  
- Email validation
- Password security
- Authentication foundation

---

**Built with FastAPI Tutorial by bug6129** 🚀

*This e-commerce API demonstrates professional FastAPI development practices and serves as both a learning resource and a foundation for real-world applications.*