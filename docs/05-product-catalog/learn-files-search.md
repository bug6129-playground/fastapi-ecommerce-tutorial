# Tutorial A5: File Uploads & Search Patterns

**Handle file uploads and implement search functionality** 🔍

In this tutorial, you'll learn how to handle file uploads in FastAPI and implement effective search and filtering patterns. These are essential features for real-world applications like product catalogs, document management systems, and media platforms.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ How to accept and validate file uploads
- ✅ Saving files to disk and managing file paths
- ✅ Serving static files through your API
- ✅ Image validation and processing basics
- ✅ Implementing text search across multiple fields
- ✅ Advanced filtering and query patterns
- ✅ Security considerations for file uploads

## 📤 File Upload Fundamentals

### **1. Basic File Upload**

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from pathlib import Path

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # Create directory if it doesn't exist

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a single file.

    - **file**: The file to upload
    """
    # Save the file
    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(content)
    }
```

### **2. File Upload with Validation**

```python
from fastapi import status

# Allowed file types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image with validation"""

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}"
        )

    # Read and check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    # Generate unique filename to prevent overwrites
    import uuid
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    with file_path.open("wb") as buffer:
        buffer.write(content)

    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "size": len(content),
        "url": f"/files/{unique_filename}"
    }
```

### **3. Multiple File Uploads**

```python
from typing import List

@app.post("/upload/multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """Upload multiple files at once"""

    uploaded_files = []

    for file in files:
        # Validate each file
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue  # Skip invalid files

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename

        # Save file
        content = await file.read()
        with file_path.open("wb") as buffer:
            buffer.write(content)

        uploaded_files.append({
            "filename": unique_filename,
            "original_filename": file.filename,
            "size": len(content)
        })

    return {
        "uploaded_count": len(uploaded_files),
        "files": uploaded_files
    }
```

### **4. Serving Uploaded Files**

```python
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Mount static files directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Or serve files through endpoint
@app.get("/files/{filename}")
async def get_file(filename: str):
    """Serve uploaded file"""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    return FileResponse(file_path)
```

## 🔍 Search Implementation Patterns

### **1. Basic Text Search**

```python
from sqlmodel import Session, select, or_

class Photo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: Optional[str]
    filename: str
    tags: str  # Comma-separated tags

@app.get("/photos/search")
async def search_photos(
    q: str,
    session: Session = Depends(get_session)
):
    """
    Search photos by title, description, or tags.

    The query searches across multiple fields.
    """
    photos = session.exec(
        select(Photo).where(
            or_(
                Photo.title.contains(q),
                Photo.description.contains(q),
                Photo.tags.contains(q)
            )
        )
    ).all()

    return photos
```

### **2. Advanced Filtering**

```python
from datetime import datetime, timedelta

@app.get("/photos")
async def get_photos(
    # Search query
    q: Optional[str] = None,

    # Filters
    tag: Optional[str] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    uploaded_after: Optional[datetime] = None,

    # Sorting
    sort_by: str = "created_at",
    order: str = "desc",

    # Pagination
    skip: int = 0,
    limit: int = 20,

    session: Session = Depends(get_session)
):
    """
    Get photos with comprehensive filtering and search.
    """
    # Start with base query
    query = select(Photo)

    # Apply search
    if q:
        query = query.where(
            or_(
                Photo.title.contains(q),
                Photo.description.contains(q),
                Photo.tags.contains(q)
            )
        )

    # Apply filters
    if tag:
        query = query.where(Photo.tags.contains(tag))

    if min_size:
        query = query.where(Photo.file_size >= min_size)

    if max_size:
        query = query.where(Photo.file_size <= max_size)

    if uploaded_after:
        query = query.where(Photo.created_at >= uploaded_after)

    # Apply sorting
    if order == "desc":
        query = query.order_by(getattr(Photo, sort_by).desc())
    else:
        query = query.order_by(getattr(Photo, sort_by))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    photos = session.exec(query).all()

    return photos
```

### **3. Case-Insensitive Search**

```python
from sqlmodel import func

@app.get("/photos/search")
async def search_photos_case_insensitive(
    q: str,
    session: Session = Depends(get_session)
):
    """
    Case-insensitive search.

    Works across different databases.
    """
    search_term = f"%{q.lower()}%"

    photos = session.exec(
        select(Photo).where(
            or_(
                func.lower(Photo.title).like(search_term),
                func.lower(Photo.description).like(search_term),
                func.lower(Photo.tags).like(search_term)
            )
        )
    ).all()

    return photos
```

### **4. Full-Text Search (PostgreSQL)**

```python
# For PostgreSQL with full-text search capabilities

from sqlalchemy import text

@app.get("/photos/search/fulltext")
async def fulltext_search(
    q: str,
    session: Session = Depends(get_session)
):
    """
    Full-text search using PostgreSQL's tsvector.

    More powerful than simple LIKE queries.
    """
    # Create a search vector from multiple columns
    query = text("""
        SELECT * FROM photo
        WHERE to_tsvector('english', title || ' ' || description || ' ' || tags)
        @@ plainto_tsquery('english', :search_term)
        ORDER BY ts_rank(
            to_tsvector('english', title || ' ' || description || ' ' || tags),
            plainto_tsquery('english', :search_term)
        ) DESC
    """)

    result = session.execute(query, {"search_term": q})
    return result.fetchall()
```

## 📝 Complete Example: Photo Gallery API

```python
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from sqlmodel import SQLModel, Field, Session, create_engine, select, or_
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import uuid
import shutil

# ==================== Models ====================

class PhotoBase(SQLModel):
    title: str = Field(max_length=100)
    description: Optional[str] = None
    tags: str = ""  # Comma-separated tags

class Photo(PhotoBase, table=True):
    id: Optional[int] = Field(primary_key=True)
    filename: str = Field(unique=True)
    file_size: int
    content_type: str
    created_at: datetime = Field(default_factory=datetime.now)

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int
    filename: str
    url: str
    file_size: int
    created_at: datetime

# ==================== Setup ====================

app = FastAPI(title="Photo Gallery API")

UPLOAD_DIR = Path("uploads/photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = "sqlite:///./photos.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Serve uploaded files
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==================== Endpoints ====================

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB

@app.post("/photos", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    title: str = "",
    description: Optional[str] = None,
    tags: str = "",
    session: Session = Depends(get_session)
):
    """Upload a photo with metadata"""

    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {ALLOWED_TYPES}"
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 5MB)"
        )

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    with file_path.open("wb") as buffer:
        buffer.write(content)

    # Create database entry
    photo = Photo(
        title=title or file.filename,
        description=description,
        tags=tags,
        filename=unique_filename,
        file_size=len(content),
        content_type=file.content_type
    )

    session.add(photo)
    session.commit()
    session.refresh(photo)

    # Return response with URL
    return PhotoResponse(
        **photo.dict(),
        url=f"/uploads/photos/{unique_filename}"
    )

@app.get("/photos", response_model=List[PhotoResponse])
async def get_photos(
    q: Optional[str] = None,
    tag: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """
    Get photos with optional search and filtering.

    - **q**: Search in title, description, and tags
    - **tag**: Filter by specific tag
    - **skip**: Skip N photos (pagination)
    - **limit**: Max photos to return
    """
    query = select(Photo)

    # Search
    if q:
        search_term = f"%{q.lower()}%"
        query = query.where(
            or_(
                Photo.title.contains(q),
                Photo.description.contains(q),
                Photo.tags.contains(q)
            )
        )

    # Filter by tag
    if tag:
        query = query.where(Photo.tags.contains(tag))

    # Pagination
    query = query.offset(skip).limit(limit).order_by(Photo.created_at.desc())

    photos = session.exec(query).all()

    # Add URLs to responses
    return [
        PhotoResponse(**photo.dict(), url=f"/uploads/photos/{photo.filename}")
        for photo in photos
    ]

@app.get("/photos/{photo_id}", response_model=PhotoResponse)
async def get_photo(
    photo_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific photo"""
    photo = session.get(Photo, photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    return PhotoResponse(
        **photo.dict(),
        url=f"/uploads/photos/{photo.filename}"
    )

@app.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    session: Session = Depends(get_session)
):
    """Delete a photo"""
    photo = session.get(Photo, photo_id)

    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Delete file from disk
    file_path = UPLOAD_DIR / photo.filename
    if file_path.exists():
        file_path.unlink()

    # Delete from database
    session.delete(photo)
    session.commit()

    return None

@app.get("/tags")
async def get_all_tags(session: Session = Depends(get_session)):
    """Get all unique tags"""
    photos = session.exec(select(Photo)).all()

    # Extract all tags
    all_tags = set()
    for photo in photos:
        if photo.tags:
            tags = [tag.strip() for tag in photo.tags.split(",")]
            all_tags.update(tags)

    return sorted(list(all_tags))
```

## 🔒 Security Considerations

### **1. Validate File Types**

```python
import magic  # python-magic library

def validate_file_type(file_content: bytes) -> bool:
    """Validate actual file type (not just extension)"""
    mime = magic.from_buffer(file_content, mime=True)
    return mime in ALLOWED_TYPES
```

### **2. Sanitize Filenames**

```python
import re

def sanitize_filename(filename: str) -> str:
    """Remove dangerous characters from filename"""
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")
    # Remove special characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    return filename
```

### **3. Limit Upload Rate**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/upload")
@limiter.limit("10/minute")  # Max 10 uploads per minute
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Upload logic
    pass
```

## 🎯 Practice Challenges

### **Challenge 1: Document Management**
Build a document upload system with:
- Support for PDF, DOCX, TXT files
- Full-text search in document content
- Organize by categories/folders
- Download statistics

### **Challenge 2: Profile Pictures**
Create a user avatar system:
- Upload profile pictures
- Automatic image resizing
- Default avatar if none uploaded
- Update/delete avatar

### **Challenge 3: Advanced Gallery**
Enhance the photo gallery:
- Tag autocomplete
- Related photos (same tags)
- Photo albums/collections
- Like/favorite system

## ❓ Troubleshooting

**Q: Files are corrupted after upload!**
A: Make sure to open files in binary mode (`"wb"`) and use `await file.read()` for async operations.

**Q: How do I handle large files?**
A: Use streaming to avoid loading entire file in memory. Consider cloud storage (S3, etc.) for large files.

**Q: Can I process images (resize, crop)?**
A: Yes! Use Pillow library for image processing before saving.

**Q: How do I prevent malicious file uploads?**
A: Validate file types by content (not just extension), limit file sizes, use virus scanning, and store files outside webroot.

## ➡️ What's Next?

Great work! Now let's learn about data relationships!

**🎯 Continue Path A:**
1. **[Example 05: File Handling](../../examples/05-file-handling/)** - Practice file uploads
2. **[Chapter 6: Data Relationships](../06-order-processing/learn-relations.md)** - Connect related data
3. **[Example 06: Relationships](../../examples/06-relationships/)** - Posts and comments

**🏗️ Or Switch to Path B:**
Jump to **[Tutorial B5: Product Catalog](apply-product-system.md)** to build the e-commerce product system!

---

## 📚 Summary

**What you learned:**
- ✅ File upload handling with validation
- ✅ Saving files securely to disk
- ✅ Serving static files
- ✅ Text search across multiple fields
- ✅ Advanced filtering and query building
- ✅ Pagination and sorting
- ✅ Security best practices

**Key takeaways:**
1. Always validate file types and sizes
2. Generate unique filenames to prevent conflicts
3. Use case-insensitive search for better UX
4. Build flexible query patterns for filtering
5. Consider security implications of file uploads

Excellent! You now know how to handle files and implement search. 🎉

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A5*
