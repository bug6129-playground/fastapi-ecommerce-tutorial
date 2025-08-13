# FastAPI Learning Resource - Complete Documentation

**A comprehensive, self-service tutorial for building production-ready REST APIs with FastAPI**

This is the complete documentation for the FastAPI Learning Resource. For a quick overview, see the [main README](../README.md).

<details>
<summary><strong>🚀 How to Use This Resource</strong></summary>

### **📖 For Self-Learners**
1. **Sequential Learning**: Follow chapters 1-8 in order for complete mastery
2. **Hands-on Practice**: Type out all code examples yourself  
3. **Experiment**: Try modifications and see what happens
4. **Build Projects**: Complete all exercises and challenges

### **🎓 For Instructors**
1. **Workshop Format**: Each chapter can be a 2-3 hour session
2. **Code-Along**: Lead students through examples step-by-step
3. **Assessment**: Use chapter exercises for evaluation

### **👥 For Teams**
1. **Onboarding**: Use as training material for new developers
2. **Standards**: Adopt patterns and practices from this tutorial
3. **Architecture Reference**: Use project structure as template

</details>

<details>
<summary><strong>🎯 Who This Resource Is For</strong></summary>

This tutorial is designed for **beginner to intermediate developers** who:
- Have basic Python knowledge
- Are new to building APIs
- Want to learn FastAPI by building a real-world project
- Prefer hands-on, project-based learning

</details>

<details>
<summary><strong>🏗️ What You'll Build</strong></summary>

By the end of this tutorial, you'll have built a complete **E-Commerce API** with:
- User registration and authentication
- Product catalog management
- Shopping cart and order processing
- Customer support ticket system
- Full CRUD operations for all resources
- Database integration with PostgreSQL
- Comprehensive testing suite
- Production-ready local deployment

</details>

<details>
<summary><strong>📋 Prerequisites</strong></summary>

- Python 3.8+ installed on your system
- Basic understanding of Python (functions, classes, decorators)
- Familiarity with command line/terminal
- Text editor or IDE (VS Code recommended)
- PostgreSQL installed locally (we'll guide you through this)

</details>

<details>
<summary><strong>🗺️ Learning Path Overview</strong></summary>

### Phase 1: Foundation (Chapters 1-3)
**Estimated Time: 2-3 hours**
- Set up development environment
- Understand FastAPI basics
- Build your first API endpoints
- Learn request/response handling

### Phase 2: Core Development (Chapters 4-5)
**Estimated Time: 4-6 hours**
- Database integration and models
- Implement CRUD operations
- Build the e-commerce API structure
- Handle data validation and errors

### Phase 3: Advanced Features (Chapters 6-7)
**Estimated Time: 3-4 hours**
- Add authentication and authorization
- Implement advanced features
- Write comprehensive tests
- Optimize for performance

### Phase 4: Production Ready (Chapter 8)
**Estimated Time: 2-3 hours**
- Configure for production
- Set up logging and monitoring
- Deploy locally with proper setup
- Best practices and security

</details>

<details>
<summary><strong>📚 Modular Curriculum</strong></summary>

Each chapter offers **two independent tutorials**:

### [Chapter 1: Getting Started](01-getting-started/)
**📖 Tutorial A: [FastAPI Basics](01-getting-started/learn-basics.md)**
- Hello World application
- Path and query parameters
- Auto-generated documentation
- Basic endpoint patterns

**🏗️ Tutorial B: [E-Commerce Foundation](01-getting-started/apply-ecommerce.md)**
- E-commerce API structure
- Health checks and API info
- Configuration system setup
- Professional project foundation

---

### [Chapter 2: Data Models & Validation](02-data-models/)
**📖 Tutorial A: [Pydantic Fundamentals](02-data-models/learn-pydantic.md)**
- Creating data models
- Request/Response validation
- Error handling basics
- Type hints and validation

**🏗️ Tutorial B: [User Management System](02-data-models/apply-user-system.md)**
- User registration models
- Profile management
- Input validation for e-commerce
- Error responses for user operations

---

### [Chapter 3: CRUD Operations](03-crud-operations/)
**📖 Tutorial A: [HTTP Methods & CRUD](03-crud-operations/learn-crud.md)**
- GET, POST, PUT, DELETE operations
- Request body handling
- HTTP status codes
- In-memory data operations

**🏗️ Tutorial B: [User CRUD Operations](03-crud-operations/apply-user-crud.md)**
- User creation and management
- Profile updates and retrieval
- User deletion and status management
- Business logic implementation

---

### [Chapter 4: Database Integration](04-database-integration/)
**📖 Tutorial A: [Database Basics](04-database-integration/learn-database.md)**
- SQLModel introduction
- Database connections
- Basic queries and relationships
- Migration concepts

**🏗️ Tutorial B: [User Data Persistence](04-database-integration/apply-user-persistence.md)**
- PostgreSQL setup for e-commerce
- User model database integration
- User authentication data storage
- Database configuration management

---

### [Chapter 5: Product Catalog](05-product-catalog/)
**📖 Tutorial A: [File Uploads & Search](05-product-catalog/learn-files-search.md)**
- File upload handling
- Search and filtering patterns
- Data relationships
- Query optimization basics

**🏗️ Tutorial B: [Product Management](05-product-catalog/apply-product-system.md)**
- Product and category models
- Product image uploads
- Catalog search and filtering
- Inventory management basics

---

### [Chapter 6: Order Processing](06-order-processing/)
**📖 Tutorial A: [Complex Data Relations](06-order-processing/learn-relations.md)**
- One-to-many relationships
- Business logic patterns
- Transaction concepts
- Data consistency

**🏗️ Tutorial B: [Shopping Cart & Orders](06-order-processing/apply-order-system.md)**
- Shopping cart implementation
- Order creation and processing
- Order tracking system
- Payment preparation

---

### [Chapter 7: Authentication & Security](07-auth-security/)
**📖 Tutorial A: [JWT & Security Basics](07-auth-security/learn-auth.md)**
- JWT token creation and validation
- Password hashing
- Protected endpoints
- Security middleware

**🏗️ Tutorial B: [E-Commerce Authentication](07-auth-security/apply-ecommerce-auth.md)**
- User login and registration
- Protected user and admin endpoints
- Order authorization
- Security best practices

---

### [Chapter 8: Production & Advanced](08-production/)
**📖 Tutorial A: [Testing & Monitoring](08-production/learn-testing.md)**
- Unit and integration testing
- API testing strategies
- Logging and monitoring
- Performance basics

**🏗️ Tutorial B: [E-Commerce Production](08-production/apply-production.md)**
- Complete e-commerce testing
- Customer support system
- Production configuration
- Deployment preparation

</details>

<details>
<summary><strong>🚀 Quick Start</strong></summary>

### Method 1: Using VS Code (Recommended)

1. **Download this tutorial:**
   - Download ZIP from GitHub (green "Code" button → "Download ZIP")
   - Extract the ZIP file to your desired location

2. **Open in VS Code:**
   ```bash
   # Open VS Code in the tutorial directory
   code fastapi-ecommerce-tutorial
   ```
   
3. **Set up Python environment in VS Code:**
   - Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
   - Type "Python: Create Environment"
   - Select "Venv" → Choose your Python interpreter
   - VS Code will create and activate the virtual environment

4. **Install FastAPI:**
   - Open VS Code terminal (`Ctrl+`` ` or `Cmd+`` `)
   - Install dependencies:
     ```bash
     pip install "fastapi[standard]"
     ```

5. **Configure VS Code for FastAPI development:**
   - Install the Python extension (if not already installed)
   - Install the "Thunder Client" extension for API testing (optional)
   - VS Code will automatically detect your FastAPI app

6. **Start developing:**
   - Create your first API following Chapter 1
   - Run with: `python -m uvicorn app.main:app --reload`
   - VS Code will show the server output in the terminal

### Method 2: Command Line Setup

1. **Create project directory:**
   ```bash
   mkdir fastapi-ecommerce-tutorial
   cd fastapi-ecommerce-tutorial
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install FastAPI:**
   ```bash
   pip install "fastapi[standard]"
   ```

4. **Choose your learning path:**
   ```bash
   # Path A: Learn concepts with simple examples
   cd examples/01-hello-world
   python main.py
   
   # Path B: Build the e-commerce application
   cd ecommerce-app
   python -m uvicorn app.main:app --reload
   
   # Path C: Start with concepts first, then apply
   # Follow both tutorials sequentially
   ```

### 🌐 Access Your API

- **API Endpoint**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

### 💡 VS Code Tips for FastAPI Development

- **Auto-completion**: VS Code provides excellent IntelliSense for FastAPI
- **Debugging**: Set breakpoints and debug your API endpoints
- **Integrated Terminal**: Run commands without leaving the editor
- **Extensions**: Install Python, Pylance, and Thunder Client for the best experience
- **Configuration**: Easily modify settings in `config.yaml` without changing code

### ⚙️ Easy Configuration

This tutorial uses a YAML-based configuration system for maximum flexibility:

**Quick Settings Change:**
```yaml
# config.yaml - Change server port easily
server:
  host: "127.0.0.1"
  port: 3000  # Changed from 8000 to 3000

# Change database settings  
database:
  host: "localhost"
  name: "my_custom_db_name"
```

**No Code Changes Required** - Just edit `config.yaml` and restart your server!

</details>

<details>
<summary><strong>📁 Modular Project Structure</strong></summary>

This tutorial is organized into **two parallel tracks** for maximum flexibility:

```
fastapi-ecommerce-tutorial/
├── README.md                           # Main guide with learning paths
│
├── 📚 docs/                            # Tutorial documentation
│   ├── 01-getting-started/
│   │   ├── learn-basics.md            # Tutorial A: FastAPI fundamentals
│   │   └── apply-ecommerce.md         # Tutorial B: E-commerce foundation
│   ├── 02-data-models/
│   │   ├── learn-pydantic.md          # Tutorial A: Pydantic basics
│   │   └── apply-user-system.md       # Tutorial B: User models
│   ├── 03-crud-operations/
│   │   ├── learn-crud.md              # Tutorial A: HTTP methods
│   │   └── apply-user-crud.md         # Tutorial B: User operations
│   └── ... (remaining chapters follow same pattern)
│
├── 🧪 examples/                        # Tutorial A: Simple learning examples
│   ├── 01-hello-world/
│   │   ├── main.py                    # Basic FastAPI hello world
│   │   └── README.md                  # How to run this example
│   ├── 02-pydantic-models/
│   │   ├── models_demo.py             # Pydantic model examples
│   │   └── README.md
│   ├── 03-crud-basics/
│   │   ├── crud_demo.py               # Basic CRUD operations
│   │   └── README.md
│   └── ... (simple examples for each concept)
│
├── 🛍️ ecommerce-app/                   # Tutorial B: Complete e-commerce application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # Main FastAPI application
│   │   ├── database.py                # Database configuration
│   │   ├── config.py                  # Configuration loader
│   │   ├── models/                    # Database models (SQLModel)
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User models and relationships
│   │   │   ├── product.py            # Product and category models
│   │   │   ├── order.py              # Order and cart models
│   │   │   └── support.py            # Customer support models
│   │   ├── routers/                   # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── users.py              # User management endpoints
│   │   │   ├── products.py           # Product catalog endpoints
│   │   │   ├── orders.py             # Order processing endpoints
│   │   │   └── support.py            # Customer support endpoints
│   │   ├── schemas/                   # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User API schemas
│   │   │   ├── product.py            # Product API schemas
│   │   │   ├── order.py              # Order API schemas
│   │   │   └── support.py            # Support API schemas
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Authentication logic
│   │   │   ├── user_service.py       # User business logic
│   │   │   ├── product_service.py    # Product business logic
│   │   │   └── order_service.py      # Order processing logic
│   │   └── utils/                     # Utility functions
│   │       ├── __init__.py
│   │       ├── security.py           # Security utilities
│   │       ├── validators.py         # Custom validators
│   │       └── helpers.py            # Common helpers
│   ├── tests/                         # Comprehensive test suite
│   │   ├── __init__.py
│   │   ├── conftest.py               # Test configuration
│   │   ├── test_users.py             # User API tests
│   │   ├── test_products.py          # Product API tests
│   │   ├── test_orders.py            # Order API tests
│   │   └── test_auth.py              # Authentication tests
│   ├── config.yaml                   # E-commerce configuration
│   ├── requirements.txt              # E-commerce dependencies
│   └── README.md                     # E-commerce app guide
│
├── ⚙️ Configuration & Dependencies
│   ├── config.yaml                   # Shared configuration template
│   ├── requirements.txt              # Base dependencies for both tracks
│   ├── requirements-dev.txt          # Development dependencies
│   └── .gitignore                   # Git ignore rules
```

### 🎯 **How to Use This Structure**

**📖 Tutorial A Learners (Concepts Only):**
- Focus on `examples/` directory
- Follow `docs/*/learn-*.md` files
- Run simple, isolated examples
- Perfect for quick concept learning

**🏗️ Tutorial B Learners (E-Commerce Project):**
- Focus on `ecommerce-app/` directory  
- Follow `docs/*/apply-*.md` files
- Build a complete, production-ready application
- Perfect for portfolio projects

**🎓 Complete Learners (Both Tracks):**
- Start with Tutorial A for concepts
- Apply knowledge in Tutorial B
- Get both understanding AND practical experience
- Most comprehensive learning path

</details>

<details>
<summary><strong>🛠️ Development Tools & Dependencies</strong></summary>

### Core Framework
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **SQLModel**: SQL database integration (built on SQLAlchemy + Pydantic)
- **PostgreSQL**: Production-ready relational database

### Development & Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: HTTP client for API testing
- **black**: Code formatting
- **isort**: Import sorting
- **mypy**: Static type checking

### Authentication & Security
- **python-jose**: JWT token handling
- **passlib**: Password hashing
- **bcrypt**: Secure password hashing algorithm

</details>

<details>
<summary><strong>🤝 How to Contribute</strong></summary>

We welcome contributions to improve this learning resource!

### Ways to Contribute:
- 🐛 **Report Issues**: Found a bug or unclear explanation?
- 📖 **Improve Documentation**: Make tutorials clearer
- 💡 **Suggest Features**: Ideas for additional topics
- 🔧 **Code Examples**: Better examples or additional exercises
- 🌍 **Translations**: Help make this accessible globally

### Contribution Process:
1. Fork this repository
2. Create a feature branch
3. Make your improvements
4. Test your changes
5. Submit a pull request

</details>

<details>
<summary><strong>🆘 Getting Help</strong></summary>

### Community Support:
- **GitHub Issues**: Report bugs or ask questions
- **Discussions**: Share your projects and get feedback
- **Stack Overflow**: Tag your questions with `fastapi-tutorial`

### Additional Resources:
- [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

</details>

<details>
<summary><strong>📅 Learning Schedule Suggestions</strong></summary>

### 🚀 **Intensive Weekend (16 hours)**
- **Day 1**: Chapters 1-4 (8 hours)
- **Day 2**: Chapters 5-8 (8 hours)

### 📚 **Part-time Learning (4 weeks)**
- **Week 1**: Chapters 1-2 (4 hours)
- **Week 2**: Chapters 3-4 (4 hours)
- **Week 3**: Chapters 5-6 (6 hours)
- **Week 4**: Chapters 7-8 (4 hours)

### 🎓 **Study Group Format (8 weeks)**
- **Weekly 2-hour sessions**
- One chapter per week
- Group coding and discussion

</details>

<details>
<summary><strong>🏆 Learning Outcomes</strong></summary>

After completing this tutorial, you will be able to:

✅ **Design and build RESTful APIs** using FastAPI  
✅ **Integrate PostgreSQL databases** with proper ORM usage  
✅ **Implement authentication and authorization** systems  
✅ **Write comprehensive tests** for API applications  
✅ **Handle file uploads and data validation**  
✅ **Deploy applications locally** with production configurations  
✅ **Follow API best practices** and security guidelines  
✅ **Structure large applications** for maintainability  
✅ **Debug and optimize** FastAPI applications  
✅ **Build real-world e-commerce features**  

</details>

<details>
<summary><strong>📝 License</strong></summary>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

</details>

<details>
<summary><strong>🙏 Acknowledgments</strong></summary>

- FastAPI team for creating an amazing framework
- The Python community for excellent libraries
- All contributors who help improve this resource

</details>

---

**Ready to start your FastAPI journey? Begin with [Chapter 1: Getting Started](01-getting-started/)!** 🚀