# Tutorial A6: Data Relationships

**Connect related data with SQLModel relationships** 🔗

In this tutorial, you'll learn how to model and work with related data in your database. Understanding relationships is crucial for building real-world applications where data is interconnected, like blog posts with comments, users with orders, or products with reviews.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ Types of database relationships (one-to-many, many-to-many)
- ✅ Defining relationships in SQLModel
- ✅ Foreign keys and referential integrity
- ✅ Querying related data efficiently
- ✅ Cascade operations (delete, update)
- ✅ API patterns for working with relationships

## 🧠 Understanding Relationships

### **Relationship Types**

#### **1. One-to-Many (Most Common)**
One parent can have many children.

**Examples:**
- One blog post → Many comments
- One user → Many orders
- One category → Many products
- One author → Many books

```
Post (1) ──────< Comments (Many)
```

#### **2. Many-to-Many**
Many items on one side relate to many on the other.

**Examples:**
- Many students → Many courses
- Many products → Many orders
- Many books → Many authors
- Many posts → Many tags

```
Students (Many) >──────< Courses (Many)
              (junction table)
```

#### **3. One-to-One (Less Common)**
One item relates to exactly one other item.

**Examples:**
- One user → One profile
- One employee → One desk
- One country → One capital

## 📝 One-to-Many Relationships

### **Basic One-to-Many Setup**

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Author(SQLModel, table=True):
    """Author can write many posts"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

    # Relationship: One author has many posts
    posts: List["Post"] = Relationship(back_populates="author")


class Post(SQLModel, table=True):
    """Post belongs to one author"""
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str

    # Foreign key: Links to author table
    author_id: int = Field(foreign_key="author.id")

    # Relationship: Post belongs to one author
    author: Optional[Author] = Relationship(back_populates="posts")
```

**Key Concepts:**
- **Foreign Key** (`author_id`): Stores the ID of the related author
- **Relationship**: Allows accessing related objects
- **back_populates**: Links the relationship in both directions

### **Using Relationships in Code**

```python
from sqlmodel import Session, select

# Create author with posts
def create_author_with_posts(session: Session):
    # Create author
    author = Author(name="John Doe", email="john@example.com")
    session.add(author)
    session.commit()
    session.refresh(author)

    # Create posts for this author
    post1 = Post(
        title="First Post",
        content="Hello World",
        author_id=author.id
    )
    post2 = Post(
        title="Second Post",
        content="Another post",
        author_id=author.id
    )

    session.add(post1)
    session.add(post2)
    session.commit()

    return author

# Query with relationships
def get_author_with_posts(session: Session, author_id: int):
    # Get author
    author = session.get(Author, author_id)

    # Access related posts automatically
    print(f"Author: {author.name}")
    for post in author.posts:
        print(f"  - {post.title}")

    return author

# Query posts with author
def get_posts_with_authors(session: Session):
    posts = session.exec(select(Post)).all()

    for post in posts:
        print(f"Post: {post.title}")
        print(f"Author: {post.author.name}")  # Access related author

    return posts
```

## 📝 Complete Example: Blog System

```python
from fastapi import FastAPI, HTTPException, Depends, status
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine, select
from typing import Optional, List
from datetime import datetime

# ==================== Models ====================

class AuthorBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    bio: Optional[str] = None

class Author(AuthorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship
    posts: List["Post"] = Relationship(back_populates="author")

class AuthorCreate(AuthorBase):
    email: str

class AuthorRead(AuthorBase):
    id: int
    email: str
    created_at: datetime


class PostBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    content: str
    published: bool = False

class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Foreign key
    author_id: int = Field(foreign_key="author.id")

    # Relationships
    author: Optional[Author] = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: int
    author_id: int
    created_at: datetime

class PostReadWithAuthor(PostRead):
    author: AuthorRead  # Include author info


class CommentBase(SQLModel):
    content: str = Field(min_length=1)
    author_name: str

class Comment(CommentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)

    # Foreign key
    post_id: int = Field(foreign_key="post.id")

    # Relationship
    post: Optional[Post] = Relationship(back_populates="comments")

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int
    post_id: int
    created_at: datetime

class PostReadWithComments(PostRead):
    comments: List[CommentRead] = []  # Include comments

# ==================== Setup ====================

app = FastAPI(title="Blog API")

DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ==================== Author Endpoints ====================

@app.post("/authors", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(
    author: AuthorCreate,
    session: Session = Depends(get_session)
):
    """Create a new author"""
    db_author = Author.from_orm(author)
    session.add(db_author)
    session.commit()
    session.refresh(db_author)
    return db_author

@app.get("/authors", response_model=List[AuthorRead])
def get_authors(session: Session = Depends(get_session)):
    """Get all authors"""
    authors = session.exec(select(Author)).all()
    return authors

@app.get("/authors/{author_id}", response_model=AuthorRead)
def get_author(
    author_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific author"""
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@app.get("/authors/{author_id}/posts", response_model=List[PostRead])
def get_author_posts(
    author_id: int,
    session: Session = Depends(get_session)
):
    """Get all posts by an author"""
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Access related posts
    return author.posts

# ==================== Post Endpoints ====================

@app.post("/authors/{author_id}/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(
    author_id: int,
    post: PostCreate,
    session: Session = Depends(get_session)
):
    """Create a new post for an author"""
    # Verify author exists
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # Create post
    db_post = Post(**post.dict(), author_id=author_id)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

@app.get("/posts", response_model=List[PostReadWithAuthor])
def get_posts(
    published: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """Get all posts with author information"""
    query = select(Post)

    if published is not None:
        query = query.where(Post.published == published)

    posts = session.exec(query).all()

    # Relationship is automatically loaded
    return posts

@app.get("/posts/{post_id}", response_model=PostReadWithComments)
def get_post(
    post_id: int,
    session: Session = Depends(get_session)
):
    """Get a post with all comments"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post

# ==================== Comment Endpoints ====================

@app.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment: CommentCreate,
    session: Session = Depends(get_session)
):
    """Add a comment to a post"""
    # Verify post exists
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Create comment
    db_comment = Comment(**comment.dict(), post_id=post_id)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment

@app.get("/posts/{post_id}/comments", response_model=List[CommentRead])
def get_post_comments(
    post_id: int,
    session: Session = Depends(get_session)
):
    """Get all comments for a post"""
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post.comments
```

## 🔍 Advanced Relationship Patterns

### **1. Eager Loading (Prevent N+1 Queries)**

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Load posts with authors in one query
statement = select(Post).options(selectinload(Post.author))
posts = session.exec(statement).all()

# Now accessing post.author doesn't trigger additional queries
for post in posts:
    print(f"{post.title} by {post.author.name}")
```

### **2. Cascade Deletes**

```python
class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # When author is deleted, delete all their posts
    posts: List["Post"] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )
```

### **3. Counting Related Items**

```python
from sqlmodel import func

# Get authors with post count
statement = select(
    Author,
    func.count(Post.id).label("post_count")
).outerjoin(Post).group_by(Author.id)

results = session.exec(statement).all()

for author, count in results:
    print(f"{author.name}: {count} posts")
```

### **4. Filtering by Related Data**

```python
# Get all posts by authors named "John"
posts = session.exec(
    select(Post).join(Author).where(Author.name == "John")
).all()

# Get authors who have published posts
authors_with_posts = session.exec(
    select(Author).join(Post).where(Post.published == True).distinct()
).all()
```

## 🎯 Many-to-Many Relationships

```python
from sqlmodel import SQLModel, Field, Relationship

# Junction table (link table)
class StudentCourse(SQLModel, table=True):
    student_id: int = Field(foreign_key="student.id", primary_key=True)
    course_id: int = Field(foreign_key="course.id", primary_key=True)
    enrolled_at: datetime = Field(default_factory=datetime.now)
    grade: Optional[str] = None


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Many-to-many relationship
    courses: List["Course"] = Relationship(
        back_populates="students",
        link_model=StudentCourse
    )


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Many-to-many relationship
    students: List[Student] = Relationship(
        back_populates="courses",
        link_model=StudentCourse
    )


# Using the relationship
def enroll_student(session: Session, student_id: int, course_id: int):
    student = session.get(Student, student_id)
    course = session.get(Course, course_id)

    # Add course to student's courses
    student.courses.append(course)
    session.commit()


# Query
def get_student_courses(session: Session, student_id: int):
    student = session.get(Student, student_id)
    return student.courses  # List of all enrolled courses
```

## 🎯 Practice Challenges

### **Challenge 1: E-Commerce Orders**
Model the relationship between:
- Customers (1) → Orders (Many)
- Orders (1) → OrderItems (Many)
- Products (1) → OrderItems (Many)

### **Challenge 2: Social Network**
Create a blog with:
- Users (1) → Posts (Many)
- Posts (1) → Likes (Many)
- Posts (Many) → Tags (Many) via junction table

### **Challenge 3: Library System**
Build a library API with:
- Authors (Many) → Books (Many)
- Books (1) → Copies (Many)
- Members (1) → Loans (Many)
- Books (1) → Loans (Many)

## ❓ Troubleshooting

**Q: I get circular import errors!**
A: Use forward references with quotes: `List["Post"]` instead of `List[Post]`

**Q: Accessing relationships triggers many queries!**
A: Use eager loading with `selectinload()` to load related data in one query.

**Q: How do I delete with cascades?**
A: Add `sa_relationship_kwargs={"cascade": "all, delete"}` to your Relationship.

**Q: Should I use one-to-one or one-to-many?**
A: Use one-to-one only when there's truly a 1:1 relationship. one-to-many is more flexible.

## ➡️ What's Next?

Excellent! Now let's add security with authentication!

**🎯 Continue Path A:**
1. **[Example 06: Relationships](../../examples/06-relationships/)** - Practice relationships
2. **[Chapter 7: Authentication](../07-auth-security/learn-auth.md)** - Secure your API
3. **[Example 07: Auth Basics](../../examples/07-auth-basics/)** - JWT authentication

**🏗️ Or Switch to Path B:**
Jump to **[Tutorial B6: Order Processing](apply-order-system.md)** to build shopping cart and orders!

---

## 📚 Summary

**What you learned:**
- ✅ Database relationship types (one-to-many, many-to-many)
- ✅ Defining relationships with SQLModel
- ✅ Foreign keys and referential integrity
- ✅ Querying related data
- ✅ Cascade operations
- ✅ API endpoints for nested resources

**Key takeaways:**
1. Use foreign keys to link tables
2. Relationship() provides convenient access to related data
3. back_populates connects relationships bidirectionally
4. Use eager loading to avoid N+1 query problems
5. Many-to-many requires a junction table

Great work! You now understand data relationships. 🎉

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A6*
