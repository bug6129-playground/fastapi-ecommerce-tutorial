"""
Database Relationships Fundamentals - Blog System API
=====================================================

This example demonstrates database relationships using SQLModel with FastAPI.
Learn how to create and manage one-to-many and many-to-many relationships
through a blog system with authors, posts, comments, and tags.

Key Concepts Demonstrated:
- One-to-many relationships (Author -> Posts, Post -> Comments)
- Many-to-many relationships (Posts <-> Tags)
- Foreign keys and relationship fields
- Joining and querying related data
- Cascade operations and data integrity
- Nested API responses with related data
- Relationship validation and constraints

Author: bug6129
"""

from typing import List, Optional
from datetime import datetime
from enum import Enum
from sqlmodel import (
    SQLModel, Field, Relationship, create_engine, 
    Session, select, and_, or_, desc
)
from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="Relationships Fundamentals - Blog System",
    description="Learn database relationships through a blog management API",
    version="1.0.0"
)

# =============================================================================
# 1. DATABASE MODELS - Relationships and Foreign Keys
# =============================================================================

class PostStatus(str, Enum):
    """Post status enumeration."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

# Many-to-many relationship table for posts and tags
class PostTagLink(SQLModel, table=True):
    """Link table for many-to-many relationship between posts and tags."""
    __tablename__ = "post_tags"
    
    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

# =============================================================================
# Author Model (One side of one-to-many with Posts)
# =============================================================================

class AuthorBase(SQLModel):
    """Base author model with shared fields."""
    name: str = Field(..., description="Author's full name", max_length=100)
    email: str = Field(..., description="Author's email address", max_length=255)
    bio: Optional[str] = Field(None, description="Author biography", max_length=1000)
    website: Optional[str] = Field(None, description="Author's website URL", max_length=200)
    is_active: bool = Field(default=True, description="Whether author is active")

class Author(AuthorBase, table=True):
    """Author database table model."""
    
    __tablename__ = "authors"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship: One author has many posts
    posts: List["Post"] = Relationship(back_populates="author")

class AuthorCreate(AuthorBase):
    """Model for creating new authors."""
    pass

class AuthorUpdate(SQLModel):
    """Model for updating existing authors."""
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=1000)
    website: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None

# =============================================================================
# Tag Model (Many side of many-to-many with Posts)
# =============================================================================

class TagBase(SQLModel):
    """Base tag model with shared fields."""
    name: str = Field(..., description="Tag name", max_length=50)
    description: Optional[str] = Field(None, description="Tag description", max_length=200)
    color: Optional[str] = Field(None, description="Display color for tag", max_length=7)

class Tag(TagBase, table=True):
    """Tag database table model."""
    
    __tablename__ = "tags"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship: Many tags have many posts
    posts: List["Post"] = Relationship(back_populates="tags", link_model=PostTagLink)

class TagCreate(TagBase):
    """Model for creating new tags."""
    pass

class TagUpdate(SQLModel):
    """Model for updating existing tags."""
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    color: Optional[str] = Field(None, max_length=7)

# =============================================================================
# Post Model (Many side of one-to-many with Author, One side with Comments)
# =============================================================================

class PostBase(SQLModel):
    """Base post model with shared fields."""
    title: str = Field(..., description="Post title", max_length=200)
    content: str = Field(..., description="Post content")
    excerpt: Optional[str] = Field(None, description="Post excerpt", max_length=500)
    status: PostStatus = Field(default=PostStatus.DRAFT, description="Post status")
    is_featured: bool = Field(default=False, description="Whether post is featured")
    view_count: int = Field(default=0, description="Number of views")
    
    # Foreign key to author
    author_id: int = Field(..., foreign_key="authors.id", description="Author ID")

class Post(PostBase, table=True):
    """Post database table model."""
    
    __tablename__ = "posts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    
    # Relationships
    author: Author = Relationship(back_populates="posts")  # Many posts -> One author
    comments: List["Comment"] = Relationship(back_populates="post")  # One post -> Many comments
    tags: List[Tag] = Relationship(back_populates="posts", link_model=PostTagLink)  # Many-to-many

class PostCreate(PostBase):
    """Model for creating new posts."""
    tag_ids: Optional[List[int]] = Field(default=[], description="List of tag IDs to associate")

class PostUpdate(SQLModel):
    """Model for updating existing posts."""
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    excerpt: Optional[str] = Field(None, max_length=500)
    status: Optional[PostStatus] = None
    is_featured: Optional[bool] = None
    author_id: Optional[int] = None
    tag_ids: Optional[List[int]] = Field(default=None, description="List of tag IDs to associate")

# =============================================================================
# Comment Model (Many side of one-to-many with Posts)
# =============================================================================

class CommentBase(SQLModel):
    """Base comment model with shared fields."""
    author_name: str = Field(..., description="Commenter's name", max_length=100)
    author_email: Optional[str] = Field(None, description="Commenter's email", max_length=255)
    content: str = Field(..., description="Comment content", max_length=2000)
    is_approved: bool = Field(default=False, description="Whether comment is approved")
    
    # Foreign key to post
    post_id: int = Field(..., foreign_key="posts.id", description="Post ID")

class Comment(CommentBase, table=True):
    """Comment database table model."""
    
    __tablename__ = "comments"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship: Many comments -> One post
    post: Post = Relationship(back_populates="comments")

class CommentCreate(CommentBase):
    """Model for creating new comments."""
    pass

class CommentUpdate(SQLModel):
    """Model for updating existing comments."""
    author_name: Optional[str] = Field(None, max_length=100)
    author_email: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, max_length=2000)
    is_approved: Optional[bool] = None

# =============================================================================
# RESPONSE MODELS - Including Related Data
# =============================================================================

class TagResponse(SQLModel):
    """Response model for tag data."""
    id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    created_at: datetime

class AuthorResponse(SQLModel):
    """Response model for author data."""
    id: int
    name: str
    email: str
    bio: Optional[str]
    website: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    post_count: Optional[int] = None  # Computed field

class CommentResponse(SQLModel):
    """Response model for comment data."""
    id: int
    author_name: str
    author_email: Optional[str]
    content: str
    is_approved: bool
    created_at: datetime
    post_id: int

class PostResponse(SQLModel):
    """Response model for post data with related information."""
    id: int
    title: str
    content: str
    excerpt: Optional[str]
    status: PostStatus
    is_featured: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    
    # Related data
    author: AuthorResponse
    tags: List[TagResponse]
    comment_count: Optional[int] = None  # Computed field

class PostSummaryResponse(SQLModel):
    """Lightweight response model for post listings."""
    id: int
    title: str
    excerpt: Optional[str]
    status: PostStatus
    is_featured: bool
    view_count: int
    created_at: datetime
    published_at: Optional[datetime]
    
    author_name: str
    tag_names: List[str]
    comment_count: int

# =============================================================================
# DATABASE SETUP
# =============================================================================

# Database setup
DATABASE_URL = "sqlite:///blog.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Database session dependency."""
    with Session(engine) as session:
        yield session

# Initialize database
create_db_and_tables()

# =============================================================================
# SAMPLE DATA CREATION
# =============================================================================

def create_sample_data(session: Session):
    """Create sample blog data for demonstration."""
    
    # Check if data already exists
    existing_authors = session.exec(select(Author)).first()
    if existing_authors:
        return
    
    # Create sample authors
    authors = [
        Author(
            name="Alice Johnson",
            email="alice@blogexample.com",
            bio="Tech blogger and software developer with 10 years of experience.",
            website="https://alice-tech-blog.com"
        ),
        Author(
            name="Bob Smith",
            email="bob@blogexample.com",
            bio="Travel enthusiast and photographer sharing stories from around the world.",
            website="https://bob-travels.com"
        ),
        Author(
            name="Carol Williams",
            email="carol@blogexample.com",
            bio="Food critic and cooking instructor passionate about culinary arts.",
            is_active=True
        )
    ]
    
    for author in authors:
        session.add(author)
    session.commit()
    
    # Refresh to get IDs
    for author in authors:
        session.refresh(author)
    
    # Create sample tags
    tags = [
        Tag(name="Technology", description="Tech-related posts", color="#007bff"),
        Tag(name="Travel", description="Travel and adventure posts", color="#28a745"),
        Tag(name="Food", description="Cooking and food reviews", color="#ffc107"),
        Tag(name="Tutorial", description="How-to guides and tutorials", color="#17a2b8"),
        Tag(name="Opinion", description="Personal opinions and thoughts", color="#6c757d"),
        Tag(name="Photography", description="Photo-related content", color="#e83e8c")
    ]
    
    for tag in tags:
        session.add(tag)
    session.commit()
    
    # Refresh to get IDs
    for tag in tags:
        session.refresh(tag)
    
    # Create sample posts with relationships
    posts_data = [
        {
            "title": "Getting Started with FastAPI",
            "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.6+. In this comprehensive guide, we'll explore how to build production-ready APIs...",
            "excerpt": "Learn how to build modern APIs with FastAPI framework",
            "status": PostStatus.PUBLISHED,
            "is_featured": True,
            "author": authors[0],  # Alice
            "tags": [tags[0], tags[3]],  # Technology, Tutorial
            "published_at": datetime(2024, 1, 15, 10, 0, 0)
        },
        {
            "title": "Exploring Tokyo: A Food Lover's Guide",
            "content": "Tokyo offers an incredible culinary experience with everything from street food to Michelin-starred restaurants. Here's my complete guide to eating in Tokyo...",
            "excerpt": "Discover the best food spots in Tokyo from a local's perspective",
            "status": PostStatus.PUBLISHED,
            "is_featured": True,
            "author": authors[1],  # Bob
            "tags": [tags[1], tags[2]],  # Travel, Food
            "published_at": datetime(2024, 1, 20, 14, 30, 0)
        },
        {
            "title": "The Art of Sourdough Bread Making",
            "content": "Making sourdough bread is both an art and a science. In this detailed tutorial, I'll walk you through every step of creating the perfect sourdough...",
            "excerpt": "Master the ancient art of sourdough bread making",
            "status": PostStatus.PUBLISHED,
            "author": authors[2],  # Carol
            "tags": [tags[2], tags[3]],  # Food, Tutorial
            "published_at": datetime(2024, 1, 25, 9, 15, 0)
        },
        {
            "title": "Photography Tips for Travelers",
            "content": "Capturing great travel photos requires more than just a good camera. Here are my top tips for taking memorable travel photographs...",
            "excerpt": "Essential photography tips for your next adventure",
            "status": PostStatus.PUBLISHED,
            "author": authors[1],  # Bob
            "tags": [tags[1], tags[5], tags[3]],  # Travel, Photography, Tutorial
            "published_at": datetime(2024, 2, 1, 16, 45, 0)
        },
        {
            "title": "Database Relationships in Modern Web Apps",
            "content": "Understanding database relationships is crucial for building scalable web applications. This post covers one-to-many, many-to-many, and other relationship types...",
            "excerpt": "Deep dive into database relationship patterns",
            "status": PostStatus.DRAFT,
            "is_featured": False,
            "author": authors[0],  # Alice
            "tags": [tags[0], tags[3]],  # Technology, Tutorial
        }
    ]
    
    for post_data in posts_data:
        post = Post(
            title=post_data["title"],
            content=post_data["content"],
            excerpt=post_data["excerpt"],
            status=post_data["status"],
            is_featured=post_data["is_featured"],
            author_id=post_data["author"].id,
            published_at=post_data.get("published_at")
        )
        session.add(post)
        session.commit()
        session.refresh(post)
        
        # Add tags to post
        for tag in post_data["tags"]:
            link = PostTagLink(post_id=post.id, tag_id=tag.id)
            session.add(link)
        
        session.commit()
    
    # Create sample comments
    posts = session.exec(select(Post)).all()
    comments_data = [
        {
            "post": posts[0],  # FastAPI post
            "author_name": "Developer123",
            "author_email": "dev@example.com",
            "content": "Great tutorial! This really helped me understand FastAPI better.",
            "is_approved": True
        },
        {
            "post": posts[0],  # FastAPI post
            "author_name": "PythonFan",
            "content": "Thanks for sharing. Any plans for a follow-up on advanced features?",
            "is_approved": True
        },
        {
            "post": posts[1],  # Tokyo food post
            "author_name": "TokyoResident",
            "author_email": "local@tokyo.jp",
            "content": "As someone living in Tokyo, I can confirm these recommendations are spot on!",
            "is_approved": True
        },
        {
            "post": posts[2],  # Sourdough post
            "author_name": "BreadLover",
            "content": "I followed your recipe and it turned out amazing! Thank you!",
            "is_approved": True
        },
        {
            "post": posts[1],  # Tokyo food post
            "author_name": "Foodie",
            "content": "This is spam content that should not be approved.",
            "is_approved": False
        }
    ]
    
    for comment_data in comments_data:
        comment = Comment(
            post_id=comment_data["post"].id,
            author_name=comment_data["author_name"],
            author_email=comment_data.get("author_email"),
            content=comment_data["content"],
            is_approved=comment_data["is_approved"]
        )
        session.add(comment)
    
    session.commit()
    print("Sample blog data created successfully!")

# Create sample data on startup
with Session(engine) as session:
    create_sample_data(session)

# =============================================================================
# API ENDPOINTS - Root and Info
# =============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API information and relationship examples."""
    return {
        "message": "Blog System API - Database Relationships Fundamentals",
        "description": "Learn database relationships through blog management",
        "relationships": {
            "one_to_many": {
                "authors_to_posts": "One author can have many posts",
                "posts_to_comments": "One post can have many comments"
            },
            "many_to_many": {
                "posts_to_tags": "Posts can have multiple tags, tags can belong to multiple posts"
            }
        },
        "endpoints": {
            "authors": "/authors/ - Manage authors",
            "posts": "/posts/ - Manage posts with relationships",
            "comments": "/comments/ - Manage comments",
            "tags": "/tags/ - Manage tags"
        },
        "documentation": "/docs"
    }

# =============================================================================
# AUTHOR ENDPOINTS - One Side of One-to-Many
# =============================================================================

@app.get("/authors", response_model=List[AuthorResponse], tags=["Authors"])
async def get_authors(
    session: Session = Depends(get_session),
    include_inactive: bool = Query(False, description="Include inactive authors"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """Get all authors with post counts."""
    query = select(Author)
    
    if not include_inactive:
        query = query.where(Author.is_active == True)
    
    query = query.offset(skip).limit(limit)
    authors = session.exec(query).all()
    
    # Add post counts
    author_responses = []
    for author in authors:
        post_count = len(session.exec(
            select(Post).where(Post.author_id == author.id)
        ).all())
        
        author_response = AuthorResponse(
            id=author.id,
            name=author.name,
            email=author.email,
            bio=author.bio,
            website=author.website,
            is_active=author.is_active,
            created_at=author.created_at,
            updated_at=author.updated_at,
            post_count=post_count
        )
        author_responses.append(author_response)
    
    return author_responses

@app.post("/authors", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED, tags=["Authors"])
async def create_author(author_data: AuthorCreate, session: Session = Depends(get_session)):
    """Create a new author."""
    author = Author(**author_data.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    session.add(author)
    session.commit()
    session.refresh(author)
    
    return AuthorResponse(
        id=author.id,
        name=author.name,
        email=author.email,
        bio=author.bio,
        website=author.website,
        is_active=author.is_active,
        created_at=author.created_at,
        updated_at=author.updated_at,
        post_count=0
    )

@app.get("/authors/{author_id}", response_model=AuthorResponse, tags=["Authors"])
async def get_author(author_id: int, session: Session = Depends(get_session)):
    """Get a specific author with their post count."""
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Get post count
    post_count = len(session.exec(
        select(Post).where(Post.author_id == author.id)
    ).all())
    
    return AuthorResponse(
        id=author.id,
        name=author.name,
        email=author.email,
        bio=author.bio,
        website=author.website,
        is_active=author.is_active,
        created_at=author.created_at,
        updated_at=author.updated_at,
        post_count=post_count
    )

@app.get("/authors/{author_id}/posts", response_model=List[PostSummaryResponse], tags=["Authors"])
async def get_author_posts(
    author_id: int,
    session: Session = Depends(get_session),
    status_filter: Optional[PostStatus] = Query(None, description="Filter by post status")
):
    """Get all posts by a specific author (demonstrates one-to-many relationship)."""
    # Verify author exists
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    # Query posts by author
    query = select(Post).where(Post.author_id == author_id)
    
    if status_filter:
        query = query.where(Post.status == status_filter)
    
    query = query.order_by(desc(Post.created_at))
    posts = session.exec(query).all()
    
    # Build response with related data
    post_responses = []
    for post in posts:
        # Get tags for this post
        post_tags = session.exec(
            select(Tag).join(PostTagLink).where(PostTagLink.post_id == post.id)
        ).all()
        
        # Get comment count
        comment_count = len(session.exec(
            select(Comment).where(Comment.post_id == post.id)
        ).all())
        
        post_response = PostSummaryResponse(
            id=post.id,
            title=post.title,
            excerpt=post.excerpt,
            status=post.status,
            is_featured=post.is_featured,
            view_count=post.view_count,
            created_at=post.created_at,
            published_at=post.published_at,
            author_name=author.name,
            tag_names=[tag.name for tag in post_tags],
            comment_count=comment_count
        )
        post_responses.append(post_response)
    
    return post_responses

# =============================================================================
# POST ENDPOINTS - Central Hub with Multiple Relationships
# =============================================================================

@app.get("/posts", response_model=List[PostSummaryResponse], tags=["Posts"])
async def get_posts(
    session: Session = Depends(get_session),
    status_filter: Optional[PostStatus] = Query(None, description="Filter by status"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    featured_only: bool = Query(False, description="Show only featured posts"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Get posts with filtering and related data.
    
    Demonstrates querying with relationships and joins.
    """
    query = select(Post)
    
    # Apply filters
    if status_filter:
        query = query.where(Post.status == status_filter)
    
    if author_id:
        query = query.where(Post.author_id == author_id)
    
    if featured_only:
        query = query.where(Post.is_featured == True)
    
    if tag_id:
        # Join with PostTagLink to filter by tag
        query = query.join(PostTagLink).where(PostTagLink.tag_id == tag_id)
    
    query = query.order_by(desc(Post.created_at)).offset(skip).limit(limit)
    posts = session.exec(query).all()
    
    # Build responses with related data
    post_responses = []
    for post in posts:
        # Get author
        author = session.get(Author, post.author_id)
        
        # Get tags
        post_tags = session.exec(
            select(Tag).join(PostTagLink).where(PostTagLink.post_id == post.id)
        ).all()
        
        # Get comment count
        comment_count = len(session.exec(
            select(Comment).where(Comment.post_id == post.id)
        ).all())
        
        post_response = PostSummaryResponse(
            id=post.id,
            title=post.title,
            excerpt=post.excerpt,
            status=post.status,
            is_featured=post.is_featured,
            view_count=post.view_count,
            created_at=post.created_at,
            published_at=post.published_at,
            author_name=author.name if author else "Unknown",
            tag_names=[tag.name for tag in post_tags],
            comment_count=comment_count
        )
        post_responses.append(post_response)
    
    return post_responses

@app.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED, tags=["Posts"])
async def create_post(post_data: PostCreate, session: Session = Depends(get_session)):
    """
    Create a new post with author and tag relationships.
    
    Demonstrates creating records with foreign keys and many-to-many relationships.
    """
    # Verify author exists
    author = session.get(Author, post_data.author_id)
    if not author:
        raise HTTPException(status_code=400, detail="Author not found")
    
    # Verify tags exist
    if post_data.tag_ids:
        for tag_id in post_data.tag_ids:
            if not session.get(Tag, tag_id):
                raise HTTPException(status_code=400, detail=f"Tag with ID {tag_id} not found")
    
    # Create post
    post_dict = post_data.dict()
    tag_ids = post_dict.pop("tag_ids", [])
    
    post = Post(
        **post_dict,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        published_at=datetime.utcnow() if post_data.status == PostStatus.PUBLISHED else None
    )
    
    session.add(post)
    session.commit()
    session.refresh(post)
    
    # Add tag relationships
    for tag_id in tag_ids:
        link = PostTagLink(post_id=post.id, tag_id=tag_id)
        session.add(link)
    session.commit()
    
    # Build response with related data
    author_response = AuthorResponse(
        id=author.id,
        name=author.name,
        email=author.email,
        bio=author.bio,
        website=author.website,
        is_active=author.is_active,
        created_at=author.created_at,
        updated_at=author.updated_at
    )
    
    # Get associated tags
    post_tags = session.exec(
        select(Tag).join(PostTagLink).where(PostTagLink.post_id == post.id)
    ).all()
    
    tag_responses = [
        TagResponse(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            color=tag.color,
            created_at=tag.created_at
        )
        for tag in post_tags
    ]
    
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        status=post.status,
        is_featured=post.is_featured,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at,
        author=author_response,
        tags=tag_responses,
        comment_count=0
    )

@app.get("/posts/{post_id}", response_model=PostResponse, tags=["Posts"])
async def get_post(post_id: int, session: Session = Depends(get_session)):
    """
    Get a specific post with all related data.
    
    Demonstrates fetching a record with all its relationships.
    """
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment view count
    post.view_count += 1
    session.add(post)
    session.commit()
    
    # Get author
    author = session.get(Author, post.author_id)
    author_response = AuthorResponse(
        id=author.id,
        name=author.name,
        email=author.email,
        bio=author.bio,
        website=author.website,
        is_active=author.is_active,
        created_at=author.created_at,
        updated_at=author.updated_at
    )
    
    # Get tags
    post_tags = session.exec(
        select(Tag).join(PostTagLink).where(PostTagLink.post_id == post.id)
    ).all()
    
    tag_responses = [
        TagResponse(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            color=tag.color,
            created_at=tag.created_at
        )
        for tag in post_tags
    ]
    
    # Get comment count
    comment_count = len(session.exec(
        select(Comment).where(Comment.post_id == post.id)
    ).all())
    
    return PostResponse(
        id=post.id,
        title=post.title,
        content=post.content,
        excerpt=post.excerpt,
        status=post.status,
        is_featured=post.is_featured,
        view_count=post.view_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at,
        author=author_response,
        tags=tag_responses,
        comment_count=comment_count
    )

@app.get("/posts/{post_id}/comments", response_model=List[CommentResponse], tags=["Posts"])
async def get_post_comments(
    post_id: int,
    session: Session = Depends(get_session),
    approved_only: bool = Query(True, description="Show only approved comments")
):
    """
    Get all comments for a specific post.
    
    Demonstrates one-to-many relationship querying.
    """
    # Verify post exists
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    query = select(Comment).where(Comment.post_id == post_id)
    
    if approved_only:
        query = query.where(Comment.is_approved == True)
    
    query = query.order_by(Comment.created_at)
    comments = session.exec(query).all()
    
    return [
        CommentResponse(
            id=comment.id,
            author_name=comment.author_name,
            author_email=comment.author_email,
            content=comment.content,
            is_approved=comment.is_approved,
            created_at=comment.created_at,
            post_id=comment.post_id
        )
        for comment in comments
    ]

# =============================================================================
# TAG ENDPOINTS - Many-to-Many Relationships
# =============================================================================

@app.get("/tags", response_model=List[TagResponse], tags=["Tags"])
async def get_tags(session: Session = Depends(get_session)):
    """Get all tags."""
    tags = session.exec(select(Tag).order_by(Tag.name)).all()
    
    return [
        TagResponse(
            id=tag.id,
            name=tag.name,
            description=tag.description,
            color=tag.color,
            created_at=tag.created_at
        )
        for tag in tags
    ]

@app.get("/tags/{tag_id}/posts", response_model=List[PostSummaryResponse], tags=["Tags"])
async def get_tag_posts(tag_id: int, session: Session = Depends(get_session)):
    """
    Get all posts associated with a specific tag.
    
    Demonstrates many-to-many relationship querying.
    """
    tag = session.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Query posts through the link table
    posts = session.exec(
        select(Post)
        .join(PostTagLink)
        .where(PostTagLink.tag_id == tag_id)
        .order_by(desc(Post.created_at))
    ).all()
    
    post_responses = []
    for post in posts:
        # Get author
        author = session.get(Author, post.author_id)
        
        # Get all tags for this post
        post_tags = session.exec(
            select(Tag).join(PostTagLink).where(PostTagLink.post_id == post.id)
        ).all()
        
        # Get comment count
        comment_count = len(session.exec(
            select(Comment).where(Comment.post_id == post.id)
        ).all())
        
        post_response = PostSummaryResponse(
            id=post.id,
            title=post.title,
            excerpt=post.excerpt,
            status=post.status,
            is_featured=post.is_featured,
            view_count=post.view_count,
            created_at=post.created_at,
            published_at=post.published_at,
            author_name=author.name if author else "Unknown",
            tag_names=[t.name for t in post_tags],
            comment_count=comment_count
        )
        post_responses.append(post_response)
    
    return post_responses

# =============================================================================
# COMMENT ENDPOINTS - Many Side of One-to-Many
# =============================================================================

@app.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED, tags=["Comments"])
async def create_comment(comment_data: CommentCreate, session: Session = Depends(get_session)):
    """
    Create a new comment.
    
    Demonstrates creating records with foreign key relationships.
    """
    # Verify post exists
    post = session.get(Post, comment_data.post_id)
    if not post:
        raise HTTPException(status_code=400, detail="Post not found")
    
    comment = Comment(**comment_data.dict(), created_at=datetime.utcnow())
    session.add(comment)
    session.commit()
    session.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        author_name=comment.author_name,
        author_email=comment.author_email,
        content=comment.content,
        is_approved=comment.is_approved,
        created_at=comment.created_at,
        post_id=comment.post_id
    )

# =============================================================================
# STATISTICS AND REPORTING
# =============================================================================

@app.get("/stats", tags=["Statistics"])
async def get_blog_stats(session: Session = Depends(get_session)):
    """Get comprehensive blog statistics showing relationships."""
    
    # Basic counts
    author_count = len(session.exec(select(Author)).all())
    post_count = len(session.exec(select(Post)).all())
    comment_count = len(session.exec(select(Comment)).all())
    tag_count = len(session.exec(select(Tag)).all())
    
    # Published vs draft posts
    published_posts = len(session.exec(
        select(Post).where(Post.status == PostStatus.PUBLISHED)
    ).all())
    draft_posts = len(session.exec(
        select(Post).where(Post.status == PostStatus.DRAFT)
    ).all())
    
    # Most active authors (by post count)
    authors = session.exec(select(Author)).all()
    author_post_counts = []
    for author in authors:
        posts = session.exec(select(Post).where(Post.author_id == author.id)).all()
        if posts:
            author_post_counts.append({
                "author_name": author.name,
                "post_count": len(posts)
            })
    
    author_post_counts.sort(key=lambda x: x["post_count"], reverse=True)
    
    # Most used tags
    tags = session.exec(select(Tag)).all()
    tag_usage = []
    for tag in tags:
        post_tags = session.exec(
            select(PostTagLink).where(PostTagLink.tag_id == tag.id)
        ).all()
        if post_tags:
            tag_usage.append({
                "tag_name": tag.name,
                "post_count": len(post_tags)
            })
    
    tag_usage.sort(key=lambda x: x["post_count"], reverse=True)
    
    # Posts with most comments
    posts = session.exec(select(Post)).all()
    post_comment_counts = []
    for post in posts:
        comments = session.exec(select(Comment).where(Comment.post_id == post.id)).all()
        if comments:
            post_comment_counts.append({
                "post_title": post.title,
                "comment_count": len(comments)
            })
    
    post_comment_counts.sort(key=lambda x: x["comment_count"], reverse=True)
    
    return {
        "overview": {
            "total_authors": author_count,
            "total_posts": post_count,
            "total_comments": comment_count,
            "total_tags": tag_count,
            "published_posts": published_posts,
            "draft_posts": draft_posts
        },
        "top_authors": author_post_counts[:5],
        "popular_tags": tag_usage[:5],
        "most_commented_posts": post_comment_counts[:5],
        "relationships": {
            "avg_posts_per_author": round(post_count / author_count, 2) if author_count > 0 else 0,
            "avg_comments_per_post": round(comment_count / post_count, 2) if post_count > 0 else 0,
            "avg_tags_per_post": round(
                len(session.exec(select(PostTagLink)).all()) / post_count, 2
            ) if post_count > 0 else 0
        }
    }

# Health check
@app.get("/health", tags=["System"])
async def health_check(session: Session = Depends(get_session)):
    """Health check with relationship counts."""
    try:
        counts = {
            "authors": len(session.exec(select(Author)).all()),
            "posts": len(session.exec(select(Post)).all()),
            "comments": len(session.exec(select(Comment)).all()),
            "tags": len(session.exec(select(Tag)).all()),
            "post_tag_links": len(session.exec(select(PostTagLink)).all())
        }
        
        return {
            "status": "healthy",
            "service": "Blog System API - Database Relationships Fundamentals",
            "database": DATABASE_URL,
            "record_counts": counts,
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
    print("🚀 Database Relationships Fundamentals - Blog System API")
    print("=" * 65)
    print("This tutorial demonstrates database relationships through blog management.")
    print("")
    print("🌐 Open your browser to:")
    print("   • API: http://localhost:8000")
    print("   • Docs: http://localhost:8000/docs")
    print("   • Stats: http://localhost:8000/stats")
    print("")
    print("🔗 Relationships demonstrated:")
    print("   • One-to-Many: Authors → Posts, Posts → Comments")
    print("   • Many-to-Many: Posts ↔ Tags")
    print("   • Foreign Keys: post.author_id, comment.post_id")
    print("   • Link Tables: post_tags for many-to-many")
    print("")
    print("💾 Database:")
    print(f"   • File: {DATABASE_URL}")
    print("   • Tables: authors, posts, comments, tags, post_tags")
    print("")
    print("📚 What you'll learn:")
    print("   • One-to-many relationship modeling")
    print("   • Many-to-many relationships with link tables")
    print("   • Foreign key constraints and validation")
    print("   • Joining and querying related data")
    print("   • Cascade operations and data integrity")
    print("")
    print("🎯 Try these operations:")
    print("   1. GET /posts - See posts with author and tag info")
    print("   2. GET /authors/1/posts - Get all posts by an author")
    print("   3. GET /tags/1/posts - Get all posts with a specific tag")
    print("   4. POST /posts - Create post with author and tags")
    print("   5. GET /stats - See relationship statistics")
    print("")
    print("Press CTRL+C to quit")
    print("=" * 65)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)