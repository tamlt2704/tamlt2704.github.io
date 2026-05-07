# Chapter 6: Authentication — JWT & Dependencies

[← Chapter 5: Database](chapter-05-database.md) | [Chapter 7: Relationships →](chapter-07-relationships.md)

---

## The Task

Marcus: "Anyone can hit any endpoint. I need: register, login (returns JWT), and protected routes that require the token."

---

## Dependencies

```bash
pip install python-jose[cryptography] passlib[bcrypt]
```

---

## Password Hashing

```python
# app/auth.py
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC

pwd_context = CryptContext(schemes=["bcrypt"])
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

---

## Auth Dependency (The Key Pattern)

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.auth import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = await db.get(User, user_id)
    if not user:
        raise credentials_exception
    return user
```

---

## Protecting Routes

```python
from app.dependencies import get_current_user
from app.models.user import User

@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),  # ← requires auth
    db: AsyncSession = Depends(get_db),
):
    db_project = Project(**project.model_dump(), owner_id=current_user.id)
    db.add(db_project)
    await db.flush()
    await db.refresh(db_project)
    return db_project
```

If no valid token → 401. If valid → `current_user` is the authenticated user. One line adds auth to any endpoint.

---

## Login & Register Endpoints

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == user.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return {"id": db_user.id, "email": db_user.email}


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
```

`OAuth2PasswordRequestForm` makes the login endpoint compatible with Swagger UI's "Authorize" button — you can test auth directly from `/docs`.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
OAuth2PasswordBearer            │ Extracts token from Authorization header
Depends(get_current_user)       │ Validates token, returns user
jwt.encode() / jwt.decode()     │ Create/verify JWT tokens
passlib bcrypt                  │ Hash & verify passwords
OAuth2PasswordRequestForm       │ Standard login form (works with /docs)
HTTPException(401)              │ Unauthorized response
────────────────────────────────┴──────────────────────────────────────
```

---

[← Chapter 5: Database](chapter-05-database.md) | [Chapter 7: Relationships →](chapter-07-relationships.md)
