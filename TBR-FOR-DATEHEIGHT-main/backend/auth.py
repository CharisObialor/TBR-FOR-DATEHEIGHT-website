from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import User, UserRole, get_default_visible_modules
from permissions import migrate_old_permissions, get_modules_from_permissions, PERMISSION_SCHEMA
from config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM
JWT_EXPIRY_HOURS = settings.JWT_EXPIRY_HOURS
COOKIE_DOMAIN = settings.COOKIE_DOMAIN
COOKIE_SECURE = settings.COOKIE_SECURE

PASSWORD_RESET_EXPIRY_MINUTES = settings.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    })
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_password_reset_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRY_MINUTES)
    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "password_reset",
        "purpose": "password_reset",
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "password_reset" or payload.get("purpose") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token type",
            )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link has expired or is invalid. Please request a new one.",
        )


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def set_auth_cookie(response: Response, token: str, max_age: int = None):
    if max_age is None:
        max_age = JWT_EXPIRY_HOURS * 3600
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=max_age,
        expires=max_age,
        path="/",
        domain=COOKIE_DOMAIN,
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )


def clear_auth_cookie(response: Response):
    response.set_cookie(
        key="access_token",
        value="",
        max_age=0,
        expires=0,
        path="/",
        domain=COOKIE_DOMAIN,
        secure=COOKIE_SECURE,
        httponly=True,
        samesite="lax",
    )


async def get_token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization")
    if auth and auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]
    return request.cookies.get("access_token")


async def get_current_user_from_request(request: Request, db: AsyncIOMotorDatabase = None) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    token = await get_token_from_request(request)
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user_doc is None:
        raise credentials_exception

    if user_doc.get("visible_modules") is None:
        user_doc["visible_modules"] = get_default_visible_modules(user_doc.get("role", "client"))

    perms = user_doc.get("permissions") or {}
    role = user_doc.get("role", "client")
    has_old_keys = any(k in perms for k in ("can_upload", "can_review", "can_download", "can_approve"))
    has_new_keys = any(k in perms for k in PERMISSION_SCHEMA)
    if has_old_keys and not has_new_keys:
        user_doc["permissions"] = migrate_old_permissions(perms, role)
        user_doc["visible_modules"] = get_modules_from_permissions(user_doc["permissions"])
        try:
            await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "permissions": user_doc["permissions"],
                    "visible_modules": user_doc["visible_modules"],
                }},
            )
        except Exception:
            pass

    user = User(**user_doc)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncIOMotorDatabase = None) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user_doc is None:
        raise credentials_exception

    if user_doc.get("visible_modules") is None:
        user_doc["visible_modules"] = get_default_visible_modules(user_doc.get("role", "client"))

    perms = user_doc.get("permissions") or {}
    role = user_doc.get("role", "client")
    has_old_keys = any(k in perms for k in ("can_upload", "can_review", "can_download", "can_approve"))
    has_new_keys = any(k in perms for k in PERMISSION_SCHEMA)
    if has_old_keys and not has_new_keys:
        user_doc["permissions"] = migrate_old_permissions(perms, role)
        user_doc["visible_modules"] = get_modules_from_permissions(user_doc["permissions"])
        try:
            await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "permissions": user_doc["permissions"],
                    "visible_modules": user_doc["visible_modules"],
                }},
            )
        except Exception:
            pass

    user = User(**user_doc)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def require_role(*allowed_roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker


def get_user_scoped_query(query: dict, user_id: str, user_role: str) -> dict:
    admin_roles = ["super_admin", "operations_manager", "compliance_officer",
                   "tax_officer", "legal_officer", "finance_officer"]
    if user_role in admin_roles:
        return query
    scoped = query.copy()
    scoped["user_id"] = user_id
    return scoped
