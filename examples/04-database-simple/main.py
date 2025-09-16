"""
Database Integration Fundamentals - Contact Book API
====================================================

This example demonstrates basic database integration with FastAPI using SQLModel.
Learn how to connect to SQLite database, create tables, and perform database
operations while maintaining the same API patterns from previous examples.

Key Concepts Demonstrated:
- SQLModel for database models and operations
- SQLite database setup and connection
- Database sessions and dependency injection
- SQL queries with SQLModel
- Database migrations and table creation
- Error handling with database operations

Author: bug6129
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
import os

# Create FastAPI app
app = FastAPI(
    title="Database Fundamentals - Contact Book",
    description="Learn database integration through a simple contact management API",
    version="1.0.0"
)

# =============================================================================
# 1. DATABASE MODELS - SQLModel Integration
# =============================================================================

class ContactType(str, Enum):
    """Contact type enumeration."""
    PERSONAL = "personal"
    BUSINESS = "business"
    FAMILY = "family"
    FRIEND = "friend"

class ContactBase(SQLModel):
    """Base contact model with shared fields."""
    first_name: str = Field(..., description="Contact's first name", max_length=50)
    last_name: str = Field(..., description="Contact's last name", max_length=50)
    email: Optional[str] = Field(None, description="Email address", max_length=255)
    phone: Optional[str] = Field(None, description="Phone number", max_length=20)
    contact_type: ContactType = Field(default=ContactType.PERSONAL, description="Type of contact")
    company: Optional[str] = Field(None, description="Company name", max_length=100)
    notes: Optional[str] = Field(None, description="Additional notes", max_length=500)

class Contact(ContactBase, table=True):
    """Contact database table model."""
    
    __tablename__ = "contacts"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique contact ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1-555-123-4567",
                "contact_type": "business",
                "company": "Tech Corp",
                "notes": "Met at tech conference",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:00:00Z"
            }
        }

class ContactCreate(ContactBase):
    """Model for creating new contacts."""
    pass

class ContactUpdate(SQLModel):
    """Model for updating existing contacts (all fields optional)."""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    contact_type: Optional[ContactType] = None
    company: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)

class ContactResponse(ContactBase):
    """Response model for contact data."""
    id: int
    created_at: datetime
    updated_at: datetime

# =============================================================================
# 2. DATABASE SETUP - SQLite Connection
# =============================================================================

# Create database directory if it doesn't exist
DATABASE_DIR = "database"
os.makedirs(DATABASE_DIR, exist_ok=True)

# Database URL (SQLite file)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/contacts.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries in logs
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Database session dependency.
    
    This function provides a database session for each request
    and ensures it's properly closed after use.
    """
    with Session(engine) as session:
        yield session

# Initialize database
create_db_and_tables()

# =============================================================================
# 3. DATABASE OPERATIONS - CRUD with SQLModel
# =============================================================================

def create_sample_contacts(session: Session):
    """Create sample contacts for demonstration."""
    sample_contacts = [
        Contact(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            phone="+1-555-111-2222",
            contact_type=ContactType.BUSINESS,
            company="Design Studio",
            notes="Lead designer, very creative"
        ),
        Contact(
            first_name="Bob",
            last_name="Smith",
            email="bob.smith@personal.com",
            phone="+1-555-333-4444",
            contact_type=ContactType.FRIEND,
            notes="College roommate"
        ),
        Contact(
            first_name="Carol",
            last_name="Williams",
            email="carol@williams.com",
            phone="+1-555-555-6666",
            contact_type=ContactType.FAMILY,
            notes="Sister"
        ),
        Contact(
            first_name="David",
            last_name="Brown",
            email="d.brown@techcorp.com",
            phone="+1-555-777-8888",
            contact_type=ContactType.BUSINESS,
            company="TechCorp",
            notes="Project manager on API development"
        ),
        Contact(
            first_name="Emma",
            last_name="Davis",
            email="emma.davis@startup.com",
            contact_type=ContactType.BUSINESS,
            company="StartupXYZ",
            notes="CEO of promising startup"
        )
    ]
    
    # Check if we already have contacts
    existing_contacts = session.exec(select(Contact)).first()
    if not existing_contacts:
        for contact in sample_contacts:
            session.add(contact)
        session.commit()
        print(f"Created {len(sample_contacts)} sample contacts")

# Create sample data on startup
with Session(engine) as session:
    create_sample_contacts(session)

# =============================================================================
# 4. API ENDPOINTS - Database-Backed CRUD
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API information and available endpoints."""
    return {
        "message": "Contact Book API - Database Fundamentals",
        "description": "Learn database integration through contact management",
        "database": {
            "type": "SQLite",
            "file": DATABASE_URL,
            "tables": ["contacts"]
        },
        "endpoints": {
            "GET /contacts": "List all contacts (with filtering)",
            "POST /contacts": "Create a new contact",
            "GET /contacts/{id}": "Get a specific contact by ID",
            "PUT /contacts/{id}": "Update a contact completely",
            "PATCH /contacts/{id}": "Update specific contact fields",
            "DELETE /contacts/{id}": "Delete a contact"
        },
        "documentation": "/docs"
    }

# =============================================================================
# READ OPERATIONS - Database Queries
# =============================================================================

@app.get("/contacts", response_model=List[ContactResponse], tags=["Contacts"])
async def get_contacts(
    session: Session = Depends(get_session),
    contact_type: Optional[ContactType] = Query(None, description="Filter by contact type"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    search: Optional[str] = Query(None, description="Search in names and email"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of contacts to return"),
    skip: int = Query(0, ge=0, description="Number of contacts to skip")
):
    """
    Get all contacts with optional filtering and pagination.
    
    This endpoint demonstrates:
    - Database queries with SQLModel
    - Optional filtering with WHERE clauses
    - Text search across multiple fields
    - Pagination with LIMIT and OFFSET
    """
    # Start with base query
    query = select(Contact)
    
    # Apply filters
    if contact_type:
        query = query.where(Contact.contact_type == contact_type)
    
    if company:
        query = query.where(Contact.company.contains(company))
    
    if search:
        # Search in first name, last name, and email
        search_filter = (
            Contact.first_name.contains(search) |
            Contact.last_name.contains(search) |
            Contact.email.contains(search)
        )
        query = query.where(search_filter)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    contacts = session.exec(query).all()
    
    return contacts

@app.get("/contacts/{contact_id}", response_model=ContactResponse, tags=["Contacts"])
async def get_contact(contact_id: int, session: Session = Depends(get_session)):
    """
    Get a specific contact by its ID.
    
    This endpoint demonstrates:
    - Single record retrieval by primary key
    - Database session dependency injection
    - 404 error handling for missing records
    """
    contact = session.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    return contact

# =============================================================================
# CREATE OPERATIONS - Database Inserts
# =============================================================================

@app.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, tags=["Contacts"])
async def create_contact(
    contact_data: ContactCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new contact.
    
    This endpoint demonstrates:
    - Database insertion with SQLModel
    - Automatic ID generation
    - Timestamp handling
    - Session commit and refresh
    """
    # Create new contact with timestamps
    db_contact = Contact(
        **contact_data.dict(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Add to session and commit
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)  # Refresh to get the generated ID
    
    return db_contact

# =============================================================================
# UPDATE OPERATIONS - Database Updates
# =============================================================================

@app.put("/contacts/{contact_id}", response_model=ContactResponse, tags=["Contacts"])
async def update_contact_complete(
    contact_id: int,
    contact_data: ContactCreate,
    session: Session = Depends(get_session)
):
    """
    Completely update a contact (replaces all fields).
    
    This endpoint demonstrates:
    - Database record retrieval and update
    - Complete field replacement
    - Timestamp updates
    - Transaction handling
    """
    # Get existing contact
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    # Update all fields
    contact_dict = contact_data.dict()
    for field, value in contact_dict.items():
        setattr(db_contact, field, value)
    
    # Update timestamp
    db_contact.updated_at = datetime.utcnow()
    
    # Commit changes
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    
    return db_contact

@app.patch("/contacts/{contact_id}", response_model=ContactResponse, tags=["Contacts"])
async def update_contact_partial(
    contact_id: int,
    contact_data: ContactUpdate,
    session: Session = Depends(get_session)
):
    """
    Partially update a contact (only provided fields).
    
    This endpoint demonstrates:
    - Selective field updates
    - Handling None/null values properly
    - Excluding unset fields from updates
    """
    # Get existing contact
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    # Update only provided fields
    update_data = contact_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_contact, field, value)
    
    # Update timestamp
    db_contact.updated_at = datetime.utcnow()
    
    # Commit changes
    session.add(db_contact)
    session.commit()
    session.refresh(db_contact)
    
    return db_contact

# =============================================================================
# DELETE OPERATIONS - Database Deletions
# =============================================================================

@app.delete("/contacts/{contact_id}", tags=["Contacts"])
async def delete_contact(contact_id: int, session: Session = Depends(get_session)):
    """
    Delete a contact.
    
    This endpoint demonstrates:
    - Database record deletion
    - Transaction handling
    - Confirmation responses
    """
    # Get contact to delete
    db_contact = session.get(Contact, contact_id)
    if not db_contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with ID {contact_id} not found"
        )
    
    # Store info for response
    contact_name = f"{db_contact.first_name} {db_contact.last_name}"
    
    # Delete from database
    session.delete(db_contact)
    session.commit()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Contact '{contact_name}' has been deleted successfully",
            "deleted_contact_id": contact_id
        }
    )

# =============================================================================
# ADDITIONAL ENDPOINTS - Advanced Database Operations
# =============================================================================

@app.get("/contacts/type/{contact_type}", response_model=List[ContactResponse], tags=["Contacts"])
async def get_contacts_by_type(
    contact_type: ContactType,
    session: Session = Depends(get_session)
):
    """
    Get all contacts of a specific type.
    
    Demonstrates enum-based filtering.
    """
    statement = select(Contact).where(Contact.contact_type == contact_type)
    contacts = session.exec(statement).all()
    return contacts

@app.get("/contacts/company/{company_name}", response_model=List[ContactResponse], tags=["Contacts"])
async def get_contacts_by_company(
    company_name: str,
    session: Session = Depends(get_session)
):
    """
    Get all contacts from a specific company.
    
    Demonstrates case-insensitive string matching.
    """
    statement = select(Contact).where(Contact.company.ilike(f"%{company_name}%"))
    contacts = session.exec(statement).all()
    return contacts

@app.get("/contacts/search/{search_term}", response_model=List[ContactResponse], tags=["Contacts"])
async def search_contacts(
    search_term: str,
    session: Session = Depends(get_session)
):
    """
    Search contacts by name or email.
    
    Demonstrates complex WHERE conditions with OR logic.
    """
    statement = select(Contact).where(
        Contact.first_name.contains(search_term) |
        Contact.last_name.contains(search_term) |
        Contact.email.contains(search_term)
    )
    contacts = session.exec(statement).all()
    return contacts

@app.get("/contacts/stats", tags=["Statistics"])
async def get_contact_statistics(session: Session = Depends(get_session)):
    """
    Get contact statistics.
    
    Demonstrates database aggregation and counting.
    """
    # Count total contacts
    total_contacts = len(session.exec(select(Contact)).all())
    
    if total_contacts == 0:
        return {"message": "No contacts found"}
    
    # Count by type
    type_counts = {}
    for contact_type in ContactType:
        count = len(session.exec(
            select(Contact).where(Contact.contact_type == contact_type)
        ).all())
        type_counts[contact_type.value] = count
    
    # Count contacts with companies
    contacts_with_company = len(session.exec(
        select(Contact).where(Contact.company.isnot(None))
    ).all())
    
    # Count contacts with email
    contacts_with_email = len(session.exec(
        select(Contact).where(Contact.email.isnot(None))
    ).all())
    
    # Find most recent contact
    recent_contact = session.exec(
        select(Contact).order_by(Contact.created_at.desc()).limit(1)
    ).first()
    
    return {
        "total_contacts": total_contacts,
        "type_breakdown": type_counts,
        "contacts_with_company": contacts_with_company,
        "contacts_with_email": contacts_with_email,
        "most_recent_contact": f"{recent_contact.first_name} {recent_contact.last_name}" if recent_contact else None,
        "database_file": DATABASE_URL
    }

@app.delete("/contacts", tags=["Contacts"])
async def delete_all_contacts(session: Session = Depends(get_session)):
    """
    Delete all contacts (bulk operation).
    
    Demonstrates bulk deletion.
    """
    # Get count before deletion
    contacts = session.exec(select(Contact)).all()
    deleted_count = len(contacts)
    
    # Delete all contacts
    for contact in contacts:
        session.delete(contact)
    
    session.commit()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"All {deleted_count} contacts have been deleted",
            "deleted_count": deleted_count
        }
    )

@app.post("/contacts/reset", tags=["Contacts"])
async def reset_contacts(session: Session = Depends(get_session)):
    """
    Reset to sample data.
    
    Useful for testing and demonstrations.
    """
    # Delete all existing contacts
    contacts = session.exec(select(Contact)).all()
    for contact in contacts:
        session.delete(contact)
    session.commit()
    
    # Create sample contacts
    create_sample_contacts(session)
    
    # Count new contacts
    new_count = len(session.exec(select(Contact)).all())
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Contacts reset to sample data",
            "total_contacts": new_count
        }
    )

# Health check with database info
@app.get("/health", tags=["System"])
async def health_check(session: Session = Depends(get_session)):
    """Health check endpoint with database connectivity."""
    try:
        # Test database connection
        contact_count = len(session.exec(select(Contact)).all())
        
        return {
            "status": "healthy",
            "service": "Contact Book API - Database Fundamentals",
            "database": {
                "status": "connected",
                "type": "SQLite",
                "url": DATABASE_URL,
                "contact_count": contact_count
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "Contact Book API - Database Fundamentals",
                "database": {
                    "status": "disconnected",
                    "error": str(e)
                },
                "timestamp": datetime.utcnow()
            }
        )

# Database info endpoint
@app.get("/database/info", tags=["Database"])
async def database_info():
    """Get information about the database."""
    return {
        "database_type": "SQLite",
        "database_url": DATABASE_URL,
        "tables": ["contacts"],
        "models": ["Contact"],
        "features": [
            "CRUD operations",
            "Text search",
            "Filtering",
            "Pagination",
            "Aggregation"
        ]
    }

# Main execution
if __name__ == "__main__":
    import uvicorn
    print("🚀 Database Fundamentals - Contact Book API")
    print("=" * 55)
    print("This tutorial demonstrates database integration with SQLModel.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Contacts: http://localhost:8000/contacts")
    print("   • Stats: http://localhost:8000/contacts/stats")
    print("")
    print("💾 Database:")
    print(f"   • Type: SQLite")
    print(f"   • File: {DATABASE_URL}")
    print(f"   • Location: {os.path.abspath(DATABASE_DIR)}/contacts.db")
    print("")
    print("📚 What you'll learn:")
    print("   • SQLModel for database operations")
    print("   • Database sessions and dependency injection")
    print("   • SQL queries with filtering and search")
    print("   • Database migrations and table creation")
    print("   • Transaction handling and error management")
    print("")
    print("🎯 Try these operations:")
    print("   1. GET /contacts - See all contacts")
    print("   2. POST /contacts - Create a new contact")
    print("   3. GET /contacts/search/john - Search for contacts")
    print("   4. PUT /contacts/1 - Update contact completely")
    print("   5. DELETE /contacts/1 - Delete a contact")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 55)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)