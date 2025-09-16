# Database Relationships Fundamentals

**Learn database relationships through a Blog System API** 📝

This example demonstrates essential database relationship concepts using SQLModel with FastAPI. Learn how to create and manage one-to-many and many-to-many relationships through a blog system with authors, posts, comments, and tags.

## 🎯 What You'll Learn

- **One-to-Many Relationships**: Authors to Posts, Posts to Comments
- **Many-to-Many Relationships**: Posts to Tags with link tables
- **Foreign Keys**: Establishing and maintaining data integrity
- **Relationship Fields**: SQLModel relationship definitions
- **Joining Data**: Querying across related tables
- **Cascade Operations**: Managing related data lifecycle
- **Nested Responses**: Including related data in API responses
- **Relationship Validation**: Ensuring referential integrity

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- Relationship concepts: 20 minutes
- One-to-many implementation: 30 minutes
- Many-to-many relationships: 30 minutes
- Advanced querying: 10 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]" sqlmodel
```

### Run the Example

```bash
# Navigate to this directory
cd examples/06-relationships

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Blog Stats**: http://localhost:8000/stats
- **Author Posts**: http://localhost:8000/authors/1/posts
- **Tag Posts**: http://localhost:8000/tags/1/posts

## 📚 Key Concepts Explained

### 1. Relationship Types

| Relationship | Description | Example | Implementation |
|--------------|-------------|---------|----------------|
| **One-to-Many** | One record relates to many | Author → Posts | Foreign key |
| **Many-to-Many** | Many records relate to many | Posts ↔ Tags | Link table |
| **One-to-One** | One record relates to one | User ↔ Profile | Foreign key (unique) |

### 2. One-to-Many Relationship

```python
# Parent model (One side)
class Author(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    
    # Relationship field
    posts: List["Post"] = Relationship(back_populates="author")

# Child model (Many side)
class Post(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    author_id: int = Field(foreign_key="authors.id")  # Foreign key
    
    # Relationship field
    author: Author = Relationship(back_populates="posts")
```

### 3. Many-to-Many Relationship

```python
# Link table for many-to-many
class PostTagLink(SQLModel, table=True):
    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)

# First model
class Post(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)

# Second model
class Tag(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    
    posts: List[Post] = Relationship(back_populates="tags", link_model=PostTagLink)
```

### 4. Querying Relationships

```python
# Get posts with their authors
posts_with_authors = session.exec(
    select(Post).join(Author).where(Author.is_active == True)
).all()

# Get posts by specific tag
posts_with_tag = session.exec(
    select(Post)
    .join(PostTagLink)
    .where(PostTagLink.tag_id == tag_id)
).all()

# Count related records
author_post_count = len(session.exec(
    select(Post).where(Post.author_id == author_id)
).all())
```

## 🎮 Hands-On Exercises

### Exercise 1: Explore Existing Relationships

1. **View All Authors with Post Counts**:
   ```bash
   curl "http://localhost:8000/authors"
   ```

2. **Get Posts by Specific Author**:
   ```bash
   curl "http://localhost:8000/authors/1/posts"
   ```

3. **Get Posts with Specific Tag**:
   ```bash
   curl "http://localhost:8000/tags/1/posts"
   ```

4. **View Blog Statistics**:
   ```bash
   curl "http://localhost:8000/stats"
   ```

### Exercise 2: Create with Relationships

1. **Create New Author**:
   ```bash
   curl -X POST "http://localhost:8000/authors" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Jane Developer",
          "email": "jane@example.com",
          "bio": "Full-stack developer and tech writer",
          "website": "https://janedev.com"
        }'
   ```

2. **Create Post with Author and Tags**:
   ```bash
   curl -X POST "http://localhost:8000/posts" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "Advanced FastAPI Techniques",
          "content": "In this post, we explore advanced FastAPI patterns...",
          "excerpt": "Learn advanced FastAPI development patterns",
          "status": "published",
          "author_id": 1,
          "tag_ids": [1, 4]
        }'
   ```

3. **Add Comment to Post**:
   ```bash
   curl -X POST "http://localhost:8000/comments" \
        -H "Content-Type: application/json" \
        -d '{
          "post_id": 1,
          "author_name": "Reader123",
          "author_email": "reader@example.com",
          "content": "Great post! Very informative.",
          "is_approved": true
        }'
   ```

### Exercise 3: Query Relationships

1. **Get Post with Full Details**:
   ```bash
   curl "http://localhost:8000/posts/1"
   # Notice: author info, tags, and comment count included
   ```

2. **Get Comments for a Post**:
   ```bash
   curl "http://localhost:8000/posts/1/comments"
   ```

3. **Filter Posts by Status**:
   ```bash
   curl "http://localhost:8000/posts?status=published"
   ```

4. **Filter Posts by Tag**:
   ```bash
   curl "http://localhost:8000/posts?tag_id=1"
   ```

### Exercise 4: Relationship Statistics

1. **Blog Overview**:
   ```bash
   curl "http://localhost:8000/stats"
   # Shows relationship statistics and popular content
   ```

## 🔍 Code Structure Walkthrough

### 1. Database Models with Relationships

```python
# One-to-many: Author → Posts
class Author(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    
    # Relationship: back reference to posts
    posts: List["Post"] = Relationship(back_populates="author")

class Post(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    author_id: int = Field(foreign_key="authors.id")  # Foreign key
    
    # Relationships
    author: Author = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)
```

### 2. Many-to-Many Link Table

```python
class PostTagLink(SQLModel, table=True):
    """Junction table for posts and tags."""
    __tablename__ = "post_tags"
    
    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)
```

### 3. Querying with Joins

```python
# Query with relationship filtering
@app.get("/authors/{author_id}/posts")
async def get_author_posts(author_id: int, session: Session = Depends(get_session)):
    # Verify author exists (relationship validation)
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(404, "Author not found")
    
    # Query posts by foreign key
    posts = session.exec(
        select(Post).where(Post.author_id == author_id)
    ).all()
    
    return posts
```

### 4. Creating with Relationships

```python
@app.post("/posts")
async def create_post(post_data: PostCreate, session: Session = Depends(get_session)):
    # Validate foreign key relationships
    author = session.get(Author, post_data.author_id)
    if not author:
        raise HTTPException(400, "Author not found")
    
    # Create main record
    post = Post(**post_data.dict(exclude={"tag_ids"}))
    session.add(post)
    session.commit()
    session.refresh(post)
    
    # Create many-to-many relationships
    for tag_id in post_data.tag_ids:
        link = PostTagLink(post_id=post.id, tag_id=tag_id)
        session.add(link)
    session.commit()
    
    return post
```

## 🎯 Relationship Patterns Demonstrated

### 1. **One-to-Many Patterns**

```python
# Parent access to children
author = session.get(Author, 1)
author_posts = author.posts  # SQLModel handles the query

# Child access to parent
post = session.get(Post, 1)
post_author = post.author  # Automatic join

# Manual querying
posts_by_author = session.exec(
    select(Post).where(Post.author_id == author_id)
).all()
```

### 2. **Many-to-Many Patterns**

```python
# Get all tags for a post
post_tags = session.exec(
    select(Tag)
    .join(PostTagLink)
    .where(PostTagLink.post_id == post_id)
).all()

# Get all posts for a tag
tag_posts = session.exec(
    select(Post)
    .join(PostTagLink) 
    .where(PostTagLink.tag_id == tag_id)
).all()

# Create many-to-many relationship
link = PostTagLink(post_id=1, tag_id=2)
session.add(link)
session.commit()
```

### 3. **Nested Response Building**

```python
# Build response with related data
def build_post_response(post: Post, session: Session) -> PostResponse:
    # Get author
    author = session.get(Author, post.author_id)
    
    # Get tags through junction table
    tags = session.exec(
        select(Tag).join(PostTagLink).where(PostTagLink.post_id == post.id)
    ).all()
    
    # Get comment count
    comment_count = len(session.exec(
        select(Comment).where(Comment.post_id == post.id)
    ).all())
    
    return PostResponse(
        **post.dict(),
        author=author,
        tags=tags,
        comment_count=comment_count
    )
```

## 📊 Database Schema Overview

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Authors   │──────▶│    Posts    │──────▶│  Comments   │
│             │ 1:M   │             │ 1:M   │             │
│ • id (PK)   │       │ • id (PK)   │       │ • id (PK)   │
│ • name      │       │ • title     │       │ • content   │
│ • email     │       │ • content   │       │ • post_id   │
│ • bio       │       │ • author_id │       │             │
└─────────────┘       │   (FK)      │       └─────────────┘
                      └─────────────┘
                             │
                             │ M:M
                             ▼
                      ┌─────────────┐       ┌─────────────┐
                      │ PostTagLink │──────▶│    Tags     │
                      │             │       │             │
                      │ • post_id   │       │ • id (PK)   │
                      │   (PK, FK)  │       │ • name      │
                      │ • tag_id    │       │ • color     │
                      │   (PK, FK)  │       │             │
                      └─────────────┘       └─────────────┘
```

## 🧪 Testing Your Understanding

### Challenge 1: Add Categories
Implement a new Category model:
- One-to-many relationship with Posts
- Posts can have one category
- Categories can have many posts
- Add category filtering to post endpoints

### Challenge 2: User System
Add a User model for authentication:
- Authors belong to Users (one-to-one)
- Comments belong to Users (one-to-many)
- Users can like Posts (many-to-many)

### Challenge 3: Hierarchical Comments
Implement nested comments:
- Comments can reply to other comments
- Self-referencing foreign key
- Recursive relationship handling

### Challenge 4: Advanced Querying
Implement complex queries:
- Posts by author with specific tags
- Most commented posts in date range
- Authors with most posts in category
- Tag usage statistics over time

## 🔗 What's Next?

After mastering database relationships, you're ready for:

1. **Authentication** (Example 07) - Protect your API and relate data to users
2. **Testing** (Example 08) - Test relationship scenarios and data integrity
3. **Advanced Topics** - Polymorphic relationships, soft deletes, audit trails
4. **Performance** - Query optimization, eager loading, caching

## 💡 Key Takeaways

- **Foreign keys maintain integrity** - Database enforces relationships
- **SQLModel handles complexity** - Relationship fields simplify queries
- **Link tables enable many-to-many** - Junction tables store relationships
- **Validation is crucial** - Always verify related records exist
- **Joins can be expensive** - Consider performance for complex queries
- **Cascade carefully** - Understand deletion behavior

## 🐛 Common Pitfalls

1. **Forgetting foreign key constraints**: Always define foreign keys properly
2. **N+1 query problems**: Loading related data in loops instead of joins
3. **Missing relationship validation**: Not checking if related records exist
4. **Circular imports**: Careful with forward references in relationships
5. **Cascade deletion issues**: Understanding what gets deleted automatically
6. **Link table management**: Properly handling many-to-many relationships

## 🔧 Relationship Best Practices

### Performance Optimization

```python
# Bad: N+1 queries
posts = session.exec(select(Post)).all()
for post in posts:
    author = session.get(Author, post.author_id)  # Extra query each time!

# Good: Join in single query  
posts_with_authors = session.exec(
    select(Post, Author)
    .join(Author)
    .where(Post.status == "published")
).all()
```

### Data Integrity

```python
# Always validate relationships before creating
@app.post("/posts")
async def create_post(post_data: PostCreate, session: Session = Depends(get_session)):
    # Validate author exists
    if not session.get(Author, post_data.author_id):
        raise HTTPException(400, "Author not found")
    
    # Validate all tags exist
    for tag_id in post_data.tag_ids:
        if not session.get(Tag, tag_id):
            raise HTTPException(400, f"Tag {tag_id} not found")
    
    # Now safe to create
    post = Post(**post_data.dict())
    session.add(post)
    session.commit()
```

### Relationship Loading

```python
# Eager loading (load related data immediately)
posts = session.exec(
    select(Post)
    .options(selectinload(Post.author), selectinload(Post.tags))
).all()

# Lazy loading (load related data when accessed)
post = session.get(Post, 1)
author = post.author  # Triggers additional query
```

---

**Ready to secure your API? Continue with [Example 07: Authentication Basics](../07-auth-basics/)!** 🔒