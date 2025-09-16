# Database Integration Fundamentals

**Learn database operations with SQLModel through a Contact Book API** 📞

This example demonstrates essential database integration concepts using FastAPI and SQLModel with SQLite. Perfect for understanding database operations, sessions, and SQL queries before moving to complex relationships.

## 🎯 What You'll Learn

- **SQLModel Basics**: Database models that work with FastAPI
- **Database Sessions**: Managing database connections properly
- **CRUD with Database**: Create, Read, Update, Delete with real persistence
- **SQL Queries**: Filtering, searching, and pagination with databases
- **Dependency Injection**: Using FastAPI's dependency system for database sessions
- **Transaction Management**: Commits, rollbacks, and data integrity
- **Database Migrations**: Creating tables and managing schema changes
- **Error Handling**: Database-specific error scenarios

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- Understanding concepts: 30 minutes
- Hands-on practice: 45 minutes
- Database exploration: 15 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]" sqlmodel
```

### Run the Example

```bash
# Navigate to this directory
cd examples/04-database-simple

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Contact List**: http://localhost:8000/contacts
- **Statistics**: http://localhost:8000/contacts/stats
- **Database Info**: http://localhost:8000/database/info

## 📚 Key Concepts Explained

### 1. SQLModel vs Pydantic

| Feature | Pydantic | SQLModel |
|---------|----------|----------|
| **Purpose** | Data validation | Database + validation |
| **Database** | ❌ No | ✅ Yes |
| **FastAPI** | ✅ Native | ✅ Native |
| **SQL Queries** | ❌ No | ✅ Yes |
| **Relationships** | ❌ Limited | ✅ Full support |

### 2. Database Models

```python
class Contact(ContactBase, table=True):
    """SQLModel that creates a database table."""
    __tablename__ = "contacts"  # Table name in database
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Database Sessions

```python
def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session

@app.get("/contacts")
async def get_contacts(session: Session = Depends(get_session)):
    # session is automatically provided and closed
```

### 4. SQL Queries with SQLModel

```python
# Simple select
query = select(Contact)

# With filtering
query = select(Contact).where(Contact.contact_type == "business")

# With search
query = select(Contact).where(Contact.first_name.contains("john"))

# With pagination
query = select(Contact).offset(skip).limit(limit)

# Execute query
contacts = session.exec(query).all()
```

## 🎮 Hands-On Exercises

### Exercise 1: Basic Database Operations

1. **Create a Contact**:
   ```bash
   curl -X POST "http://localhost:8000/contacts" \
        -H "Content-Type: application/json" \
        -d '{
          "first_name": "Jane",
          "last_name": "Doe",
          "email": "jane.doe@example.com",
          "phone": "+1-555-999-0000",
          "contact_type": "business",
          "company": "Innovation Corp",
          "notes": "Lead developer"
        }'
   ```

2. **List All Contacts**:
   ```bash
   curl "http://localhost:8000/contacts"
   ```

3. **Search Contacts**:
   ```bash
   curl "http://localhost:8000/contacts?search=jane"
   ```

4. **Filter by Type**:
   ```bash
   curl "http://localhost:8000/contacts?contact_type=business"
   ```

5. **Get Single Contact**:
   ```bash
   curl "http://localhost:8000/contacts/1"
   ```

### Exercise 2: Advanced Database Queries

1. **Company-based Search**:
   ```bash
   curl "http://localhost:8000/contacts/company/tech"
   ```

2. **Complex Search**:
   ```bash
   curl "http://localhost:8000/contacts/search/john"
   ```

3. **Pagination**:
   ```bash
   curl "http://localhost:8000/contacts?limit=2&skip=0"  # First 2
   curl "http://localhost:8000/contacts?limit=2&skip=2"  # Next 2
   ```

4. **Combined Filters**:
   ```bash
   curl "http://localhost:8000/contacts?contact_type=business&company=corp&limit=10"
   ```

### Exercise 3: Database Administration

1. **View Statistics**:
   ```bash
   curl "http://localhost:8000/contacts/stats"
   ```

2. **Database Health Check**:
   ```bash
   curl "http://localhost:8000/health"
   ```

3. **Reset Sample Data**:
   ```bash
   curl -X POST "http://localhost:8000/contacts/reset"
   ```

4. **Database Info**:
   ```bash
   curl "http://localhost:8000/database/info"
   ```

## 🔍 Code Structure Walkthrough

### 1. Database Setup

```python
# Database URL
DATABASE_URL = "sqlite:///database/contacts.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

### 2. Session Management

```python
def get_session():
    """Dependency that provides database session."""
    with Session(engine) as session:
        yield session  # Session is automatically closed after request
```

### 3. Database Models

```python
class Contact(ContactBase, table=True):
    """Database table model."""
    __tablename__ = "contacts"
    
    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamps (automatically managed)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. CRUD Operations

**Create**:
```python
@app.post("/contacts")
async def create_contact(contact_data: ContactCreate, session: Session = Depends(get_session)):
    db_contact = Contact(**contact_data.dict())
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)  # Get generated ID
    return db_contact
```

**Read**:
```python
@app.get("/contacts")
async def get_contacts(session: Session = Depends(get_session)):
    statement = select(Contact)
    contacts = session.exec(statement).all()
    return contacts
```

**Update**:
```python
@app.put("/contacts/{contact_id}")
async def update_contact(contact_id: int, contact_data: ContactCreate, session: Session = Depends(get_session)):
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(404, "Contact not found")
    
    # Update fields
    for field, value in contact_data.dict().items():
        setattr(db_contact, field, value)
    
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    return db_contact
```

**Delete**:
```python
@app.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(404, "Contact not found")
    
    session.delete(db_contact)
    session.commit()
    return {"message": "Contact deleted"}
```

## 🎯 Database Features Demonstrated

### 1. **Filtering and Search**
```python
# Filter by enum value
query = select(Contact).where(Contact.contact_type == ContactType.BUSINESS)

# Text search (case-insensitive)
query = select(Contact).where(Contact.company.ilike(f"%{company_name}%"))

# Multiple field search with OR
query = select(Contact).where(
    Contact.first_name.contains(search_term) |
    Contact.last_name.contains(search_term) |
    Contact.email.contains(search_term)
)
```

### 2. **Pagination**
```python
query = select(Contact).offset(skip).limit(limit)
```

### 3. **Ordering**
```python
query = select(Contact).order_by(Contact.created_at.desc())
```

### 4. **Aggregation**
```python
# Count records
total = len(session.exec(select(Contact)).all())

# Conditional counting
business_contacts = len(session.exec(
    select(Contact).where(Contact.contact_type == ContactType.BUSINESS)
).all())
```

## 🗂️ Database File Structure

```
examples/04-database-simple/
├── main.py              # Main application
├── README.md           # This file
└── database/           # Database directory (auto-created)
    └── contacts.db     # SQLite database file
```

The SQLite database file is automatically created when you run the application for the first time.

## 🧪 Testing Your Understanding

### Challenge 1: Add Address Fields
Extend the Contact model with address fields:
- `street_address: Optional[str]`
- `city: Optional[str]`
- `state: Optional[str]`
- `postal_code: Optional[str]`
- `country: str = "USA"`

### Challenge 2: Add Custom Queries
Create these additional endpoints:
- `GET /contacts/no-email` - Find contacts without email
- `GET /contacts/recent/{days}` - Contacts created in last N days
- `GET /contacts/by-first-letter/{letter}` - Contacts by first name initial

### Challenge 3: Add Data Validation
Implement custom validation:
- Email format validation
- Phone number format validation
- Name capitalization (auto-format)
- Company name deduplication

### Challenge 4: Add Soft Delete
Implement soft delete functionality:
- Add `is_deleted: bool` field
- Modify queries to exclude deleted contacts
- Add `restore` endpoint to undelete contacts

## 🔗 What's Next?

After mastering database fundamentals, you're ready for:

1. **File Handling** (Example 05) - Upload and manage files with database references
2. **Relationships** (Example 06) - Connect related data with foreign keys
3. **Authentication** (Example 07) - Protect your database with user authentication
4. **Testing** (Example 08) - Test database operations properly

## 💡 Key Takeaways

- **SQLModel = SQLAlchemy + Pydantic** - Best of both worlds
- **Sessions manage connections** - Always use dependency injection
- **Queries are composable** - Build complex queries step by step
- **Transactions are automatic** - session.commit() saves changes
- **Type safety everywhere** - SQLModel provides full type checking

## 🐛 Common Pitfalls

1. **Forgetting session.commit()**: Changes won't be saved without commit
2. **Not using dependencies**: Always inject sessions via Depends()
3. **Missing error handling**: Always check if records exist before operations
4. **Forgetting session.refresh()**: Won't see auto-generated IDs without refresh
5. **Not closing sessions**: Use dependency injection to handle automatically

## 🔧 Database Tools

### View Your Database
You can inspect your SQLite database using:

1. **SQLite Browser**: Download DB Browser for SQLite
2. **Command Line**: 
   ```bash
   sqlite3 database/contacts.db
   .tables
   .schema contacts
   SELECT * FROM contacts;
   ```

3. **Python Script**:
   ```python
   from sqlmodel import create_engine, Session, select
   from main import Contact
   
   engine = create_engine("sqlite:///database/contacts.db")
   with Session(engine) as session:
       contacts = session.exec(select(Contact)).all()
       for contact in contacts:
           print(f"{contact.first_name} {contact.last_name}")
   ```

---

**Ready to handle file uploads? Continue with [Example 05: File Handling](../05-file-handling/)!** 📁