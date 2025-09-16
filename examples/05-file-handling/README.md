# File Handling Fundamentals

**Learn file upload, storage, and serving through a Photo Gallery API** 📸

This example demonstrates essential file handling concepts using FastAPI. Learn how to upload files, validate them, extract metadata, create thumbnails, and serve static content through a photo gallery application.

## 🎯 What You'll Learn

- **File Uploads**: Handle multipart file uploads with UploadFile
- **File Validation**: Validate file types, sizes, and MIME types
- **Static File Serving**: Serve uploaded files through FastAPI
- **Image Processing**: Extract metadata and create thumbnails
- **File Storage**: Organize and manage uploaded files
- **Download Responses**: Provide file downloads with proper headers
- **Bulk Operations**: Handle multiple file uploads
- **File Cleanup**: Manage orphaned files and storage

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- File upload basics: 20 minutes
- Image processing: 30 minutes
- Static file serving: 20 minutes
- Advanced features: 20 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]" sqlmodel pillow
```

### Run the Example

```bash
# Navigate to this directory
cd examples/05-file-handling

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Upload Form**: http://localhost:8000/docs#/Photos/upload_photo_upload_post
- **Gallery Stats**: http://localhost:8000/gallery/stats
- **Static Files**: http://localhost:8000/static/{filename}

## 📚 Key Concepts Explained

### 1. File Upload with FastAPI

```python
@app.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),          # File from multipart form
    title: str = Form(None),               # Additional form fields
    session: Session = Depends(get_session) # Database dependency
):
    # Process the uploaded file
```

### 2. File Validation

```python
def validate_file(file: UploadFile) -> tuple[bool, str]:
    # Check file size
    if file.size > MAX_FILE_SIZE:
        return False, "File too large"
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        return False, "Invalid file type"
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, "Invalid MIME type"
    
    return True, ""
```

### 3. Static File Serving

```python
from fastapi.staticfiles import StaticFiles

# Mount static files
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Files accessible at: http://localhost:8000/static/{filename}
```

### 4. File Download Responses

```python
from fastapi.responses import FileResponse

@app.get("/photos/{id}/download")
async def download_photo(photo_id: int):
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=original_filename,
        headers={"Content-Disposition": f"attachment; filename={original_filename}"}
    )
```

## 🎮 Hands-On Exercises

### Exercise 1: Basic File Upload

1. **Upload a Photo**:
   - Go to http://localhost:8000/docs
   - Find the `POST /upload` endpoint
   - Click "Try it out"
   - Choose an image file
   - Add title and description
   - Execute the request

2. **View Uploaded Photos**:
   ```bash
   curl "http://localhost:8000/photos"
   ```

3. **Access Static File**:
   ```bash
   # Use the URL from upload response
   curl "http://localhost:8000/static/{stored_filename}"
   ```

### Exercise 2: File Validation Testing

1. **Test File Size Limit**:
   - Try uploading a file larger than 10MB
   - Observe the validation error

2. **Test File Type Validation**:
   - Try uploading a .txt or .pdf file
   - See the MIME type validation error

3. **Test Valid Upload**:
   ```bash
   curl -X POST "http://localhost:8000/upload" \
        -F "file=@your_image.jpg" \
        -F "title=Test Photo" \
        -F "category=nature"
   ```

### Exercise 3: Image Metadata and Processing

1. **Upload Photo with EXIF Data**:
   - Use a photo taken with a digital camera
   - Check the response for camera make/model
   - Note the extracted dimensions

2. **View Thumbnail**:
   - Check if thumbnail was created
   - Access via `/static/thumbnails/thumb_{filename}`

3. **Download Original**:
   ```bash
   curl -O "http://localhost:8000/photos/1/download"
   ```

### Exercise 4: Bulk Operations

1. **Multiple Upload**:
   ```bash
   curl -X POST "http://localhost:8000/upload-multiple" \
        -F "files=@image1.jpg" \
        -F "files=@image2.png" \
        -F "category=landscapes"
   ```

2. **Gallery Statistics**:
   ```bash
   curl "http://localhost:8000/gallery/stats"
   ```

## 🔍 Code Structure Walkthrough

### 1. File Configuration

```python
# Configuration constants
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(THUMBNAILS_DIR, exist_ok=True)
```

### 2. Database Models

```python
class PhotoMetadata(SQLModel, table=True):
    """Store file metadata in database."""
    id: Optional[int] = Field(primary_key=True)
    filename: str  # Original filename
    stored_filename: str  # Unique filename on disk
    file_size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    # ... more fields
```

### 3. File Processing Pipeline

```python
# 1. Validate file
is_valid, error = validate_file(file)

# 2. Generate unique filename
stored_filename = generate_unique_filename(file.filename)

# 3. Save to disk
with open(file_path, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

# 4. Extract metadata
metadata = extract_image_metadata(file_path)

# 5. Create thumbnail
create_thumbnail(file_path, thumbnail_path)

# 6. Save to database
photo_record = PhotoMetadata(...)
session.add(photo_record)
session.commit()
```

## 🎯 File Features Demonstrated

### 1. **File Upload Types**

| Feature | Implementation | Use Case |
|---------|----------------|----------|
| Single Upload | `UploadFile = File(...)` | Profile pictures |
| Multiple Upload | `List[UploadFile] = File(...)` | Photo galleries |
| Form + File | `Form(...)` + `File(...)` | Metadata with files |

### 2. **File Validation**

```python
# Size validation
if file.size > MAX_FILE_SIZE:
    raise HTTPException(400, "File too large")

# Type validation
if file.content_type not in ALLOWED_MIME_TYPES:
    raise HTTPException(400, "Invalid file type")

# Extension validation
extension = Path(file.filename).suffix.lower()
if extension not in ALLOWED_EXTENSIONS:
    raise HTTPException(400, "Invalid file extension")
```

### 3. **Image Processing**

```python
from PIL import Image

# Extract dimensions
with Image.open(file_path) as img:
    width, height = img.size

# Create thumbnail
img.thumbnail((300, 300))
img.save(thumbnail_path, optimize=True, quality=85)

# Extract EXIF data
exif = img._getexif()
# Process camera make, model, date taken, etc.
```

### 4. **Static File Serving**

```python
# Mount static directory
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Files accessible at: /static/{filename}
# Automatic MIME type detection
# Browser caching headers
```

## 📁 File Structure

```
examples/05-file-handling/
├── main.py                 # Main application
├── README.md              # This file
├── uploads/               # Upload directory (auto-created)
│   ├── {timestamp}_{name}.jpg  # Original files
│   ├── thumbnails/        # Thumbnail directory
│   │   └── thumb_{filename}    # Generated thumbnails
│   └── gallery.db         # SQLite database
```

## 🧪 Testing Your Understanding

### Challenge 1: Add File Processing
Implement additional image processing:
- Resize images to maximum dimensions
- Convert all uploads to JPEG
- Add watermarking functionality
- Generate multiple thumbnail sizes

### Challenge 2: Enhanced Validation
Add more validation rules:
- Minimum image dimensions
- Maximum pixel count
- Image aspect ratio validation
- Content-based validation (not just extension)

### Challenge 3: Storage Backends
Implement different storage options:
- Amazon S3 integration
- Google Cloud Storage
- Local storage with directory organization
- Database BLOB storage

### Challenge 4: Advanced Features
Add sophisticated features:
- Image format conversion
- EXIF data editing
- Batch operations (resize, convert)
- Duplicate image detection

## 🔗 What's Next?

After mastering file handling, you're ready for:

1. **Relationships** (Example 06) - Connect files to users and other entities
2. **Authentication** (Example 07) - Protect file uploads and access
3. **Testing** (Example 08) - Test file upload scenarios
4. **Production** - Deploy with proper file storage

## 💡 Key Takeaways

- **Always validate files** - Size, type, and content validation is crucial
- **Use unique filenames** - Prevent conflicts and security issues
- **Store metadata separately** - Database for searchable info, filesystem for files
- **Handle cleanup properly** - Remove files when database records are deleted
- **Security matters** - Validate file types and scan for malicious content

## 🐛 Common Pitfalls

1. **No file validation**: Always validate size, type, and content
2. **Filename conflicts**: Use unique filenames or directory structure
3. **Missing cleanup**: Delete files when removing database records  
4. **Security risks**: Don't trust file extensions, validate content
5. **Large file handling**: Consider streaming for large files
6. **Storage limits**: Monitor disk usage and implement limits

## 🔧 File Handling Best Practices

### Security
```python
# Don't trust file extensions
def get_file_type(file_path):
    return magic.from_file(file_path, mime=True)

# Scan for malware
def scan_file(file_path):
    # Use antivirus API or service
    pass

# Limit upload rate
@app.post("/upload")
@limiter.limit("5/minute")
async def upload_photo(...):
    pass
```

### Performance
```python
# Stream large files
async def save_large_file(file: UploadFile):
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(8192):  # 8KB chunks
            await f.write(chunk)

# Background processing
from fastapi import BackgroundTasks

@app.post("/upload")
async def upload_photo(background_tasks: BackgroundTasks, ...):
    # Save file immediately
    # Process in background
    background_tasks.add_task(create_thumbnail, file_path)
```

### Storage Organization
```python
# Organize by date
def get_upload_path(filename):
    date_path = datetime.now().strftime("%Y/%m/%d")
    return f"uploads/{date_path}/{filename}"

# Organize by file type
def get_upload_path(filename, file_type):
    type_path = file_type.split('/')[0]  # image, video, document
    return f"uploads/{type_path}/{filename}"
```

---

**Ready to learn data relationships? Continue with [Example 06: Relationships](../06-relationships/)!** 🔗