"""
File Handling Fundamentals - Photo Gallery API
==============================================

This example demonstrates file upload, storage, and serving with FastAPI.
Learn how to handle multipart file uploads, validate file types, manage storage,
and serve static files through a photo gallery application.

Key Concepts Demonstrated:
- File uploads with UploadFile
- File validation (size, type, extension)
- Static file serving
- File storage management
- Image metadata handling
- File download responses
- Error handling for file operations

Author: bug6129
"""

import os
import shutil
from typing import List, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path
from PIL import Image, ExifTags
import mimetypes

from pydantic import BaseModel, Field
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends, Query, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field as SQLField, create_engine, Session, select

# Create FastAPI app
app = FastAPI(
    title="File Handling Fundamentals - Photo Gallery",
    description="Learn file operations through a photo gallery API",
    version="1.0.0"
)

# =============================================================================
# 1. CONFIGURATION - File Handling Settings
# =============================================================================

# File storage configuration
UPLOAD_DIR = "uploads"
THUMBNAILS_DIR = "uploads/thumbnails"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", 
    "image/bmp", "image/webp"
}

# Create upload directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)

# Database setup for photo metadata
DATABASE_URL = "sqlite:///uploads/gallery.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# =============================================================================
# 2. DATA MODELS - Photo Metadata and Validation
# =============================================================================

class PhotoCategory(str, Enum):
    """Photo categories for organization."""
    NATURE = "nature"
    PORTRAITS = "portraits"
    LANDSCAPES = "landscapes"
    ARCHITECTURE = "architecture"
    STREET = "street"
    ABSTRACT = "abstract"
    OTHER = "other"

class PhotoMetadata(SQLModel, table=True):
    """Database model for photo metadata."""
    
    __tablename__ = "photos"
    
    id: Optional[int] = SQLField(default=None, primary_key=True)
    filename: str = SQLField(description="Original filename")
    stored_filename: str = SQLField(description="Filename as stored on disk")
    title: Optional[str] = SQLField(default=None, max_length=200)
    description: Optional[str] = SQLField(default=None, max_length=1000)
    category: PhotoCategory = SQLField(default=PhotoCategory.OTHER)
    
    # File information
    file_size: int = SQLField(description="File size in bytes")
    mime_type: str = SQLField(description="MIME type")
    width: Optional[int] = SQLField(default=None, description="Image width in pixels")
    height: Optional[int] = SQLField(default=None, description="Image height in pixels")
    
    # Metadata
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    uploaded_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # EXIF data (simplified)
    camera_make: Optional[str] = SQLField(default=None, max_length=100)
    camera_model: Optional[str] = SQLField(default=None, max_length=100)
    taken_at: Optional[datetime] = SQLField(default=None)

class PhotoCreate(BaseModel):
    """Model for creating photo metadata."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: PhotoCategory = Field(default=PhotoCategory.OTHER)

class PhotoUpdate(BaseModel):
    """Model for updating photo metadata."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[PhotoCategory] = None

class PhotoResponse(BaseModel):
    """Response model for photo data."""
    id: int
    filename: str
    title: Optional[str]
    description: Optional[str]
    category: PhotoCategory
    file_size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    created_at: datetime
    uploaded_at: datetime
    camera_make: Optional[str]
    camera_model: Optional[str]
    taken_at: Optional[datetime]
    
    # URLs
    url: str
    thumbnail_url: Optional[str]
    download_url: str

class UploadResponse(BaseModel):
    """Response model for file upload."""
    message: str
    photo: PhotoResponse
    upload_info: dict

# Create database tables
SQLModel.metadata.create_all(engine)

# =============================================================================
# 3. UTILITY FUNCTIONS - File Operations
# =============================================================================

def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session

def validate_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate uploaded file.
    
    Returns:
        (is_valid, error_message)
    """
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}"
    
    return True, ""

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent conflicts."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = Path(original_filename).stem
    extension = Path(original_filename).suffix
    return f"{timestamp}_{name}{extension}"

def extract_image_metadata(file_path: str) -> dict:
    """Extract metadata from image file."""
    try:
        with Image.open(file_path) as img:
            metadata = {
                "width": img.width,
                "height": img.height,
                "format": img.format
            }
            
            # Extract EXIF data if available
            if hasattr(img, '_getexif'):
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == "Make":
                            metadata["camera_make"] = str(value)
                        elif tag == "Model":
                            metadata["camera_model"] = str(value)
                        elif tag == "DateTime":
                            try:
                                metadata["taken_at"] = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                            except:
                                pass
            
            return metadata
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {"width": None, "height": None}

def create_thumbnail(source_path: str, thumbnail_path: str, size: tuple = (300, 300)):
    """Create a thumbnail from the original image."""
    try:
        with Image.open(source_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        return True
    except Exception as e:
        print(f"Error creating thumbnail: {e}")
        return False

# =============================================================================
# 4. API ENDPOINTS - File Operations
# =============================================================================

# Mount static files for serving uploaded images
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

@app.get("/", tags=["Info"])
async def root():
    """API information and file handling capabilities."""
    return {
        "message": "Photo Gallery API - File Handling Fundamentals",
        "description": "Learn file operations through photo management",
        "file_config": {
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
            "allowed_extensions": list(ALLOWED_EXTENSIONS),
            "allowed_mime_types": list(ALLOWED_MIME_TYPES),
            "upload_directory": UPLOAD_DIR
        },
        "endpoints": {
            "POST /upload": "Upload a photo",
            "GET /photos": "List all photos",
            "GET /photos/{id}": "Get photo details",
            "GET /photos/{id}/download": "Download original photo",
            "PUT /photos/{id}": "Update photo metadata",
            "DELETE /photos/{id}": "Delete a photo"
        },
        "static_files": "/static/{filename} - Access uploaded files",
        "documentation": "/docs"
    }

# =============================================================================
# FILE UPLOAD ENDPOINTS
# =============================================================================

@app.post("/upload", response_model=UploadResponse, tags=["Photos"])
async def upload_photo(
    file: UploadFile = File(..., description="Image file to upload"),
    title: Optional[str] = Form(None, description="Photo title"),
    description: Optional[str] = Form(None, description="Photo description"),
    category: PhotoCategory = Form(PhotoCategory.OTHER, description="Photo category"),
    session: Session = Depends(get_session)
):
    """
    Upload a photo with metadata.
    
    This endpoint demonstrates:
    - File upload with UploadFile
    - File validation (size, type, extension)
    - Metadata extraction from images
    - Database storage of file information
    - Thumbnail generation
    - Form data with file uploads
    """
    # Validate the uploaded file
    is_valid, error_message = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    try:
        # Generate unique filename
        stored_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, stored_filename)
        thumbnail_path = os.path.join(THUMBNAILS_DIR, f"thumb_{stored_filename}")
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract image metadata
        img_metadata = extract_image_metadata(file_path)
        
        # Create thumbnail
        thumbnail_created = create_thumbnail(file_path, thumbnail_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create database record
        photo_record = PhotoMetadata(
            filename=file.filename,
            stored_filename=stored_filename,
            title=title,
            description=description,
            category=category,
            file_size=file_size,
            mime_type=file.content_type,
            width=img_metadata.get("width"),
            height=img_metadata.get("height"),
            camera_make=img_metadata.get("camera_make"),
            camera_model=img_metadata.get("camera_model"),
            taken_at=img_metadata.get("taken_at")
        )
        
        session.add(photo_record)
        session.commit()
        session.refresh(photo_record)
        
        # Build response
        photo_response = PhotoResponse(
            id=photo_record.id,
            filename=photo_record.filename,
            title=photo_record.title,
            description=photo_record.description,
            category=photo_record.category,
            file_size=photo_record.file_size,
            mime_type=photo_record.mime_type,
            width=photo_record.width,
            height=photo_record.height,
            created_at=photo_record.created_at,
            uploaded_at=photo_record.uploaded_at,
            camera_make=photo_record.camera_make,
            camera_model=photo_record.camera_model,
            taken_at=photo_record.taken_at,
            url=f"/static/{stored_filename}",
            thumbnail_url=f"/static/thumbnails/thumb_{stored_filename}" if thumbnail_created else None,
            download_url=f"/photos/{photo_record.id}/download"
        )
        
        return UploadResponse(
            message="Photo uploaded successfully",
            photo=photo_response,
            upload_info={
                "original_filename": file.filename,
                "stored_filename": stored_filename,
                "file_size_bytes": file_size,
                "thumbnail_created": thumbnail_created,
                "upload_timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )

@app.post("/upload-multiple", tags=["Photos"])
async def upload_multiple_photos(
    files: List[UploadFile] = File(..., description="Multiple image files"),
    category: PhotoCategory = Form(PhotoCategory.OTHER),
    session: Session = Depends(get_session)
):
    """
    Upload multiple photos at once.
    
    Demonstrates bulk file upload handling.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per request")
    
    results = []
    failed_uploads = []
    
    for file in files:
        try:
            # Validate each file
            is_valid, error_message = validate_file(file)
            if not is_valid:
                failed_uploads.append({"filename": file.filename, "error": error_message})
                continue
            
            # Process upload (simplified version)
            stored_filename = generate_unique_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, stored_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            img_metadata = extract_image_metadata(file_path)
            file_size = os.path.getsize(file_path)
            
            photo_record = PhotoMetadata(
                filename=file.filename,
                stored_filename=stored_filename,
                category=category,
                file_size=file_size,
                mime_type=file.content_type,
                width=img_metadata.get("width"),
                height=img_metadata.get("height")
            )
            
            session.add(photo_record)
            session.commit()
            session.refresh(photo_record)
            
            results.append({
                "filename": file.filename,
                "id": photo_record.id,
                "url": f"/static/{stored_filename}",
                "status": "success"
            })
            
        except Exception as e:
            failed_uploads.append({"filename": file.filename, "error": str(e)})
    
    return {
        "message": f"Processed {len(files)} files",
        "successful_uploads": len(results),
        "failed_uploads": len(failed_uploads),
        "results": results,
        "failures": failed_uploads
    }

# =============================================================================
# PHOTO MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/photos", response_model=List[PhotoResponse], tags=["Photos"])
async def get_photos(
    session: Session = Depends(get_session),
    category: Optional[PhotoCategory] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    List all photos with optional filtering.
    
    Demonstrates file listing with metadata.
    """
    query = select(PhotoMetadata)
    
    if category:
        query = query.where(PhotoMetadata.category == category)
    
    query = query.offset(skip).limit(limit).order_by(PhotoMetadata.uploaded_at.desc())
    photos = session.exec(query).all()
    
    # Build response with URLs
    photo_responses = []
    for photo in photos:
        photo_responses.append(PhotoResponse(
            id=photo.id,
            filename=photo.filename,
            title=photo.title,
            description=photo.description,
            category=photo.category,
            file_size=photo.file_size,
            mime_type=photo.mime_type,
            width=photo.width,
            height=photo.height,
            created_at=photo.created_at,
            uploaded_at=photo.uploaded_at,
            camera_make=photo.camera_make,
            camera_model=photo.camera_model,
            taken_at=photo.taken_at,
            url=f"/static/{photo.stored_filename}",
            thumbnail_url=f"/static/thumbnails/thumb_{photo.stored_filename}",
            download_url=f"/photos/{photo.id}/download"
        ))
    
    return photo_responses

@app.get("/photos/{photo_id}", response_model=PhotoResponse, tags=["Photos"])
async def get_photo(photo_id: int, session: Session = Depends(get_session)):
    """Get detailed information about a specific photo."""
    photo = session.get(PhotoMetadata, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    return PhotoResponse(
        id=photo.id,
        filename=photo.filename,
        title=photo.title,
        description=photo.description,
        category=photo.category,
        file_size=photo.file_size,
        mime_type=photo.mime_type,
        width=photo.width,
        height=photo.height,
        created_at=photo.created_at,
        uploaded_at=photo.uploaded_at,
        camera_make=photo.camera_make,
        camera_model=photo.camera_model,
        taken_at=photo.taken_at,
        url=f"/static/{photo.stored_filename}",
        thumbnail_url=f"/static/thumbnails/thumb_{photo.stored_filename}",
        download_url=f"/photos/{photo.id}/download"
    )

@app.get("/photos/{photo_id}/download", tags=["Photos"])
async def download_photo(photo_id: int, session: Session = Depends(get_session)):
    """
    Download the original photo file.
    
    Demonstrates file download with proper headers.
    """
    photo = session.get(PhotoMetadata, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    file_path = os.path.join(UPLOAD_DIR, photo.stored_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Photo file not found")
    
    # Determine media type
    media_type = photo.mime_type or "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=photo.filename,  # Original filename for download
        headers={"Content-Disposition": f"attachment; filename={photo.filename}"}
    )

@app.put("/photos/{photo_id}", response_model=PhotoResponse, tags=["Photos"])
async def update_photo_metadata(
    photo_id: int,
    photo_data: PhotoUpdate,
    session: Session = Depends(get_session)
):
    """Update photo metadata (title, description, category)."""
    photo = session.get(PhotoMetadata, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Update fields
    update_data = photo_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(photo, field, value)
    
    session.add(photo)
    session.commit()
    session.refresh(photo)
    
    return PhotoResponse(
        id=photo.id,
        filename=photo.filename,
        title=photo.title,
        description=photo.description,
        category=photo.category,
        file_size=photo.file_size,
        mime_type=photo.mime_type,
        width=photo.width,
        height=photo.height,
        created_at=photo.created_at,
        uploaded_at=photo.uploaded_at,
        camera_make=photo.camera_make,
        camera_model=photo.camera_model,
        taken_at=photo.taken_at,
        url=f"/static/{photo.stored_filename}",
        thumbnail_url=f"/static/thumbnails/thumb_{photo.stored_filename}",
        download_url=f"/photos/{photo.id}/download"
    )

@app.delete("/photos/{photo_id}", tags=["Photos"])
async def delete_photo(photo_id: int, session: Session = Depends(get_session)):
    """
    Delete a photo and its associated files.
    
    Demonstrates proper cleanup of files and database records.
    """
    photo = session.get(PhotoMetadata, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Delete physical files
    file_path = os.path.join(UPLOAD_DIR, photo.stored_filename)
    thumbnail_path = os.path.join(THUMBNAILS_DIR, f"thumb_{photo.stored_filename}")
    
    files_deleted = []
    if os.path.exists(file_path):
        os.remove(file_path)
        files_deleted.append("original")
    
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)
        files_deleted.append("thumbnail")
    
    # Delete database record
    session.delete(photo)
    session.commit()
    
    return JSONResponse(
        status_code=200,
        content={
            "message": f"Photo '{photo.filename}' deleted successfully",
            "deleted_files": files_deleted,
            "photo_id": photo_id
        }
    )

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.get("/gallery/stats", tags=["Gallery"])
async def get_gallery_stats(session: Session = Depends(get_session)):
    """Get gallery statistics and storage information."""
    photos = session.exec(select(PhotoMetadata)).all()
    
    if not photos:
        return {"message": "No photos in gallery"}
    
    # Calculate statistics
    total_photos = len(photos)
    total_size = sum(photo.file_size for photo in photos)
    
    category_counts = {}
    for category in PhotoCategory:
        count = len([p for p in photos if p.category == category])
        if count > 0:
            category_counts[category.value] = count
    
    # File type distribution
    mime_type_counts = {}
    for photo in photos:
        mime_type_counts[photo.mime_type] = mime_type_counts.get(photo.mime_type, 0) + 1
    
    # Average dimensions
    photos_with_dimensions = [p for p in photos if p.width and p.height]
    avg_width = sum(p.width for p in photos_with_dimensions) // len(photos_with_dimensions) if photos_with_dimensions else 0
    avg_height = sum(p.height for p in photos_with_dimensions) // len(photos_with_dimensions) if photos_with_dimensions else 0
    
    return {
        "total_photos": total_photos,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "category_distribution": category_counts,
        "file_type_distribution": mime_type_counts,
        "average_dimensions": {
            "width": avg_width,
            "height": avg_height
        },
        "storage_info": {
            "upload_directory": UPLOAD_DIR,
            "max_file_size_mb": MAX_FILE_SIZE // (1024 * 1024),
            "allowed_extensions": list(ALLOWED_EXTENSIONS)
        }
    }

@app.get("/gallery/categories", tags=["Gallery"])
async def get_categories():
    """Get available photo categories."""
    return {
        "categories": [
            {"value": category.value, "label": category.value.title()}
            for category in PhotoCategory
        ]
    }

@app.post("/gallery/cleanup", tags=["Gallery"])
async def cleanup_orphaned_files(session: Session = Depends(get_session)):
    """
    Clean up files that exist on disk but not in database.
    
    Useful for maintenance and debugging.
    """
    # Get all files in upload directory
    upload_files = set()
    for file_path in Path(UPLOAD_DIR).glob("*"):
        if file_path.is_file():
            upload_files.add(file_path.name)
    
    # Get all stored filenames from database
    photos = session.exec(select(PhotoMetadata)).all()
    stored_filenames = {photo.stored_filename for photo in photos}
    
    # Find orphaned files
    orphaned_files = upload_files - stored_filenames
    
    # Remove orphaned files (optional - be careful!)
    removed_files = []
    for filename in orphaned_files:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            removed_files.append(filename)
    
    return {
        "message": "Cleanup completed",
        "orphaned_files_found": len(orphaned_files),
        "files_removed": len(removed_files),
        "removed_files": removed_files
    }

# Health check
@app.get("/health", tags=["System"])
async def health_check(session: Session = Depends(get_session)):
    """Health check with storage information."""
    try:
        # Check database
        photo_count = len(session.exec(select(PhotoMetadata)).all())
        
        # Check upload directory
        upload_dir_exists = os.path.exists(UPLOAD_DIR)
        
        return {
            "status": "healthy",
            "service": "Photo Gallery API - File Handling Fundamentals",
            "storage": {
                "upload_directory": UPLOAD_DIR,
                "directory_exists": upload_dir_exists,
                "photo_count": photo_count
            },
            "file_config": {
                "max_size_mb": MAX_FILE_SIZE // (1024 * 1024),
                "allowed_extensions": list(ALLOWED_EXTENSIONS)
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
    print("🚀 File Handling Fundamentals - Photo Gallery API")
    print("=" * 60)
    print("This tutorial demonstrates file operations through photo management.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Upload: http://localhost:8000/docs#/Photos/upload_photo_upload_post")
    print("   • Gallery Stats: http://localhost:8000/gallery/stats")
    print("")
    print("📁 File Storage:")
    print(f"   • Upload Directory: {os.path.abspath(UPLOAD_DIR)}")
    print(f"   • Database: {DATABASE_URL}")
    print(f"   • Max File Size: {MAX_FILE_SIZE // (1024*1024)}MB")
    print(f"   • Allowed Types: {', '.join(ALLOWED_EXTENSIONS)}")
    print("")
    print("📚 What you'll learn:")
    print("   • File upload with validation")
    print("   • Image metadata extraction")
    print("   • Thumbnail generation")
    print("   • Static file serving")
    print("   • File download responses")
    print("   • Bulk upload handling")
    print("")
    print("🎯 Try these operations:")
    print("   1. POST /upload - Upload a photo with metadata")
    print("   2. GET /photos - List all uploaded photos")
    print("   3. GET /photos/1/download - Download original file")
    print("   4. PUT /photos/1 - Update photo metadata")
    print("   5. DELETE /photos/1 - Delete photo and files")
    print("")
    print("📁 Access uploaded files at: http://localhost:8000/static/{filename}")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 60)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)