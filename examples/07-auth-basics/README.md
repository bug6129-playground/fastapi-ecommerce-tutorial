# Authentication & Security Fundamentals

**Learn authentication and security through a Protected Notes API** 🔒

This example demonstrates essential authentication and security concepts using FastAPI. Learn how to implement JWT tokens, password hashing, protected endpoints, role-based access control, and user management through a secure notes application.

## 🎯 What You'll Learn

- **JWT Authentication**: Token creation, validation, and management
- **Password Security**: Bcrypt hashing and verification
- **Protected Endpoints**: Authentication requirements and dependencies
- **Authorization**: Role-based access control (RBAC)
- **User Management**: Registration, login, and account lifecycle
- **Security Headers**: Bearer token authentication
- **Error Handling**: Authentication and authorization errors
- **Session Management**: Token expiration and refresh patterns

## ⏱️ Time Commitment

**Estimated Time: 1.5 hours**

- Authentication basics: 25 minutes
- JWT implementation: 30 minutes
- Protected endpoints: 20 minutes
- Role-based access: 15 minutes

## 🚀 Quick Start

### Prerequisites

```bash
pip install "fastapi[standard]" sqlmodel python-jose[cryptography] passlib[bcrypt]
```

### Run the Example

```bash
# Navigate to this directory
cd examples/07-auth-basics

# Run the application
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

### Access the API

- **API Root**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Public Notes**: http://localhost:8000/notes/public
- **Login**: http://localhost:8000/auth/login
- **User Profile**: http://localhost:8000/auth/me (requires auth)

## 📚 Key Concepts Explained

### 1. Authentication vs Authorization

| Concept | Purpose | Example |
|---------|---------|---------|
| **Authentication** | Verify identity | "Who are you?" - Login with username/password |
| **Authorization** | Verify permissions | "What can you do?" - Admin-only endpoints |

### 2. JWT Token Structure

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNjQwOTk1MjAwfQ.signature
     ^^^^^^^^^^^^^^^^^                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                ^^^^^^^^^
          Header                                        Payload                                    Signature
```

**Header**: Algorithm and token type
**Payload**: User data and expiration
**Signature**: Verification hash

### 3. Password Security

```python
from passlib.context import CryptContext

# Hash password for storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("plaintext_password")

# Verify password during login
is_valid = pwd_context.verify("plaintext_password", hashed)
```

### 4. Protected Endpoint Pattern

```python
from fastapi import Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)  # Authentication required
):
    return {"message": f"Hello, {current_user.email}!"}
```

## 🎮 Hands-On Exercises

### Exercise 1: User Registration and Login

1. **Register New User**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "test@example.com",
          "full_name": "Test User",
          "password": "testpass123"
        }'
   ```

2. **Login to Get Token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "test@example.com",
          "password": "testpass123"
        }'
   ```

3. **Use Test Accounts**:
   ```bash
   # Login as admin
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "admin@example.com",
          "password": "admin123"
        }'
   ```

### Exercise 2: Using JWT Tokens

1. **Save Token from Login Response**:
   ```bash
   # Copy the access_token from login response
   export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   ```

2. **Get Current User Info**:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        "http://localhost:8000/auth/me"
   ```

3. **Access Protected Notes**:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        "http://localhost:8000/notes"
   ```

### Exercise 3: Creating and Managing Notes

1. **Create a Private Note**:
   ```bash
   curl -X POST "http://localhost:8000/notes" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "My Secret Note",
          "content": "This is my private note that only I can see.",
          "is_private": true,
          "tags": "personal,secret"
        }'
   ```

2. **Create a Public Note**:
   ```bash
   curl -X POST "http://localhost:8000/notes" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "Public Announcement",
          "content": "This note is visible to everyone.",
          "is_private": false,
          "tags": "public,announcement"
        }'
   ```

3. **Get Specific Note**:
   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
        "http://localhost:8000/notes/1"
   ```

4. **Try Unauthorized Access**:
   ```bash
   # This should fail with 401 Unauthorized
   curl "http://localhost:8000/notes/1"
   ```

### Exercise 4: Role-Based Access Control

1. **Login as Admin**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "admin@example.com",
          "password": "admin123"
        }'
   
   export ADMIN_TOKEN="<admin_token_here>"
   ```

2. **Access Admin Endpoints**:
   ```bash
   # Get all users (admin only)
   curl -H "Authorization: Bearer $ADMIN_TOKEN" \
        "http://localhost:8000/admin/users"
   
   # Get system statistics (admin only)
   curl -H "Authorization: Bearer $ADMIN_TOKEN" \
        "http://localhost:8000/admin/stats"
   ```

3. **Try Admin Endpoint as Regular User**:
   ```bash
   # This should fail with 403 Forbidden
   curl -H "Authorization: Bearer $TOKEN" \
        "http://localhost:8000/admin/users"
   ```

## 🔍 Code Structure Walkthrough

### 1. Authentication Dependencies

```python
# JWT Token validation dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    # Extract token from Authorization header
    token = credentials.credentials
    
    # Decode and validate JWT
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")
    
    # Get user from database
    user = get_user_by_email(session, email)
    if not user or not user.is_active:
        raise HTTPException(401, "Invalid credentials")
    
    return user
```

### 2. Role-Based Access Control

```python
# Admin-only dependency
async def get_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Admin access required")
    return current_user

# Usage in endpoint
@app.get("/admin/users")
async def get_all_users(
    admin_user: User = Depends(get_admin_user)  # Automatically checks for admin role
):
    # Only admins can reach this code
```

### 3. Resource Authorization

```python
@app.get("/notes/{note_id}")
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    note = session.get(Note, note_id)
    
    # Authorization check: users can only see their own private notes
    if note.is_private and note.owner_id != current_user.id:
        raise HTTPException(403, "Access denied: This is a private note")
    
    return note
```

### 4. Login Flow

```python
@app.post("/auth/login")
async def login_user(user_credentials: UserLogin, session: Session = Depends(get_session)):
    # 1. Authenticate user credentials
    user = authenticate_user(session, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(401, "Incorrect email or password")
    
    # 2. Create JWT token
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=timedelta(minutes=30)
    )
    
    # 3. Update last login timestamp
    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # 4. Return token and user info
    return Token(access_token=access_token, user=user)
```

## 🔐 Security Features Demonstrated

### 1. **Password Security**

```python
# Hash passwords before storage
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Verify passwords during login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 2. **JWT Token Management**

```python
# Create token with expiration
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Validate token
def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

### 3. **Authorization Levels**

| Level | Description | Implementation |
|-------|-------------|----------------|
| **Public** | No authentication required | No dependencies |
| **Authenticated** | Valid JWT token required | `Depends(get_current_user)` |
| **Active User** | Active account required | `Depends(get_current_active_user)` |
| **Admin Only** | Admin role required | `Depends(get_admin_user)` |
| **Resource Owner** | Owner of specific resource | Manual check in endpoint |

## 🎯 Authentication Patterns

### 1. **Registration Flow**

```python
# 1. Validate email uniqueness
existing_user = get_user_by_email(session, email)
if existing_user:
    raise HTTPException(400, "Email already registered")

# 2. Hash password
hashed_password = get_password_hash(password)

# 3. Create user record
user = User(email=email, hashed_password=hashed_password)
session.add(user)
session.commit()
```

### 2. **Authentication Middleware**

```python
# FastAPI Security with HTTPBearer
from fastapi.security import HTTPBearer

security = HTTPBearer()

# Automatic token extraction from Authorization header
async def protected_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials  # Extracted automatically
```

### 3. **Error Handling**

```python
# Standard authentication errors
credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# Authorization errors
access_denied = HTTPException(
    status_code=403,
    detail="Access denied: insufficient permissions"
)
```

## 🧪 Testing Your Understanding

### Challenge 1: Add Password Reset
Implement password reset functionality:
- Generate secure reset tokens
- Email token to user (simulate with logs)
- Allow password reset with valid token
- Token expiration handling

### Challenge 2: Implement Refresh Tokens
Add refresh token support:
- Issue long-lived refresh tokens
- Short-lived access tokens
- Refresh token rotation
- Revocation mechanism

### Challenge 3: Add User Roles
Extend the role system:
- Add "MODERATOR" role capabilities
- Implement hierarchical permissions
- Role-based note visibility
- Dynamic permission checking

### Challenge 4: Session Management
Implement advanced session features:
- Track active sessions
- Session invalidation
- Concurrent login limits
- Device/IP tracking

## 🔗 What's Next?

After mastering authentication, you're ready for:

1. **Testing** (Example 08) - Test authentication flows and security
2. **Advanced Security** - OAuth2, API keys, rate limiting
3. **Production Deployment** - HTTPS, secrets management, monitoring
4. **Real Applications** - Integrate auth with complex business logic

## 💡 Key Takeaways

- **Never store plaintext passwords** - Always hash with bcrypt or similar
- **JWT tokens are stateless** - All info is encoded in the token
- **Use HTTPS in production** - Tokens can be intercepted over HTTP
- **Implement proper error handling** - Don't leak sensitive information
- **Validate tokens on every request** - Tokens can be compromised
- **Role-based access is powerful** - Separate authentication from authorization

## 🐛 Common Pitfalls

1. **Storing passwords in plaintext**: Always hash passwords
2. **Not using HTTPS**: Tokens can be intercepted
3. **Long token expiry**: Increases security risk if compromised
4. **No token validation**: Always verify tokens server-side
5. **Weak secret keys**: Use long, random secret keys
6. **Inconsistent authorization**: Check permissions consistently

## 🔧 Security Best Practices

### Production Configuration

```python
# Environment-based configuration
import os

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "30"))

# Use strong password requirements
def validate_password_strength(password: str) -> bool:
    return (
        len(password) >= 8 and
        any(c.isupper() for c in password) and
        any(c.islower() for c in password) and
        any(c.isdigit() for c in password)
    )
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")  # Limit login attempts
async def login_user(...):
    pass
```

### Token Security

```python
# Add token blacklisting
BLACKLISTED_TOKENS = set()

def is_token_blacklisted(token: str) -> bool:
    return token in BLACKLISTED_TOKENS

def blacklist_token(token: str):
    BLACKLISTED_TOKENS.add(token)

# Logout endpoint
@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # Add current token to blacklist
    blacklist_token(current_user.token)
    return {"message": "Successfully logged out"}
```

---

**Ready to test your code? Continue with [Example 08: Testing Fundamentals](../08-testing/)!** 🧪