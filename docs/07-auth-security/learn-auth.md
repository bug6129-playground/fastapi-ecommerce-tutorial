# Tutorial A7: Authentication & Security

**Secure your APIs with JWT authentication** 🔒

In this tutorial, you'll learn how to implement authentication and authorization in FastAPI using JWT (JSON Web Tokens). This is essential for protecting sensitive endpoints and managing user access to your API.

## 🎯 Learning Objectives

By the end of this tutorial, you'll understand:
- ✅ Authentication vs Authorization concepts
- ✅ Password hashing with bcrypt
- ✅ JWT (JSON Web Tokens) for stateless authentication
- ✅ Creating and validating JWT tokens
- ✅ Protecting endpoints with dependencies
- ✅ Role-based access control (RBAC)
- ✅ Security best practices

## 🧠 Authentication Fundamentals

### **Authentication vs Authorization**

| Concept | Question | Example |
|---------|----------|---------|
| **Authentication** | Who are you? | Login with username/password |
| **Authorization** | What can you do? | Admin can delete, users can't |

### **Authentication Flow**

```
1. User sends credentials (username + password)
   ↓
2. Server validates credentials
   ↓
3. Server creates JWT token
   ↓
4. User stores token (browser/app)
   ↓
5. User sends token with each request
   ↓
6. Server validates token and allows access
```

## 🔐 Password Security

### **1. Never Store Plain Text Passwords!**

❌ **WRONG:**
```python
# NEVER DO THIS!
class User:
    password: str = "mypassword123"  # Visible to anyone with database access
```

✅ **CORRECT:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password before storing
hashed_password = pwd_context.hash("mypassword123")
# Result: "$2b$12$EixZ..."

# Verify password during login
is_valid = pwd_context.verify("mypassword123", hashed_password)
# Result: True
```

### **2. Password Hashing Setup**

```python
from passlib.context import CryptContext

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain text password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)
```

## 🎟️ JWT (JSON Web Tokens)

### **What is a JWT?**

A JWT is a secure way to transmit information between parties. It consists of three parts:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
│                                        │                                                                                                │
│          HEADER                        │                                      PAYLOAD                                                   │                    SIGNATURE
```

**Parts:**
1. **Header**: Algorithm and token type
2. **Payload**: Claims (user data)
3. **Signature**: Verifies token wasn't tampered with

### **JWT Setup**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional

# Configuration
SECRET_KEY = "your-secret-key-keep-this-secret!"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (usually user ID and username)
        expires_delta: How long until token expires

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    # Create token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Returns:
        Token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

## 📝 Complete Authentication System

```python
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, Session, create_engine, select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

# ==================== Configuration ====================

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ==================== Models ====================

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ==================== Setup ====================

app = FastAPI(title="Secure API")

DATABASE_URL = "sqlite:///./auth.db"
engine = create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ==================== Security Functions ====================

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Get user from database"""
    return session.exec(select(User).where(User.username == username)).first()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current user from JWT token.

    This is a dependency that will be used to protect endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = get_user_by_username(session, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# ==================== Auth Endpoints ====================

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """Register a new user"""

    # Check if username already exists
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user with hashed password
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@app.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Login endpoint - returns JWT token.

    Use username and password to get an access token.
    """
    # Get user
    user = get_user_by_username(session, form_data.username)

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

# ==================== Protected Endpoints ====================

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user info.

    Requires authentication (JWT token).
    """
    return current_user

@app.get("/users/me/notes")
async def read_my_notes(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's notes.

    This is a protected endpoint - only authenticated users can access.
    """
    return {
        "user": current_user.username,
        "notes": [
            "Note 1 - Secret information",
            "Note 2 - Only visible to logged in user"
        ]
    }

@app.get("/admin/users")
async def list_all_users(
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    Admin only - list all users.

    Requires admin role.
    """
    users = session.exec(select(User)).all()
    return users

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: Session = Depends(get_session)
):
    """
    Admin only - delete a user.

    Requires admin role.
    """
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself"
        )

    session.delete(user)
    session.commit()

    return {"message": f"User {user.username} deleted"}

# ==================== Public Endpoints ====================

@app.get("/")
def public_route():
    """Public endpoint - no authentication required"""
    return {"message": "This is public, anyone can see this"}

@app.get("/health")
def health_check():
    """Health check - no authentication required"""
    return {"status": "healthy"}
```

## 🧪 Testing Authentication

### **1. Register a User**

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'
```

### **2. Login (Get Token)**

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret123"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### **3. Access Protected Endpoint**

```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer eyJhbGc..."
```

### **4. Using the Interactive Docs**

1. Go to `/docs`
2. Click the **"Authorize"** button (🔓)
3. Enter `username` and `password`
4. Click **"Authorize"**
5. Now you can test protected endpoints!

## 🎯 Security Best Practices

### **1. Use Environment Variables for Secrets**

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key-for-development")
```

### **2. Use Strong Secret Keys**

```python
# Generate a secure secret key
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)  # Use this in production!
```

### **3. Set Token Expiration**

```python
# Short-lived tokens are more secure
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

# For sensitive operations, use even shorter expiration
RESET_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
```

### **4. Implement Refresh Tokens**

```python
# Access token: Short-lived (15-30 min)
# Refresh token: Long-lived (7-30 days)

# User can get new access token using refresh token
# without re-entering credentials
```

### **5. Rate Limiting**

```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: "global")

@app.post("/token")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(...):
    pass
```

## 🎯 Practice Challenges

### **Challenge 1: Password Requirements**
Add password validation:
- Minimum 8 characters
- At least one uppercase letter
- At least one number
- At least one special character

### **Challenge 2: Email Verification**
Implement email verification:
- Send verification email on registration
- Create verification endpoint
- Mark user as verified

### **Challenge 3: Password Reset**
Build password reset flow:
- Request reset endpoint
- Generate reset token
- Verify token and reset password

## ❓ Troubleshooting

**Q: "Could not validate credentials" error?**
A: Check that your token is being sent correctly in the `Authorization: Bearer <token>` header.

**Q: Token expires too quickly!**
A: Increase `ACCESS_TOKEN_EXPIRE_MINUTES` or implement refresh tokens.

**Q: How do I test protected endpoints in /docs?**
A: Click the "Authorize" button and enter credentials. The token is automatically included in requests.

**Q: Should I use OAuth2 or JWT?**
A: JWT is a token format; OAuth2 is an authorization framework. FastAPI's OAuth2PasswordBearer uses JWT tokens.

## ➡️ What's Next?

Excellent! Now let's learn how to test your API!

**🎯 Continue Path A:**
1. **[Example 07: Auth Basics](../../examples/07-auth-basics/)** - Practice authentication
2. **[Chapter 8: Testing](../08-production/learn-testing.md)** - Test your APIs
3. **[Example 08: Testing](../../examples/08-testing/)** - Write comprehensive tests

**🏗️ Or Switch to Path B:**
Jump to **[Tutorial B7: E-Commerce Auth](apply-ecommerce-auth.md)** to secure your e-commerce app!

---

## 📚 Summary

**What you learned:**
- ✅ Authentication vs authorization
- ✅ Password hashing with bcrypt
- ✅ JWT token creation and validation
- ✅ Protecting endpoints with dependencies
- ✅ Role-based access control
- ✅ Security best practices

**Key takeaways:**
1. Never store plain text passwords
2. Use JWT for stateless authentication
3. Protect endpoints with FastAPI dependencies
4. Implement role-based access control
5. Keep secret keys secret and rotate them regularly

Amazing work! You now know how to secure your APIs. 🎉

---

*Author: bug6129 | FastAPI E-Commerce Tutorial | Tutorial A7*
