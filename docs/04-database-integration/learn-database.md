# Tutorial A4: Database Integration with SQLModel

**Add real persistence to your APIs with SQLModel and SQLite** 📊

In this tutorial, you'll learn how to integrate databases into your FastAPI applications using SQLModel. SQLModel combines the power of SQLAlchemy (database ORM) with Pydantic (data validation), making it perfect for FastAPI projects.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ What SQLModel is and why it's perfect for FastAPI
- ✅ How to define database models with SQLModel
- ✅ Database connection and session management
- ✅ CRUD operations with real database persistence
- ✅ SQL queries, filtering, and searching
- ✅ FastAPI dependency injection for database sessions
- ✅ Database transactions and error handling

## 🧠 Why SQLModel?

### **The Perfect Match for FastAPI**

SQLModel was created by the same author as FastAPI and is specifically designed to work seamlessly with it:

```python
from sqlmodel import SQLModel, Field

# This model works as BOTH:
# 1. A database table (like SQLAlchemy)
# 2. A Pydantic model (for validation and serialization)
class Contact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
```

**Benefits:**
- 🎯 **Single Model Definition** - One model for database AND API
- ✅ **Type Safety** - Full type hints and IDE support
- 📚 **Auto Documentation** - Works with FastAPI's automatic docs
- 🔍 **Validation** - Pydantic validation built-in
- 💪 **Powerful ORM** - SQLAlchemy under the hood

### **SQLModel vs Alternatives**

| Feature | SQLModel | SQLAlchemy + Pydantic | Django ORM |
|---------|----------|----------------------|------------|
| Type hints | ✅ Excellent | ⚠️ Separate models | ❌ Limited |
| FastAPI integration | ✅ Native | ⚠️ Manual work | ❌ Not designed for it |
| Learning curve | ✅ Easy | ⚠️ Moderate | ⚠️ Steep |
| Code duplication | ✅ None | ❌ Duplicate models | ✅ None |

## 🏗️ Database Fundamentals

### **1. Installing Dependencies**

```bash
pip install sqlmodel
```

That's it! SQLModel includes everything you need.

### **2. Creating Database Models**

```python
from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
from datetime import datetime

class Contact(SQLModel, table=True):
    """
    Contact database model.

    This class serves dual purposes:
    - Database table schema (table=True)
    - Pydantic model for validation
    """

    # Primary key with auto-increment
    id: Optional[int] = Field(default=None, primary_key=True)

    # Required fields
    name: str = Field(index=True)  # index=True for faster queries
    email: str = Field(unique=True)  # unique=True prevents duplicates

    # Optional fields
    phone: Optional[str] = None
    notes: Optional[str] = None

    # Metadata fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Field validation example
    age: int = Field(ge=0, le=150)  # Between 0 and 150
```

**Key Concepts:**
- `table=True` makes this a database table
- `Field()` adds constraints and metadata
- Type hints provide automatic validation
- `Optional` fields can be None
- Indexes speed up queries on that field
- Unique constraints prevent duplicates

### **3. Database Connection Setup**

```python
from sqlmodel import create_engine, SQLModel

# SQLite database (file-based, perfect for development)
DATABASE_URL = "sqlite:///./database.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log all SQL queries (useful for learning)
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
```

**Database URL Formats:**
```python
# SQLite (local file)
"sqlite:///./database.db"

# PostgreSQL (production)
"postgresql://user:password@localhost/dbname"

# MySQL
"mysql://user:password@localhost/dbname"
```

### **4. Database Sessions**

Sessions manage your database connections and transactions:

```python
from sqlmodel import Session

def get_session():
    """
    Dependency that provides database session.

    FastAPI will automatically call this function
    and inject the session into your endpoint.
    """
    with Session(engine) as session:
        yield session
```

**Using sessions in endpoints:**
```python
from fastapi import Depends

@app.get("/contacts")
def get_contacts(session: Session = Depends(get_session)):
    # session is automatically provided by FastAPI
    contacts = session.exec(select(Contact)).all()
    return contacts
```

## 📝 Complete Database CRUD Example

### **Full Application Structure**

```python
from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
from datetime import datetime

# ==================== Models ====================

class ContactBase(SQLModel):
    """Base model with common fields"""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = None

class Contact(ContactBase, table=True):
    """Database model (includes ID and timestamps)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ContactCreate(ContactBase):
    """Model for creating contacts (no ID needed)"""
    pass

class ContactUpdate(ContactBase):
    """Model for updating contacts"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = None

# ==================== Database Setup ====================

DATABASE_URL = "sqlite:///./contacts.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# ==================== FastAPI App ====================

app = FastAPI(title="Contact Book API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ==================== CRUD Endpoints ====================

# CREATE
@app.post("/contacts", response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: ContactCreate,
    session: Session = Depends(get_session)
):
    """Create a new contact"""
    # Check if email already exists
    existing = session.exec(
        select(Contact).where(Contact.email == contact.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists"
        )

    # Create new contact
    db_contact = Contact.from_orm(contact)
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)  # Get the ID from database

    return db_contact

# READ - All contacts
@app.get("/contacts", response_model=List[Contact])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """Get all contacts with pagination"""
    contacts = session.exec(
        select(Contact).offset(skip).limit(limit)
    ).all()
    return contacts

# READ - Single contact
@app.get("/contacts/{contact_id}", response_model=Contact)
def get_contact(
    contact_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific contact by ID"""
    contact = session.get(Contact, contact_id)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )

    return contact

# UPDATE
@app.patch("/contacts/{contact_id}", response_model=Contact)
def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    session: Session = Depends(get_session)
):
    """Update a contact"""
    # Get existing contact
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )

    # Update only provided fields
    update_data = contact_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    contact.updated_at = datetime.now()

    session.add(contact)
    session.commit()
    session.refresh(contact)

    return contact

# DELETE
@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    session: Session = Depends(get_session)
):
    """Delete a contact"""
    contact = session.get(Contact, contact_id)

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )

    session.delete(contact)
    session.commit()

    return None

# SEARCH
@app.get("/contacts/search/", response_model=List[Contact])
def search_contacts(
    q: str,
    session: Session = Depends(get_session)
):
    """Search contacts by name or email"""
    contacts = session.exec(
        select(Contact).where(
            (Contact.name.contains(q)) | (Contact.email.contains(q))
        )
    ).all()
    return contacts
```

## 🔍 Advanced Queries

### **Filtering**

```python
# Filter by exact match
contacts = session.exec(
    select(Contact).where(Contact.name == "John Doe")
).all()

# Filter with multiple conditions (AND)
contacts = session.exec(
    select(Contact).where(
        Contact.name == "John",
        Contact.email.contains("@example.com")
    )
).all()

# Filter with OR conditions
from sqlmodel import or_

contacts = session.exec(
    select(Contact).where(
        or_(
            Contact.name.contains("John"),
            Contact.email.contains("john")
        )
    )
).all()
```

### **Sorting**

```python
# Sort by name ascending
contacts = session.exec(
    select(Contact).order_by(Contact.name)
).all()

# Sort by created_at descending (newest first)
contacts = session.exec(
    select(Contact).order_by(Contact.created_at.desc())
).all()

# Multiple sort orders
contacts = session.exec(
    select(Contact).order_by(Contact.name, Contact.created_at.desc())
).all()
```

### **Counting**

```python
from sqlmodel import func

# Count all contacts
count = session.exec(
    select(func.count()).select_from(Contact)
).one()

# Count with filter
count = session.exec(
    select(func.count()).select_from(Contact).where(
        Contact.email.contains("@gmail.com")
    )
).one()
```

### **Pagination**

```python
@app.get("/contacts")
def get_contacts(
    page: int = 1,
    size: int = 10,
    session: Session = Depends(get_session)
):
    skip = (page - 1) * size

    # Get total count
    total = session.exec(select(func.count()).select_from(Contact)).one()

    # Get paginated results
    contacts = session.exec(
        select(Contact).offset(skip).limit(size)
    ).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": contacts
    }
```

## 🎯 Database Best Practices

### **1. Always Use Sessions Properly**

✅ **Good - Using dependency injection:**
```python
@app.get("/contacts")
def get_contacts(session: Session = Depends(get_session)):
    return session.exec(select(Contact)).all()
```

❌ **Bad - Creating session manually:**
```python
@app.get("/contacts")
def get_contacts():
    session = Session(engine)  # Don't do this!
    contacts = session.exec(select(Contact)).all()
    # Session never closed = memory leak!
    return contacts
```

### **2. Handle Transactions**

```python
@app.post("/contacts/bulk")
def create_bulk_contacts(
    contacts: List[ContactCreate],
    session: Session = Depends(get_session)
):
    try:
        for contact_data in contacts:
            db_contact = Contact.from_orm(contact_data)
            session.add(db_contact)

        session.commit()  # All or nothing
        return {"created": len(contacts)}

    except Exception as e:
        session.rollback()  # Undo all changes
        raise HTTPException(500, detail=str(e))
```

### **3. Validate Before Database Operations**

```python
@app.post("/contacts")
def create_contact(
    contact: ContactCreate,  # Pydantic validates first!
    session: Session = Depends(get_session)
):
    # Additional business logic validation
    if "@" not in contact.email:
        raise HTTPException(400, "Invalid email format")

    # Now save to database
    db_contact = Contact.from_orm(contact)
    session.add(db_contact)
    session.commit()
    return db_contact
```

### **4. Use Indexes for Performance**

```python
class Contact(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    email: str = Field(index=True, unique=True)  # Fast lookups!
    name: str = Field(index=True)  # Indexed for searches
    phone: Optional[str] = None  # Not indexed (rarely searched)
```

## 🧪 Testing Database Operations

### **Using the Interactive Docs**

1. **Create some contacts:**
   - POST `/contacts` multiple times
   - Try duplicate emails (should fail)

2. **Query and search:**
   - GET `/contacts` - See all
   - GET `/contacts/search/?q=john` - Search
   - GET `/contacts/1` - Get specific

3. **Update and delete:**
   - PATCH `/contacts/1` - Update
   - DELETE `/contacts/1` - Remove

### **Check the Database File**

```bash
# Install SQLite browser
# Then open your database.db file to see the data!
```

## 🎯 Practice Challenges

### **Challenge 1: Blog Posts Database**
Create a database-backed blog API:
- Post model with title, content, author, published
- CRUD operations
- Search posts by title/content
- Filter by published status
- Sort by date

### **Challenge 2: Inventory System**
Build a product inventory with:
- Product model with name, sku, quantity, price
- Low stock alerts (quantity < 10)
- Search by SKU or name
- Update stock levels
- Track last restocked date

### **Challenge 3: Advanced Queries**
Add to the contact API:
- Get contacts created this week
- Get contacts with most recent activity
- Aggregate statistics (total contacts, by email domain)

## ❓ Troubleshooting

**Q: My database file is locked!**
A: Make sure you're not opening the database in another program. Close all sessions properly.

**Q: Changes aren't persisting!**
A: Don't forget to call `session.commit()` after making changes!

**Q: How do I reset my database?**
A: Delete the `.db` file and restart your app. Tables will be recreated.

**Q: Should I use SQLite in production?**
A: No! SQLite is great for development and learning, but use PostgreSQL or MySQL for production.

## ➡️ What's Next?

Now that you understand databases, let's learn about relationships!

**🎯 Continue Path A - Concept Examples:**
1. **[Example 04: Database Simple](../../examples/04-database-simple/)** - Practice what you learned
2. **[Chapter 5: File Handling & Search](../05-product-catalog/learn-files-search.md)** - File uploads
3. **[Chapter 6: Data Relationships](../06-order-processing/learn-relations.md)** - Connect tables

**🏗️ Or Switch to Path B:**
Jump to **[Tutorial B4: Database Integration](apply-user-persistence.md)** to add PostgreSQL to your e-commerce app!

---

## 📚 Summary

**What you learned:**
- ✅ SQLModel fundamentals and setup
- ✅ Database model definitions with Field constraints
- ✅ Database connections and session management
- ✅ CRUD operations with real persistence
- ✅ SQL queries, filtering, sorting, pagination
- ✅ FastAPI dependency injection for sessions
- ✅ Transaction handling and best practices

**Key takeaways:**
1. SQLModel combines SQLAlchemy and Pydantic perfectly
2. Always use dependency injection for sessions
3. Commit transactions to persist changes
4. Use indexes for frequently queried fields
5. Handle errors and validate before database operations

Excellent work! You now know how to persist data in databases. 🎉

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A4*
