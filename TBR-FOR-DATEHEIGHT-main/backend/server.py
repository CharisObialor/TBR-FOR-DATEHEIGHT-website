from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status, File, UploadFile, BackgroundTasks
from fastapi.responses import Response, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo.errors
import os
import re
import logging
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
import uuid
import httpx
import hmac
import hashlib
import json
from typing import List, Optional, Dict, Any
from collections import Counter
from io import BytesIO
import base64
import aiofiles
import orjson
from cachetools import TTLCache
from pydantic import BaseModel, Field
from urllib.parse import urlparse

from config import get_settings, Settings
from security import (
    sanitize_object, sanitize_string, sanitize_html,
    get_rate_limiter, RateLimiter,
    DomainRestrictionMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware,
    get_user_scoped_query, generate_api_key, hash_api_key
)
from error_handlers import (
    register_error_handlers, AppException, NotFoundException, ForbiddenException,
    UnauthorizedException, ValidationException, RateLimitException,
    ConflictException, ServiceUnavailableException
)
from indexes import ensure_indexes
from job_queue import get_job_queue, get_job_queue_instance, JobQueue, JobType, JobStatus

ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg'}

async def validate_file_extension(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not supported. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

async def delete_client_documents(order: dict):
    uploaded_docs = (order.get("form_data") or {}).get("uploaded_docs") or {}
    if not uploaded_docs:
        return
    for doc_name, doc_info in uploaded_docs.items():
        url = doc_info.get("url", "")
        if not url:
            continue
        filename = url.rsplit("/", 1)[-1]
        if not filename:
            continue
        file_path = UPLOAD_DIR / 'service-docs' / filename
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass

from models import (
    UserCreate, UserLogin, User, UserUpdate, Token, UserRole, AccountType,
    OTPRequest, OTPVerify, OTPResend, ResetPasswordRequest,
    RegisterResponse, VerifyEmailResponse, ForgotPasswordResponse,
    VerifyResetOTPResponse, ResetPasswordResponse, ResendOTPResponse,
    ServiceCreate, ServiceUpdate, Service, PricingTier, Order, OrderCreate, OrderBulkCreate, OrderUpdate, OrderStatus,
    Document, DocumentUpload, PaymentInitiate, Payment, RefundInitiate, Refund, AdminPaymentStats,
    Invoice, ResourceCreate, Resource,
    Notification, ChecklistRequest, ChecklistResponse,
    TicketCreate, TicketUpdate, Ticket, TicketStatus, TicketPriority, TicketMessage,
    AdminOrder, ReviewCreate, Review, ReviewAction,
    PERMISSION_UPLOAD, PERMISSION_REVIEW, PERMISSION_DOWNLOAD, PERMISSION_APPROVE,
    DEFAULT_ADMIN_PERMISSIONS, DEFAULT_SUPER_ADMIN_PERMISSIONS,
    DIVISION_ROLE_MAP, get_default_visible_modules,
    VISIBLE_MODULES_DASHBOARD, VISIBLE_MODULES_MY_TASKS,
    VISIBLE_MODULES_TICKETS, VISIBLE_MODULES_JOBS, VISIBLE_MODULES_REVIEW,
    VISIBLE_MODULES_PAYMENTS, VISIBLE_MODULES_HISTORY, VISIBLE_MODULES_ADMIN_USERS,
    SUPER_ADMIN_VISIBLE_MODULES, DEFAULT_ADMIN_VISIBLE_MODULES,
    WorkflowStage, WORKFLOW_STAGES_ORDER, PriorityLevel,
    ReviewQueueType, AuditAction, AuditLog, Escalation, ReviewQueueItem, WorkflowAnalytics,
    OrgCreateRequest, OrgJoinRequest, OrgAddMemberRequest,
    OrgInviteAcceptRequest, OrgInviteInfoResponse,
    CACVerificationRequest, CACVerificationResponse,
    PermissionUpdate,
    Wallet, WalletTransaction, WalletFundRequest, WalletPayRequest, WalletTransferRequest,
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_user_from_request,
    set_auth_cookie, clear_auth_cookie, decode_token,
)
from services.otp_service import (
    store_otp, validate_otp, check_otp_rate_limit, invalidate_pending_otps, mark_otp_sent,
    generate_otp, hash_otp,
)
from services.email_service import (
    send_email, build_otp_email_html, build_verification_link_email_html,
    build_password_changed_html, build_org_invitation_html,
    build_org_invite_registration_email_html,
    send_internal_email, build_payment_success_html,
    build_ticket_notification_html, build_reminder_html, INTERNAL_SENDER,
)

# CAC Verification Models
class CACVerificationRequest(BaseModel):
    id: str
    registration_type: str = Field(..., description="One of RC, BN, IT, LP, or LLP")
    registration_name: Optional[str] = None
    verification_consent: bool

class CACVerificationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

def check_permission(user: User, permission: str):
    from permissions import check_permission as _check
    _check(user, permission)
from models import CACVerificationRequest, CACVerificationResponse

settings = get_settings()

# MongoDB connection with optimized pool settings for high concurrency
mongo_url = settings.MONGO_URL
DB_NAME = settings.DB_NAME

client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
    minPoolSize=settings.MONGO_MIN_POOL_SIZE,
    maxIdleTimeMs=settings.MONGO_MAX_IDLE_TIME_MS,
    serverSelectionTimeoutMS=settings.MONGO_SERVER_SELECTION_TIMEOUT_MS,
    connectTimeoutMS=settings.MONGO_CONNECT_TIMEOUT_MS,
    socketTimeoutMS=30000,
    retryWrites=True,
    retryReads=True,
    tls=True,
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True,
)
db = client[DB_NAME]

async def ensure_db_connected():
    for attempt in range(5):
        try:
            await client.admin.command('ping')
            logger.info("MongoDB connected successfully")
            return
        except Exception as e:
            logger.warning(f"MongoDB connection attempt {attempt + 1}/5 failed: {e}")
            if attempt < 4:
                await asyncio.sleep(5)
    logger.error("MongoDB connection failed after 5 attempts")

_background_tasks = []

async def mongo_keepalive():
    while True:
        try:
            await asyncio.sleep(240)
            await client.admin.command('ping')
            logger.debug("MongoDB keepalive ping successful")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"MongoDB keepalive ping failed: {e}")
            for attempt in range(10):
                try:
                    await asyncio.sleep(10)
                    await client.admin.command('ping')
                    logger.info("MongoDB reconnected successfully")
                    break
                except Exception as e2:
                    logger.warning(f"MongoDB reconnect attempt {attempt + 1}/10 failed: {e2}")

MAX_OTP_RETRY_ATTEMPTS = 3
OTP_RETRY_INTERVAL_SECONDS = 60


async def retry_pending_otps():
    while True:
        try:
            await asyncio.sleep(OTP_RETRY_INTERVAL_SECONDS)
            now = datetime.now(timezone.utc).isoformat()
            cursor = db.otps.find({
                "sent": False,
                "used": False,
                "expires_at": {"$gte": now},
                "send_attempts": {"$lt": MAX_OTP_RETRY_ATTEMPTS},
            })
            async for otp_doc in cursor:
                purpose = otp_doc.get("purpose", "signup")
                recipient_name = otp_doc.get("recipient_name", "there")

                if purpose == "signup":
                    title = "Verify Your Account"
                    description = "Welcome to TBR! Use the code below to complete your registration."
                    subject = "Verify your TBR account"
                else:
                    title = "Reset Your Password"
                    description = "We received a request to reset your password. Use the code below to proceed."
                    subject = "Reset your TBR password"

                new_otp = generate_otp()
                new_hash = hash_otp(new_otp)
                await db.otps.update_one(
                    {"_id": otp_doc["_id"]},
                    {"$set": {"otp_hash": new_hash}},
                )

                html = build_otp_email_html(
                    recipient_name=recipient_name,
                    title=title,
                    description=description,
                    otp_code=new_otp,
                )
                try:
                    await send_email(otp_doc["email"], subject, html)
                    await mark_otp_sent(otp_doc["email"], purpose, db)
                    logger.info("Retry: delivered OTP for %s (%s)", otp_doc["email"], purpose)
                except Exception as e:
                    await db.otps.update_one(
                        {"_id": otp_doc["_id"]},
                        {"$inc": {"send_attempts": 1}},
                    )
                    logger.warning("Retry: send attempt %d/3 failed for %s", otp_doc.get("send_attempts", 0) + 1, otp_doc["email"])
        except Exception as e:
            logger.exception("OTP retry cycle error: %s", e)


# ──────────────────────────────────────────────
# RENDER FREE-TIER KEEPALIVE
# Pings self every 10 min so the instance never idles past Render's 15-min threshold.
# ──────────────────────────────────────────────
RENDER_KEEPALIVE_INTERVAL = 600  # 10 minutes

async def render_keepalive():
    import os as _os
    port = _os.getenv("PORT", "8000")
    url = f"http://127.0.0.1:{port}/api/"
    while True:
        try:
            await asyncio.sleep(RENDER_KEEPALIVE_INTERVAL)
            async with httpx.AsyncClient(timeout=10) as session:
                resp = await session.get(url)
                logger.info("Render keepalive ping → %s (status %s)", url, resp.status_code)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning("Render keepalive ping failed: %s", e)


BILLING_REMINDER_INTERVAL = 86400  # 24 hours

async def send_billing_reminders():
    """Check for orders with billing periods ending in 5 days and send reminders."""
    while True:
        try:
            await asyncio.sleep(BILLING_REMINDER_INTERVAL)
            now = datetime.now(timezone.utc)
            reminder_threshold = (now + timedelta(days=5)).isoformat()
            reminder_floor = (now + timedelta(days=4)).isoformat()

            cursor = db.orders.find({
                "next_billing_date": {"$gte": reminder_floor, "$lte": reminder_threshold},
                "status": {"$nin": [OrderStatus.UNPAID, OrderStatus.CANCELLED]},
                "billing_reminder_sent": {"$ne": True},
            }, {"_id": 0}).to_list(100)

            for order in cursor:
                user = await db.users.find_one({"id": order.get("user_id")}, {"_id": 0, "full_name": 1, "email": 1})
                if not user or not user.get("email"):
                    continue

                service = await db.services.find_one({"id": order.get("service_id")}, {"_id": 0, "title": 1})
                service_title = service.get("title", "Service") if service else "Service"

                days_remaining = max(1, (datetime.fromisoformat(order["billing_period_end"]) - now).days)

                payment = await db.payments.find_one({"reference": order.get("payment_reference")}, {"_id": 0, "amount": 1})
                total_paid = payment.get("amount", 0) if payment else 0

                html = build_billing_reminder_html(
                    client_name=user.get("full_name", "Client"),
                    service_title=service_title,
                    billing_period_end=order.get("billing_period_end", "")[:10],
                    days_remaining=days_remaining,
                    months_paid=order.get("months_ahead", 1),
                    total_amount=total_paid,
                )

                try:
                    await send_billing_email(user["email"], f"Billing Reminder: {service_title} — {days_remaining} day(s) remaining", html)
                    await db.orders.update_one(
                        {"id": order["id"]},
                        {"$set": {"billing_reminder_sent": True}}
                    )
                    logger.info("Billing reminder sent to %s for order %s", user["email"], order["id"][:8])
                except Exception as e:
                    logger.error("Failed to send billing reminder to %s: %s", user["email"], e)

        except Exception as e:
            logger.exception("Billing reminder cycle error: %s", e)


def db_retry(max_retries=3):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (pymongo.errors.AutoReconnect, pymongo.errors.ServerSelectionTimeoutError) as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"DB retry {attempt + 1}/{max_retries}: {e}")
                    await asyncio.sleep(1)
            return None
        return wrapper
    return decorator

# In-memory caches with TTL for frequent queries
services_cache = TTLCache(maxsize=100, ttl=60)
dashboard_cache = TTLCache(maxsize=200, ttl=30)
resources_cache = TTLCache(maxsize=50, ttl=120)
admin_stats_cache = TTLCache(maxsize=50, ttl=30)

# Shared httpx client for Korapay (connection reuse)
_korapay_client = None
async def get_korapay_client():
    global _korapay_client
    if _korapay_client is None:
        _korapay_client = httpx.AsyncClient(
            base_url="https://api.korapay.com/merchant/api/v1",
            timeout=15.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
    return _korapay_client

# Environment variables
EMERGENT_LLM_KEY = os.getenv("EMERGENT_LLM_KEY", "")

# Create the main app with orjson for faster JSON serialization
class ORJSONResponse(JSONResponse):
    media_type = "application/json"
    def render(self, content):
        return orjson.dumps(content, default=str)

app = FastAPI(
    default_response_class=ORJSONResponse,
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
)
api_router = APIRouter(prefix="/api")

# Include model imports for CAC verification route
from models import CACVerificationRequest, CACVerificationResponse

# Dependency to inject db
async def get_db() -> AsyncIOMotorDatabase:
    return db

# Fixed dependency for authenticated routes — supports Bearer header OR cookie
async def get_current_user_dep(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> User:
    return await get_current_user_from_request(request, db)

# Pagination helper
async def paginated_query(collection, query, sort_key=None, page: int = 1, limit: int = 20, projection=None):
    skip = (page - 1) * limit
    cursor = collection.find(query, projection or {"_id": 0})
    if sort_key:
        cursor = cursor.sort(sort_key, -1)
    items = await cursor.skip(skip).to_list(limit)
    total = await collection.count_documents(query)
    return items, total

# ──────────────────────────────────────────────
# AUTH ROUTES — OTP-based email verification flows
# ──────────────────────────────────────────────

PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=<>?/\\[\]{}|~]).{8,}$')

def _password_error():
    return HTTPException(
        status_code=400,
        detail="Password must be at least 8 characters with 1 uppercase, 1 number, and 1 special character."
    )

def _build_user_doc(user_id: str, data: UserCreate) -> dict:
    doc = {
        "id": user_id,
        "email": data.email,
        "full_name": data.full_name,
        "account_type": data.account_type.value if isinstance(data.account_type, AccountType) else data.account_type,
        "role": UserRole.CLIENT,
        "hashed_password": get_password_hash(data.password),
        "is_active": True,
        "email_verified": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if data.rc_number:
        doc["rc_number"] = data.rc_number
    if data.company_name:
        doc["company_name"] = data.company_name
    return doc


@api_router.post("/auth/register", response_model=RegisterResponse)
async def register(data: UserCreate, response: Response, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not PASSWORD_REGEX.match(data.password):
        raise _password_error()

    existing = await db.users.find_one({"email": data.email})
    if existing and existing.get("email_verified"):
        raise HTTPException(status_code=409, detail="Email already registered and verified.")
    if existing and not existing.get("email_verified"):
        await db.users.delete_one({"email": data.email})

    user_id = str(uuid.uuid4())
    user_doc = _build_user_doc(user_id, data)

    # Handle invite token
    pending_org_id = None
    pending_org_name = None
    if data.invite_token:
        invite = await db.organization_invites.find_one({"token": data.invite_token})
        if not invite:
            raise HTTPException(status_code=400, detail="Invalid or expired invite token.")
        if invite.get("accepted_at"):
            raise HTTPException(status_code=400, detail="This invite has already been used.")
        if invite.get("expires_at") and datetime.fromisoformat(invite["expires_at"]) < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="This invite has expired.")
        if invite["email"].lower() != data.email.lower():
            raise HTTPException(status_code=400, detail="This invite was sent to a different email address.")
        pending_org_id = invite["org_id"]
        pending_org_name = invite.get("org_name")
        user_doc["pending_org_id"] = pending_org_id
        user_doc["pending_invite_token"] = data.invite_token
        # Link invite to user
        await db.organization_invites.update_one(
            {"token": data.invite_token},
            {"$set": {"user_id": user_id}}
        )

    await db.users.insert_one(user_doc)

    await check_otp_rate_limit(data.email, "signup", db)
    otp = await store_otp(data.email, "signup", db, {"recipient_name": data.full_name})

    verify_token = create_access_token(
        data={"sub": user_id, "purpose": "email_verification"},
        expires_delta=timedelta(hours=24),
    )
    frontend_url = os.getenv("FRONTEND_URL", settings.cors_origins_list[0] if settings.cors_origins_list else "http://localhost:3000")
    verify_link = f"{frontend_url}/verify-email?token={verify_token}"

    html = build_otp_email_html(
        recipient_name=data.full_name,
        title="Verify Your Account",
        description="Welcome to TBR! Use the code below or click the link to verify your account.",
        otp_code=otp,
    )
    html += f'<p style="text-align:center;margin-top:20px;"><a href="{verify_link}" style="display:inline-block;background:#0F172A;color:#ffffff;font-size:14px;font-weight:600;padding:12px 32px;border-radius:8px;text-decoration:none;">Verify via Link Instead</a></p>'
    try:
        await send_email(data.email, "Verify your TBR account", html)
        await mark_otp_sent(data.email, "signup", db)
    except Exception as e:
        logger.warning("Inline OTP send failed for %s: %s — retry will pick it up", data.email, e)

    return RegisterResponse(message="Registration successful. Check your email for the OTP or verification link.")


@api_router.post("/auth/verify-email", response_model=VerifyEmailResponse)
async def verify_email(data: OTPVerify, response: Response, db: AsyncIOMotorDatabase = Depends(get_db)):
    await validate_otp(data.email, data.otp, "signup", db)

    user_doc = await db.users.find_one({"email": data.email})
    if not user_doc:
        raise HTTPException(status_code=400, detail="User not found.")

    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"email": data.email},
        {"$set": {"email_verified": True, "email_verified_at": now}}
    )
    user_doc["email_verified"] = True
    user_doc["email_verified_at"] = now

    user = User(**{k: v for k, v in user_doc.items() if k not in ["_id", "hashed_password"]})

    await _auto_assign_org(user_doc, db)

    token = create_access_token(data={"sub": user_doc["id"]})
    set_auth_cookie(response, token)
    return VerifyEmailResponse(
        message="Email verified successfully.",
        token=token,
        user=user,
    )


@api_router.get("/auth/verify-email-link")
async def verify_email_link(token: str, response: Response, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        from jose import JWTError, jwt
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("purpose") != "email_verification":
            raise HTTPException(status_code=400, detail="Invalid token purpose.")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link.")

    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=400, detail="User not found.")

    if user_doc.get("email_verified"):
        token = create_access_token(data={"sub": user_id})
        set_auth_cookie(response, token)
        return {"message": "Email already verified.", "verified": True}

    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"email_verified": True, "email_verified_at": now}}
    )
    user_doc["email_verified"] = True

    await _auto_assign_org(user_doc, db)

    access_token = create_access_token(data={"sub": user_id})
    set_auth_cookie(response, access_token)

    # Check for pending org invite
    pending_invite = None
    if user_doc.get("pending_org_id") and user_doc.get("pending_invite_token"):
        invite_doc = await db.organization_invites.find_one({
            "token": user_doc["pending_invite_token"],
            "user_id": user_id,
            "accepted_at": None,
        })
        if invite_doc:
            org_doc = await db.organizations.find_one({"id": invite_doc["org_id"]})
            if org_doc:
                pending_invite = {
                    "org_name": org_doc.get("name", "Organization"),
                    "invite_token": invite_doc["token"],
                }

    return {"message": "Email verified successfully.", "verified": True, "pending_invite": pending_invite}


def _parse_device_info(ua: str) -> str:
    ua = ua or ""
    device = "Unknown Device"
    os_name = ""

    # OS
    if "Windows NT 10" in ua:
        os_name = "Windows 10/11"
    elif "Windows NT 6.3" in ua:
        os_name = "Windows 8.1"
    elif "Windows" in ua:
        os_name = "Windows"
    elif "Mac OS X" in ua:
        v = ua.split("Mac OS X ")[-1].split(";")[0].replace("_", ".").strip()
        os_name = f"macOS {v}" if v else "macOS"
    elif "Android" in ua:
        v = ua.split("Android ")[-1].split(";")[0].strip()
        os_name = f"Android {v}" if v else "Android"
    elif "iPhone" in ua or "iPad" in ua:
        v = ua.split("OS ")[-1].split(" ")[0].replace("_", ".").strip()
        platform = "iPad" if "iPad" in ua else "iPhone"
        os_name = f"{platform} (iOS {v})" if v else platform
    elif "Linux" in ua:
        os_name = "Linux"
    elif "CrOS" in ua:
        os_name = "ChromeOS"

    # Browser
    browser = ""
    if "Edg/" in ua:
        v = ua.split("Edg/")[-1].split(" ")[0]
        browser = f"Edge {v}"
    elif "Chrome/" in ua and "Edg/" not in ua:
        v = ua.split("Chrome/")[-1].split(" ")[0]
        browser = f"Chrome {v}"
    elif "Firefox/" in ua:
        v = ua.split("Firefox/")[-1].split(" ")[0]
        browser = f"Firefox {v}"
    elif "Safari/" in ua and "Chrome/" not in ua:
        v = ua.split("Version/")[-1].split(" ")[0] if "Version/" in ua else ""
        browser = f"Safari {v}".strip()
    elif "OPR/" in ua:
        v = ua.split("OPR/")[-1].split(" ")[0]
        browser = f"Opera {v}"

    parts = [p for p in [browser, os_name] if p]
    return " ".join(parts) if parts else "Unknown Device"


async def _get_location_from_ip(ip: str) -> str:
    if not ip or ip in ("127.0.0.1", "::1", "unknown"):
        return "Local Network"
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    parts = [p for p in [data.get("city"), data.get("regionName"), data.get("country")] if p]
                    return ", ".join(parts) if parts else "Unknown Location"
    except Exception as e:
        logger.warning("IP geolocation lookup failed for %s: %s", ip, e)
    return "Unknown Location"


@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, response: Response, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    try:
        user_doc = await db.users.find_one({"email": credentials.email})
    except Exception:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable. Please try again.")

    if not user_doc:
        raise HTTPException(status_code=401, detail="No account found with this email.")

    # Check if account is locked
    if user_doc.get("locked_until"):
        try:
            locked_until = datetime.fromisoformat(user_doc["locked_until"])
            if datetime.now(timezone.utc) < locked_until:
                remaining = (locked_until - datetime.now(timezone.utc)).seconds
                raise HTTPException(
                    status_code=429,
                    detail=f"Account is temporarily locked. Please try again in {remaining // 60 + 1} minute{'s' if remaining // 60 + 1 != 1 else ''}."
                )
        except HTTPException:
            raise
        except Exception:
            pass

    if not verify_password(credentials.password, user_doc["hashed_password"]):
        attempts = user_doc.get("failed_attempts", 0) + 1
        update = {"$set": {"failed_attempts": attempts}}

        # Extract IP and device info
        ip_address = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
        if "," in ip_address:
            ip_address = ip_address.split(",")[0].strip()
        user_agent = request.headers.get("user-agent", "Unknown Device")
        device_info = _parse_device_info(user_agent)
        location = await _get_location_from_ip(ip_address)
        timestamp = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

        if attempts >= 3:
            lock_minutes = 1
            locked_until = datetime.now(timezone.utc) + timedelta(minutes=lock_minutes)
            update["$set"]["locked_until"] = locked_until.isoformat()
            await db.users.update_one({"email": credentials.email}, update)

            # Send suspicious login email to account owner
            try:
                from services.email_service import send_support_email, build_login_alert_html
                alert_html = build_login_alert_html(
                    client_name=user_doc.get("full_name", "there"),
                    email=credentials.email,
                    ip_address=ip_address,
                    device_info=device_info,
                    location=location,
                    attempt_count=attempts,
                    timestamp=timestamp,
                )
                await send_support_email(
                    credentials.email,
                    "Security Alert: Unauthorized Login Attempt on Your Account",
                    alert_html,
                )
            except Exception as e:
                logger.error("Failed to send login alert email to %s: %s", credentials.email, e)

            raise HTTPException(status_code=429, detail="Too many failed attempts. Account locked for 1 minute.")

        await db.users.update_one({"email": credentials.email}, update)
        remaining = 3 - attempts
        raise HTTPException(
            status_code=401,
            detail=f"Incorrect password. {remaining} attempt{'s' if remaining != 1 else ''} remaining."
        )

    await db.users.update_one(
        {"email": credentials.email},
        {"$unset": {"locked_until": "", "failed_attempts": ""}}
    )

    if not user_doc.get("is_active", True):
        raise HTTPException(status_code=400, detail="Account is inactive.")

    access_token = create_access_token(data={"sub": user_doc["id"]})
    set_auth_cookie(response, access_token)
    user = User(**{k: v for k, v in user_doc.items() if k not in ["_id", "hashed_password"]})

    # Check for pending org invite
    pending_invite = None
    if user_doc.get("pending_org_id") and user_doc.get("pending_invite_token"):
        invite_doc = await db.organization_invites.find_one({
            "token": user_doc["pending_invite_token"],
            "user_id": user_doc["id"],
            "accepted_at": None,
        })
        if invite_doc:
            org_doc = await db.organizations.find_one({"id": invite_doc["org_id"]})
            if org_doc:
                pending_invite = {
                    "org_name": org_doc.get("name", "Organization"),
                    "invite_token": invite_doc["token"],
                }

    return Token(access_token=access_token, user=user, pending_invite=pending_invite)


@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user_dep)):
    return current_user


@api_router.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(data: OTPRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user_doc = await db.users.find_one({"email": data.email})
    if not user_doc:
        raise HTTPException(
            status_code=400,
            detail={"error": "This email does not exist with TBR.", "code": "EMAIL_NOT_FOUND"}
        )

    await check_otp_rate_limit(data.email, data.purpose.value, db)
    otp = await store_otp(data.email, data.purpose.value, db, {"recipient_name": user_doc.get("full_name", "there")})

    html = build_otp_email_html(
        recipient_name=user_doc.get("full_name", "there"),
        title="Reset Your Password",
        description="We received a request to reset your password. Use the code below to proceed.",
        otp_code=otp,
    )
    try:
        await send_email(data.email, "Reset your TBR password", html)
        await mark_otp_sent(data.email, data.purpose.value, db)
    except Exception as e:
        logger.warning("Inline OTP send failed for %s: %s — retry will pick it up", data.email, e)

    return ForgotPasswordResponse(message="If this email exists, an OTP has been sent.")


@api_router.post("/auth/verify-reset-otp", response_model=VerifyResetOTPResponse)
async def verify_reset_otp(data: OTPVerify, response: Response, db: AsyncIOMotorDatabase = Depends(get_db)):
    await validate_otp(data.email, data.otp, "password_reset", db)

    user_doc = await db.users.find_one({"email": data.email})
    if not user_doc:
        raise HTTPException(status_code=400, detail="User not found.")

    reset_token = create_access_token(
        data={"sub": user_doc["id"], "purpose": "password_reset"},
        expires_delta=timedelta(minutes=15),
    )
    return VerifyResetOTPResponse(reset_token=reset_token)


@api_router.post("/auth/reset-password", response_model=ResetPasswordResponse)
async def reset_password(data: ResetPasswordRequest, request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")
    if not PASSWORD_REGEX.match(data.new_password):
        raise _password_error()

    try:
        from jose import JWTError, jwt
        payload = jwt.decode(data.reset_token, settings.JWT_SECRET, algorithms=["HS256"])
        if payload.get("purpose") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token purpose.")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    hashed = get_password_hash(data.new_password)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"hashed_password": hashed}}
    )

    changed_at = datetime.now(timezone.utc).strftime("%B %d, %Y at %I:%M %p UTC")
    ip_address = request.client.host if request.client else "Unknown"
    user_agent = request.headers.get("User-Agent", "Unknown")
    device_info = user_agent.split("/")[0] if "/" in user_agent else user_agent[:64]

    user_doc = await db.users.find_one({"id": user_id})
    if user_doc:
        html = build_password_changed_html(
            changed_at=changed_at,
            ip_address=ip_address,
            device_info=device_info,
        )
        await send_email(user_doc["email"], "Your TBR password was changed", html)

    return ResetPasswordResponse(message="Password reset successful.")


@api_router.post("/auth/resend-otp", response_model=ResendOTPResponse)
async def resend_otp(data: OTPResend, db: AsyncIOMotorDatabase = Depends(get_db)):
    purpose = data.purpose.value if hasattr(data.purpose, 'value') else data.purpose

    if purpose == "password_reset":
        user_doc = await db.users.find_one({"email": data.email})
        if not user_doc:
            raise HTTPException(
                status_code=400,
                detail={"error": "This email does not exist with TBR.", "code": "EMAIL_NOT_FOUND"}
            )
        recipient_name = user_doc.get("full_name", "there")
    else:
        user_doc = await db.users.find_one({"email": data.email})
        recipient_name = user_doc.get("full_name", "there") if user_doc else "there"

    await check_otp_rate_limit(data.email, purpose, db)
    await invalidate_pending_otps(data.email, purpose, db)

    otp = await store_otp(data.email, purpose, db, {"recipient_name": recipient_name})

    if purpose == "signup":
        title = "Verify Your Account"
        description = "Welcome to TBR! Use the code below to complete your registration."
        subject = "Verify your TBR account"
    else:
        title = "Reset Your Password"
        description = "We received a request to reset your password. Use the code below to proceed."
        subject = "Reset your TBR password"

    html = build_otp_email_html(recipient_name=recipient_name, title=title, description=description, otp_code=otp)
    try:
        await send_email(data.email, subject, html)
        await mark_otp_sent(data.email, purpose, db)
    except Exception as e:
        logger.warning("Inline OTP send failed for %s: %s — retry will pick it up", data.email, e)

    return ResendOTPResponse(message="OTP resent.")

@api_router.post("/auth/google")
async def google_auth(data: dict, response: Response, db: AsyncIOMotorDatabase = Depends(get_db)):
    credential = data.get("credential")
    if not credential:
        raise HTTPException(status_code=400, detail="Missing credential")

    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests

        google_client_id = settings.GOOGLE_CLIENT_ID
        if not google_client_id:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")

        info = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            google_client_id
        )

        email = info.get("email")
        name = info.get("name", email.split("@")[0])
        google_sub = info.get("sub")

        if not email:
            raise HTTPException(status_code=400, detail="Google account has no email")

        user_doc = await db.users.find_one({"email": email})

        if user_doc:
            if not user_doc.get("google_id"):
                await db.users.update_one({"email": email}, {"$set": {"google_id": google_sub}})
        else:
            user_id = str(uuid.uuid4())
            user_doc = {
                "id": user_id,
                "email": email,
                "full_name": name,
                "phone": None,
                "company_name": None,
                "role": UserRole.CLIENT,
                "hashed_password": None,
                "google_id": google_sub,
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.users.insert_one(user_doc)

        access_token = create_access_token(data={"sub": user_doc["id"]})
        set_auth_cookie(response, access_token)
        user = User(**{k: v for k, v in user_doc.items() if k not in ["_id", "hashed_password"]})

        return Token(access_token=access_token, user=user)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")


@api_router.post("/auth/logout")
async def logout(response: Response):
    clear_auth_cookie(response)
    return {"message": "Logged out successfully"}


# ──────────────────────────────────────────────
# ORGANIZATION ROUTES
# ──────────────────────────────────────────────

def _generate_join_code() -> str:
    import secrets
    import string
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


async def _auto_assign_org(user_doc: dict, db: AsyncIOMotorDatabase):
    if user_doc.get("account_type") != "organization" or not user_doc.get("rc_number"):
        return
    existing_org = await db.organizations.find_one({"rc_number": user_doc["rc_number"]})
    if not existing_org:
        org_id = str(uuid.uuid4())
        join_code = _generate_join_code()
        while await db.organizations.find_one({"join_code": join_code}):
            join_code = _generate_join_code()
        org_doc = {
            "id": org_id,
            "name": user_doc.get("company_name") or f"{user_doc['full_name']}'s Organization",
            "rc_number": user_doc["rc_number"],
            "company_name": user_doc.get("company_name"),
            "created_by": user_doc["id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "join_code": join_code,
        }
        await db.organizations.insert_one(org_doc)
        await db.users.update_one(
            {"id": user_doc["id"]},
            {"$set": {"org_id": org_id, "org_role": "admin"}}
        )
    else:
        await db.users.update_one(
            {"id": user_doc["id"]},
            {"$set": {"org_id": existing_org["id"], "org_role": "member"}}
        )


@api_router.post("/org/create")
async def create_org(
    data: OrgCreateRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.org_id:
        raise HTTPException(status_code=400, detail="You already belong to an organization.")

    existing = await db.organizations.find_one({"name": data.name})
    if existing:
        raise HTTPException(status_code=409, detail="An organization with this name already exists.")

    org_id = str(uuid.uuid4())
    join_code = _generate_join_code()

    while await db.organizations.find_one({"join_code": join_code}):
        join_code = _generate_join_code()

    org_doc = {
        "id": org_id,
        "name": data.name,
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "join_code": join_code,
        "rc_number": data.rc_number,
        "company_name": data.company_name,
    }
    await db.organizations.insert_one(org_doc)

    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"org_id": org_id, "org_role": "admin"}}
    )

    return {"message": "Organization created successfully", "org_id": org_id, "join_code": join_code}


@api_router.post("/org/join")
async def join_org(
    data: OrgJoinRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.org_id:
        raise HTTPException(status_code=400, detail="You already belong to an organization.")

    org = await db.organizations.find_one({"join_code": data.code.upper()})
    if not org:
        raise HTTPException(status_code=404, detail="Invalid join code. No organization found.")

    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"org_id": org["id"], "org_role": "member"}}
    )

    return {"message": f"You have joined {org['name']}.", "org_id": org["id"], "org_name": org["name"]}


@api_router.post("/org/add-member")
async def add_org_member(
    data: OrgAddMemberRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="You are not part of an organization.")

    # Check if user already exists and has an org
    target = await db.users.find_one({"email": data.email})
    if target and target.get("org_id"):
        raise HTTPException(status_code=409, detail="This user already belongs to an organization.")

    org = await db.organizations.find_one({"id": current_user.org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    # Prevent duplicate pending invites
    existing_invite = await db.organization_invites.find_one({
        "org_id": org["id"],
        "email": data.email,
        "accepted_at": None,
    })
    if existing_invite:
        # Check if expired
        if existing_invite.get("expires_at") and datetime.fromisoformat(existing_invite["expires_at"]) < datetime.now(timezone.utc):
            await db.organization_invites.delete_one({"token": existing_invite["token"]})
        else:
            raise HTTPException(status_code=409, detail="An active invite already exists for this email.")

    # Create invite record
    invite_token = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    invite_doc = {
        "id": str(uuid.uuid4()),
        "org_id": org["id"],
        "org_name": org["name"],
        "email": data.email,
        "token": invite_token,
        "created_by": current_user.id,
        "invited_by_name": current_user.full_name,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=7)).isoformat(),
        "user_id": target["id"] if target else None,
        "accepted_at": None,
    }
    await db.organization_invites.insert_one(invite_doc)

    # Send invite email with registration link
    frontend_url = os.getenv("FRONTEND_URL", settings.cors_origins_list[0] if settings.cors_origins_list else "http://localhost:3000")
    register_link = f"{frontend_url}/portal/register?invite={invite_token}"
    recipient_name = target.get("full_name", data.email) if target else data.email
    html = build_org_invite_registration_email_html(
        recipient_name=recipient_name,
        invited_by=current_user.full_name,
        org_name=org["name"],
        register_link=register_link,
    )
    try:
        await send_email(data.email, f"You've been invited to join {org['name']} on TBR Solutions", html)
    except Exception as e:
        logger.error("Failed to send invitation email to %s: %s", data.email, e)
        # Clean up the invite on send failure
        await db.organization_invites.delete_one({"token": invite_token})
        raise HTTPException(status_code=500, detail="Failed to send invitation email.")

    return {"message": f"Invitation sent to {data.email}."}


@api_router.get("/org/invite-info/{token}", response_model=OrgInviteInfoResponse)
async def get_invite_info(
    token: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    invite = await db.organization_invites.find_one({"token": token})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found.")
    if invite.get("accepted_at"):
        raise HTTPException(status_code=400, detail="This invite has already been used.")
    if invite.get("expires_at") and datetime.fromisoformat(invite["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This invite has expired.")

    return OrgInviteInfoResponse(
        org_name=invite["org_name"],
        email=invite["email"],
        invited_by=invite.get("invited_by_name", ""),
    )


@api_router.post("/org/accept-invite")
async def accept_org_invite(
    data: OrgInviteAcceptRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.org_id:
        raise HTTPException(status_code=400, detail="You already belong to an organization.")

    invite = await db.organization_invites.find_one({"token": data.token})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found.")
    if invite.get("accepted_at"):
        raise HTTPException(status_code=400, detail="This invite has already been used.")
    if invite.get("expires_at") and datetime.fromisoformat(invite["expires_at"]) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This invite has expired.")
    if invite.get("user_id") and invite["user_id"] != current_user.id:
        raise HTTPException(status_code=400, detail="This invite was not intended for you.")

    now = datetime.now(timezone.utc).isoformat()

    # Add user to org
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"org_id": invite["org_id"], "org_role": "member"}}
    )

    # Mark invite as accepted
    await db.organization_invites.update_one(
        {"token": data.token},
        {"$set": {"accepted_at": now}}
    )

    # Clear pending invite fields
    await db.users.update_one(
        {"id": current_user.id},
        {"$unset": {"pending_org_id": "", "pending_invite_token": ""}}
    )

    org = await db.organizations.find_one({"id": invite["org_id"]})
    return {"message": f"You have joined {org['name'] if org else 'the organization'}.",
            "org_id": invite["org_id"], "org_name": org["name"] if org else "Organization"}


@api_router.get("/org/my")
async def get_my_org(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        return {"org": None}

    org = await db.organizations.find_one({"id": current_user.org_id}, {"_id": 0})
    if not org:
        return {"org": None}

    org["org_role"] = current_user.org_role
    member_count = await db.users.count_documents({"org_id": current_user.org_id})
    org["member_count"] = member_count
    return {"org": org}


@api_router.get("/org/members")
async def list_org_members(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="You are not part of an organization.")

    members_cursor = db.users.find(
        {"org_id": current_user.org_id},
        {"_id": 0, "hashed_password": 0}
    )
    members = await members_cursor.to_list(100)
    return {"members": members}


@api_router.post("/org/leave")
async def leave_org(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="You are not part of an organization.")

    await db.users.update_one(
        {"id": current_user.id},
        {"$unset": {"org_id": "", "org_role": ""}}
    )

    return {"message": "You have left the organization."}


@api_router.post("/org/remove-member/{user_id}")
async def remove_org_member(
    user_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="You are not part of an organization.")
    if current_user.org_role != "admin":
        raise HTTPException(status_code=403, detail="Only organization admins can remove members.")

    target = await db.users.find_one({"id": user_id, "org_id": current_user.org_id})
    if not target:
        raise HTTPException(status_code=404, detail="No member found with this ID in your organization.")
    if target["id"] == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself. Use /org/leave instead.")

    await db.users.update_one(
        {"id": user_id},
        {"$unset": {"org_id": "", "org_role": ""}}
    )

    return {"message": f"{target.get('full_name', target['email'])} has been removed from the organization."}


@api_router.get("/org/code")
async def get_org_code(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="You are not part of an organization.")

    org = await db.organizations.find_one({"id": current_user.org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")

    return {
        "join_code": org["join_code"],
        "org_name": org["name"],
        "rc_number": org.get("rc_number"),
        "company_name": org.get("company_name"),
    }


@api_router.post("/org/regenerate-code")
async def regenerate_org_code(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not current_user.org_id:
        raise HTTPException(status_code=400, detail="You are not part of an organization.")

    new_code = _generate_join_code()
    while await db.organizations.find_one({"join_code": new_code}):
        new_code = _generate_join_code()

    await db.organizations.update_one(
        {"id": current_user.org_id},
        {"$set": {"join_code": new_code}}
    )

    return {"join_code": new_code}


# SERVICES ROUTES
@api_router.get("/services", response_model=List[Service])
async def list_services(
    category: Optional[str] = None,
    division: Optional[str] = None,
    subcategory: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    cache_key = f"services_{category or ''}_{division or ''}_{subcategory or ''}"
    if cache_key in services_cache:
        return services_cache[cache_key]

    query = {"is_active": True}
    if category:
        query["category"] = category
    if division:
        query["division"] = division
    if subcategory:
        query["subcategory"] = subcategory
    
    services = await db.services.find(query, {"_id": 0}).sort("title", 1).to_list(100)
    services_cache[cache_key] = services
    return services

@api_router.get("/services/{slug}", response_model=Service)
async def get_service(slug: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    service = await db.services.find_one({"slug": slug}, {"_id": 0})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@api_router.post("/services", response_model=Service)
async def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.OPERATIONS_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    service_doc = service_data.model_dump()
    service_doc["id"] = str(uuid.uuid4())
    service_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.services.insert_one(service_doc)
    return Service(**{k: v for k, v in service_doc.items() if k != "_id"})

# ADMIN SERVICE MANAGEMENT
@api_router.get("/admin/services")
async def admin_list_services(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin only")
    services = await db.services.find({}, {"_id": 0}).sort("division", 1).to_list(500)
    return services

@api_router.post("/admin/services", response_model=Service)
async def admin_create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin only")
    existing = await db.services.find_one({"slug": service_data.slug})
    if existing:
        raise HTTPException(status_code=400, detail="A service with this slug already exists")
    service_doc = service_data.model_dump()
    service_doc["id"] = str(uuid.uuid4())
    service_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    if not service_doc.get("pricing_tiers"):
        service_doc["pricing_tiers"] = []
    await db.services.insert_one(service_doc)
    services_cache.clear()
    return Service(**{k: v for k, v in service_doc.items() if k != "_id"})

@api_router.patch("/admin/services/{service_id}")
async def admin_update_service(
    service_id: str,
    update: ServiceUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin only")
    service = await db.services.find_one({"id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.services.update_one({"id": service_id}, {"$set": update_data})
    # Clear services cache
    services_cache.clear()
    updated = await db.services.find_one({"id": service_id}, {"_id": 0})
    return updated

@api_router.delete("/admin/services/{service_id}")
async def admin_delete_service(
    service_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin only")
    result = await db.services.delete_one({"id": service_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    services_cache.clear()
    return {"message": "Service deleted"}

@api_router.put("/admin/services/{service_id}/pricing")
async def admin_update_service_pricing(
    service_id: str,
    pricing_tiers: List[PricingTier],
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super admin only")
    service = await db.services.find_one({"id": service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    tiers_data = [t.model_dump() for t in pricing_tiers]
    await db.services.update_one({"id": service_id}, {"$set": {"pricing_tiers": tiers_data}})
    services_cache.clear()
    updated = await db.services.find_one({"id": service_id}, {"_id": 0})
    return updated

# ORDERS ROUTES
@api_router.post("/orders", response_model=Order)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Verify service exists
    service = await db.services.find_one({"id": order_data.service_id})
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Calculate deadline from service's estimated_timeline
    timeline = service.get("estimated_timeline", "").lower()
    numbers = [int(n) for n in re.findall(r"(\d+)", timeline)]
    if "month" in timeline:
        multiplier = 30
    elif "week" in timeline:
        multiplier = 7
    else:
        multiplier = 1
    deadline_days = 30
    if numbers:
        deadline_days = max(numbers) * multiplier
    deadline = (datetime.now(timezone.utc) + timedelta(days=deadline_days)).isoformat()

    now = datetime.now(timezone.utc).isoformat()
    order_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "service_id": order_data.service_id,
        "status": OrderStatus.UNPAID,
        "form_data": order_data.form_data,
        "notes": order_data.notes,
        "assigned_to": None,
        "progress": 0,
        "created_at": now,
        "updated_at": now,
        "deadline": deadline,
        "months_ahead": order_data.months_ahead,
    }

    await db.orders.insert_one(order_doc)

    return Order(**{k: v for k, v in order_doc.items() if k != "_id"})

@api_router.post("/orders/bulk")
async def create_bulk_orders(
    bulk_data: OrderBulkCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    bulk_id = str(uuid.uuid4())
    created = []
    for item in bulk_data.orders:
        service_id = item.get("service_id")
        if not service_id:
            continue
        service = await db.services.find_one({"id": service_id})
        if not service:
            continue

        timeline = service.get("estimated_timeline", "").lower()
        numbers = [int(n) for n in re.findall(r"(\d+)", timeline)]
        if "month" in timeline:
            multiplier = 30
        elif "week" in timeline:
            multiplier = 7
        else:
            multiplier = 1
        deadline_days = 30
        if numbers:
            deadline_days = max(numbers) * multiplier
        deadline = (datetime.now(timezone.utc) + timedelta(days=deadline_days)).isoformat()

        now = datetime.now(timezone.utc).isoformat()
        months_ahead = int(item.get("months_ahead", 1))
        order_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "service_id": service_id,
            "status": OrderStatus.UNPAID,
            "form_data": item.get("form_data", {}),
            "notes": item.get("notes", ""),
            "assigned_to": None,
            "progress": 0,
            "created_at": now,
            "updated_at": now,
            "deadline": deadline,
            "bulk_id": bulk_id,
            "months_ahead": months_ahead,
        }
        await db.orders.insert_one(order_doc)
        created.append(order_doc)

    return {"bulk_id": bulk_id, "orders": [Order(**{k: v for k, v in o.items() if k != "_id"}) for o in created]}

async def activate_orders_on_payment(payment_ref: str, db: AsyncIOMotorDatabase):
    """Activate all unpaid orders linked to a payment reference."""
    now = datetime.now(timezone.utc).isoformat()
    orders = await db.orders.find(
        {"payment_reference": payment_ref, "status": OrderStatus.UNPAID},
        {"_id": 0}
    ).to_list(100)

    if not orders:
        return

    # Get payment info for email
    payment = await db.payments.find_one({"reference": payment_ref}, {"_id": 0})
    payment_amount = payment.get("amount", 0) if payment else 0

    # Get client info
    client_id = orders[0].get("user_id")
    client = await db.users.find_one({"id": client_id}, {"_id": 0, "full_name": 1, "email": 1, "company_name": 1}) if client_id else None
    client_name = client.get("full_name") or client.get("company_name") or "Client" if client else "Client"

    # Notify all admins about payment
    admin_users = await db.users.find(
        {"role": {"$in": ["super_admin", "operations_manager"]}, "is_active": True},
        {"_id": 0, "id": 1, "email": 1}
    ).to_list(100)

    for admin in admin_users:
        await send_notification(
            admin["id"],
            "TBR GOT PAID!!",
            f"Payment of ₦{payment_amount:,.2f} received from {client_name}. Reference: {payment_ref}",
            db
        )

    # Send email notification to admins
    for order in orders:
        service = await db.services.find_one({"id": order["service_id"]})
        division = service.get("division", "") if service else ""
        service_title = service.get("title", "Service") if service else "Service"
        target_role = DIVISION_ROLE_MAP.get(division, "operations_manager")
        assignee = await db.users.find_one({"role": target_role, "is_active": True})
        assigned_to = assignee["id"] if assignee else None

        # Calculate billing period for recurring services
        months_ahead = order.get("months_ahead", 1)
        billing_update = {}
        if service and service.get("is_recurring"):
            now_dt = datetime.now(timezone.utc)
            billing_update = {
                "billing_period_start": now_dt.isoformat(),
                "billing_period_end": (now_dt + timedelta(days=30 * months_ahead)).isoformat(),
                "next_billing_date": (now_dt + timedelta(days=30 * months_ahead - 5)).isoformat(),
            }

        await db.orders.update_one(
            {"id": order["id"]},
            {"$set": {
                "status": OrderStatus.PENDING_REVIEW,
                "assigned_to": assigned_to,
                "updated_at": now,
                **billing_update,
            }}
        )

        if assigned_to:
            await send_notification(
                assigned_to,
                "New Job Assigned",
                f"A new {division} job has been assigned to you. Service: {service_title}",
                db
            )

    # Send "TBR GOT PAID!!" email to all admin emails
    if admin_users:
        service_titles = []
        for order in orders:
            svc = await db.services.find_one({"id": order.get("service_id")}, {"_id": 0, "title": 1})
            service_titles.append(svc.get("title", "Service") if svc else "Service")
        services_summary = ", ".join(set(service_titles))
        html = build_payment_success_html(client_name, payment_amount, services_summary, payment_ref)
        for admin in admin_users:
            if admin.get("email"):
                try:
                    await send_internal_email(admin["email"], "TBR GOT PAID!!", html)
                except Exception as e:
                    logger.error("Failed to send payment email to %s: %s", admin["email"], e)

@api_router.get("/orders", response_model=List[Order])
async def list_orders(
    request: Request,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
):
    if current_user.role == UserRole.CLIENT:
        query = {"user_id": current_user.id}
    else:
        query = {}
    orders, total = await paginated_query(db.orders, query, "created_at", page, limit)
    return orders

@api_router.get("/orders/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return order

@api_router.patch("/orders/{order_id}", response_model=Order)
async def update_order(
    order_id: str,
    update_data: OrderUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == UserRole.CLIENT:
        if order["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        allowed = {k: v for k, v in update_data.model_dump(exclude_none=True).items() if k in ("form_data", "notes")}
        if not allowed:
            raise HTTPException(status_code=403, detail="Clients can only update form_data and notes")
        allowed["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.orders.update_one({"id": order_id}, {"$set": allowed})
        updated_order = await db.orders.find_one({"id": order_id}, {"_id": 0})
        return Order(**updated_order)

    update_dict = {k: v for k, v in update_data.model_dump(exclude_none=True).items()}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    new_status = update_dict.get("status")
    if new_status in (OrderStatus.APPROVED,):
        check_permission(current_user, PERMISSION_APPROVE)
    if new_status in (OrderStatus.CANCELLED, OrderStatus.COMPLETED):
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Only super admins can cancel or complete orders")

    # Non-super-admin admins can only update progress, notes, and status on their assigned orders
    if current_user.role in ADMIN_ROLES and current_user.role != UserRole.SUPER_ADMIN:
        if order.get("assigned_to") != current_user.id:
            allowed = {k: v for k, v in update_dict.items() if k in ("progress",)}
            if not allowed:
                raise HTTPException(status_code=403, detail="You can only update progress on your assigned orders")
            update_dict = allowed
            update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
        else:
            new_status = update_dict.get("status")
            if new_status and new_status not in (OrderStatus.SUBMITTED,):
                raise HTTPException(status_code=403, detail="You can only submit your assigned orders for review")
            if not new_status:
                allowed = {k: v for k, v in update_dict.items() if k in ("progress", "notes")}
                update_dict = allowed
                update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()

    if update_dict.get("status") == OrderStatus.COMPLETED:
        await delete_client_documents(order)
        existing_form = order.get("form_data") or {}
        existing_form.pop("uploaded_docs", None)
        update_dict["form_data"] = existing_form

    if update_dict.get("progress") is not None:
        prog = update_dict["progress"]
        if not isinstance(prog, int) or prog < 0 or prog > 100:
            raise HTTPException(status_code=400, detail="Progress must be an integer between 0 and 100")

    await db.orders.update_one({"id": order_id}, {"$set": update_dict})

    # Notify super admins when the order is submitted for review
    if update_dict.get("status") == OrderStatus.SUBMITTED:
        super_admins = await db.users.find({"role": UserRole.SUPER_ADMIN}, {"_id": 0, "id": 1}).to_list(100)
        for sa in super_admins:
            await send_notification(
                sa["id"],
                "Order Ready for Review",
                f"Order #{order_id[:8]} has been submitted for review by {current_user.full_name}.",
                db
            )

    updated_order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    return Order(**updated_order)

@api_router.delete("/orders/{order_id}")
async def delete_order(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == UserRole.CLIENT and order.get("status") != OrderStatus.UNPAID:
        raise HTTPException(status_code=400, detail="Cannot delete an order after payment has been confirmed")
    await db.orders.delete_one({"id": order_id})
    await db.documents.delete_many({"order_id": order_id})
    return {"message": "Order deleted"}

# DOCUMENTS ROUTES
@api_router.post("/documents", response_model=Document)
async def upload_document(
    document_data: DocumentUpload,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # Verify order exists and user has access
    order = await db.orders.find_one({"id": document_data.order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    check_document_access(order, current_user)
    
    doc = {
        "id": str(uuid.uuid4()),
        "order_id": document_data.order_id,
        "user_id": current_user.id,
        "document_type": document_data.document_type,
        "file_name": document_data.file_name,
        "file_url": document_data.file_url,
        "file_size": document_data.file_size,
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.documents.insert_one(doc)
    return Document(**{k: v for k, v in doc.items() if k != "_id"})

@api_router.get("/documents", response_model=List[Document])
async def list_documents(
    order_id: Optional[str] = None,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    query = {}
    if order_id:
        query["order_id"] = order_id
    
    if current_user.role == UserRole.CLIENT:
        query["user_id"] = current_user.id
    
    documents = await db.documents.find(query, {"_id": 0}).to_list(100)
    return documents

# Helper: check if user can access order documents (assigned admin or superadmin)
def check_document_access(order: dict, user: User):
    if user.role == UserRole.SUPER_ADMIN:
        return
    if user.role in ADMIN_ROLES:
        if order.get("assigned_to") != user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not assigned to this job. Only assigned admins can access documents."
            )
        return
    if user.role == UserRole.CLIENT and order.get("user_id") == user.id:
        return
    raise HTTPException(status_code=403, detail="Not authorized to access these documents")

# ORDER ASSIGNMENT & SUBMISSION
async def send_notification(user_id: str, title: str, message: str, db: AsyncIOMotorDatabase):
    try:
        notif = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": "job_assignment",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.notifications.insert_one(notif)
        logger.info(f"Notification sent to user {user_id}: {title}")
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")

@api_router.post("/orders/{order_id}/assign", response_model=None)
async def assign_order(
    order_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    assigned_to = body.get("assigned_to")
    notes = body.get("notes", order.get("notes"))
    if not assigned_to:
        raise HTTPException(status_code=400, detail="assigned_to is required")

    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "assigned_to": assigned_to,
            "notes": notes,
            "status": OrderStatus.IN_PROGRESS,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    # Find assignee user
    assignee = await db.users.find_one({"id": assigned_to}, {"_id": 0, "hashed_password": 0})
    if assignee:
        assignee_name = assignee.get("full_name", assigned_to)
        assignee_email = assignee.get("email", "")
        await send_notification(
            assigned_to,
            "New Job Assignment",
            f"You have been assigned to job #{order_id[:8]}. Service: {order.get('service_id', 'N/A')}. Notes: {notes or 'None'}",
            db
        )

    updated = await db.orders.find_one({"id": order_id}, {"_id": 0})
    return {"order": updated, "assigned_user": assignee}

# New: List unassigned orders (for admin dashboard / picking)
@api_router.get("/admin/orders/unassigned", response_model=None)
async def list_unassigned_orders(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {"assigned_to": None, "status": {"$ne": OrderStatus.UNPAID}}
    orders, total = await paginated_query(db.orders, query, "created_at", page, limit)
    enriched = []
    for o in orders:
        enriched.append(await enrich_order(o, db))
    return {"orders": enriched, "total": total, "page": page, "limit": limit}

# New: Admin picks an unassigned job (assigns themselves)
@api_router.post("/admin/orders/{order_id}/pick", response_model=None)
async def pick_unassigned_order(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES or current_user.role == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only non-super-admin admins can pick jobs")
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.get("assigned_to"):
        raise HTTPException(status_code=400, detail="This job is already assigned")
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "assigned_to": current_user.id,
            "status": OrderStatus.IN_PROGRESS,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    await send_notification(
        current_user.id,
        "Job Self-Assignment",
        f"You have picked job #{order_id[:8]}. Service: {order.get('service_id', 'N/A')}",
        db
    )
    updated = await db.orders.find_one({"id": order_id}, {"_id": 0})
    enriched = await enrich_order(updated, db)
    return {"order": enriched}

# New: Limited order detail for non-assigned admins
@api_router.get("/admin/orders/{order_id}/overview", response_model=None)
async def get_order_overview(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    enriched = await enrich_order(order, db)
    if current_user.role != UserRole.SUPER_ADMIN and order.get("assigned_to") == current_user.id:
        return enriched
    client = await db.users.find_one({"id": order.get("user_id")}, {"_id": 0, "hashed_password": 0})
    limited = {
        "id": order["id"],
        "service_title": enriched.get("service_title", ""),
        "service_category": enriched.get("service_category", ""),
        "service_division": enriched.get("service_division", ""),
        "deadline": order.get("deadline"),
        "time_remaining_days": enriched.get("time_remaining_days"),
        "status": order.get("status"),
        "assigned_to": order.get("assigned_to"),
        "assigned_to_name": enriched.get("assigned_to_name"),
        "assigned_to_email": enriched.get("assigned_to_email"),
        "client_name": enriched.get("client_name"),
        "client_email": enriched.get("client_email"),
        "client_company": enriched.get("client_company"),
        "created_at": order.get("created_at"),
        "notes": order.get("notes", ""),
    }
    tickets = await db.tickets.find({"order_id": order_id}, {"_id": 0}).to_list(100)
    limited["tickets"] = tickets
    return {"limited": True, "order": limited}

# New: Get tickets for a specific order
@api_router.get("/admin/orders/{order_id}/tickets", response_model=None)
async def list_order_tickets(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    tickets = await db.tickets.find({"order_id": order_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    enriched = []
    for t in tickets:
        enriched.append(await enrich_ticket(t, db))
    return {"tickets": enriched}

@api_router.post("/orders/{order_id}/submit-document", response_model=None)
async def submit_order_document(
    order_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    await validate_file_extension(file)

    if current_user.role not in ADMIN_ROLES and current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if current_user.role in ADMIN_ROLES:
        check_permission(current_user, PERMISSION_UPLOAD)

    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Only allow submission to client after review approval
    if order.get("status") != OrderStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Order must be reviewed and approved before submitting to client")

    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role in ADMIN_ROLES:
        check_document_access(order, current_user)

    ORDER_DOC_DIR = UPLOAD_DIR / 'orders'
    ORDER_DOC_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower() if file.filename else '.bin'
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = ORDER_DOC_DIR / unique_name
    content = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    url = f"/uploads/orders/{unique_name}"
    doc = {
        "id": str(uuid.uuid4()),
        "order_id": order_id,
        "user_id": current_user.id,
        "document_type": "submission",
        "file_name": file.filename or "document",
        "file_url": url,
        "file_size": len(content),
        "uploaded_at": datetime.now(timezone.utc).isoformat()
    }
    await db.documents.insert_one(doc)

    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "status": OrderStatus.COMPLETED,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    # Notify the client that their order is complete
    await send_notification(
        order["user_id"],
        "Order Completed",
        f"Your order #{order_id[:8]} has been completed. Documents are now available.",
        db
    )

    return {"document": doc}

@api_router.get("/orders/{order_id}/documents", response_model=List[Document])
async def list_order_documents(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    check_document_access(order, current_user)
    documents = await db.documents.find({"order_id": order_id}, {"_id": 0}).to_list(100)
    return documents

@api_router.get("/orders/{order_id}/documents/{document_id}/download")
async def download_order_document(
    order_id: str,
    document_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    check_document_access(order, current_user)
    doc = await db.documents.find_one({"id": document_id, "order_id": order_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    file_path = ROOT_DIR / doc["file_url"].lstrip("/")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(
        path=str(file_path),
        filename=doc["file_name"],
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc["file_name"]}"'}
    )

# ADMIN ORDERS (enriched with assignee info)
async def enrich_order(order: dict, db: AsyncIOMotorDatabase) -> dict:
    enriched = dict(order)
    if order.get("assigned_to"):
        assignee = await db.users.find_one({"id": order["assigned_to"]}, {"_id": 0, "hashed_password": 0})
        if assignee:
            enriched["assigned_to_name"] = assignee.get("full_name", "")
            enriched["assigned_to_email"] = assignee.get("email", "")
    if order.get("user_id"):
        client = await db.users.find_one({"id": order["user_id"]}, {"_id": 0, "hashed_password": 0})
        if client:
            enriched["client_name"] = client.get("full_name", "")
            enriched["client_email"] = client.get("email", "")
            enriched["client_company"] = client.get("company_name", "")
    fd = order.get("form_data") or {}
    if fd.get("company_name") and not enriched.get("client_company"):
        enriched["client_company"] = fd["company_name"]
    if fd.get("contact_person") and not enriched.get("client_name"):
        enriched["client_name"] = fd["contact_person"]
    if fd.get("email") and not enriched.get("client_email"):
        enriched["client_email"] = fd["email"]
    if fd.get("phone"):
        enriched["client_phone"] = fd["phone"]
    if order.get("deadline"):
        try:
            deadline = datetime.fromisoformat(order["deadline"])
            remaining = (deadline - datetime.now(timezone.utc)).total_seconds() / 86400
            enriched["time_remaining_days"] = round(remaining, 1)
        except:
            pass
    if order.get("service_id"):
        svc = await db.services.find_one({"id": order["service_id"]}, {"_id": 0, "title": 1, "category": 1, "division": 1, "subcategory": 1})
        if svc:
            enriched["service_title"] = svc.get("title", "")
            enriched["service_category"] = svc.get("category", "")
            enriched["service_division"] = svc.get("division", "")
            enriched["service_subcategory"] = svc.get("subcategory", "")
    reviews = await db.reviews.find({"order_id": order["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    enriched["reviews"] = reviews
    if reviews:
        enriched["review"] = reviews[0]
    enriched["assigned_reviewers"] = order.get("assigned_reviewers", [])
    enriched["reviewed_by"] = order.get("reviewed_by", [])
    return enriched

async def enrich_ticket(ticket: dict, db: AsyncIOMotorDatabase) -> dict:
    enriched = dict(ticket)
    if ticket.get("user_id"):
        client = await db.users.find_one({"id": ticket["user_id"]}, {"_id": 0, "hashed_password": 0})
        if client:
            enriched["client_name"] = client.get("full_name", "")
            enriched["client_email"] = client.get("email", "")
    if ticket.get("assigned_to"):
        assignee = await db.users.find_one({"id": ticket["assigned_to"]}, {"_id": 0, "hashed_password": 0})
        if assignee:
            enriched["assigned_to_name"] = assignee.get("full_name", "")
    return enriched

@api_router.get("/admin/orders", response_model=None)
async def list_admin_orders(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    mine: bool = False,
    status: Optional[str] = None,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {}
    if mine or current_user.role != UserRole.SUPER_ADMIN:
        query["assigned_to"] = current_user.id
    if status:
        query["status"] = status
    else:
        # Hide unpaid orders from admin unless explicitly filtering for them
        query["status"] = {"$ne": OrderStatus.UNPAID}
    orders, total = await paginated_query(db.orders, query, "created_at", page, limit)
    enriched = []
    for o in orders:
        enriched.append(await enrich_order(o, db))
    return {"orders": enriched, "total": total, "page": page, "limit": limit}

@api_router.post("/orders/{order_id}/review", response_model=None)
async def review_order(
    order_id: str,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    check_permission(current_user, PERMISSION_REVIEW)
    if review_data.action == ReviewAction.APPROVED:
        check_permission(current_user, PERMISSION_APPROVE)

    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Prevent same admin from reviewing twice
    existing = await db.reviews.find_one({"order_id": order_id, "reviewer_id": current_user.id})
    if existing:
        raise HTTPException(status_code=400, detail="You have already submitted a review for this order")

    review_doc = {
        "id": str(uuid.uuid4()),
        "order_id": order_id,
        "reviewer_id": current_user.id,
        "reviewer_name": current_user.full_name,
        "action": review_data.action,
        "comments": review_data.comments,
        "rating": review_data.rating,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.reviews.insert_one(review_doc)

    # Track who reviewed
    reviewed_by = order.get("reviewed_by") or []
    if current_user.id not in reviewed_by:
        reviewed_by.append(current_user.id)

    # Count approved reviews
    approved_count = await db.reviews.count_documents({"order_id": order_id, "action": ReviewAction.APPROVED})

    # Only set APPROVED if enough reviews and action is approved
    if review_data.action == ReviewAction.APPROVED and approved_count >= MIN_REVIEWS_FOR_APPROVAL:
        new_status = OrderStatus.APPROVED
    elif review_data.action == ReviewAction.CHANGES_REQUESTED:
        new_status = OrderStatus.PENDING_REVIEW
    else:
        new_status = order.get("status")

    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "status": new_status,
            "reviewed_by": reviewed_by,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    await send_notification(
        order["user_id"],
        "Order Review Completed",
        f"Your order #{order_id[:8]} has been {review_data.action.value}. Comments: {review_data.comments}",
        db
    )
    if order.get("assigned_to"):
        await send_notification(
            order["assigned_to"],
            "Review Received",
            f"Order #{order_id[:8]} you worked on has been reviewed: {review_data.action.value}. Comments: {review_data.comments}",
            db
        )

    return {"review": review_doc, "approved_count": approved_count, "required": MIN_REVIEWS_FOR_APPROVAL}

@api_router.post("/orders/{order_id}/remind", response_model=None)
async def remind_order(
    order_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.get("assigned_to"):
        raise HTTPException(status_code=400, detail="Order is not assigned to anyone")

    assigned_user = await db.users.find_one({"id": order["assigned_to"]}, {"_id": 0, "full_name": 1, "email": 1})
    assignee_name = assigned_user.get("full_name", "Officer") if assigned_user else "Officer"

    deadline_str = order.get("deadline", "Not set")
    message = f"Reminder for order #{order_id[:8]}. This job needs your attention. Deadline: {deadline_str}"

    # In-app notification
    await send_notification(
        order["assigned_to"],
        "Reminder: Job Due Soon",
        message,
        db
    )

    # Email notification
    if assigned_user and assigned_user.get("email"):
        html = build_reminder_html(
            "Reminder: Job Due Soon",
            f"Hi {assignee_name}, {message}",
            order_id
        )
        try:
            await send_internal_email(assigned_user["email"], "Reminder: Job Due Soon", html)
        except Exception as e:
            logger.error("Failed to send reminder email to %s: %s", assigned_user["email"], e)

    return {"message": "Reminder sent"}

MIN_REVIEWS_FOR_APPROVAL = 2

@api_router.post("/orders/{order_id}/assign-reviewers", response_model=None)
async def assign_reviewers(
    order_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can assign reviewers")

    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    reviewer_ids = body.get("reviewer_ids", [])
    if not reviewer_ids or len(reviewer_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 reviewers must be assigned")
    if len(reviewer_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 reviewers allowed")

    # Validate all reviewer IDs exist and are admin roles
    admin_roles = [r.value for r in UserRole if r != UserRole.CLIENT and r != UserRole.SUPER_ADMIN]
    valid_reviewers = []
    for rid in reviewer_ids:
        user_doc = await db.users.find_one({"id": rid, "role": {"$in": admin_roles}}, {"_id": 0, "id": 1, "full_name": 1, "email": 1})
        if not user_doc:
            raise HTTPException(status_code=400, detail=f"Reviewer {rid} not found or is not an admin")
        valid_reviewers.append(user_doc)

    await db.orders.update_one(
        {"id": order_id},
        {"$set": {
            "assigned_reviewers": reviewer_ids,
            "reviewed_by": [],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )

    for r in valid_reviewers:
        await send_notification(
            r["id"],
            "Review Assignment",
            f"You have been assigned to review order #{order_id[:8]}. Please submit your review.",
            db
        )

    return {"message": f"Reviewers assigned successfully", "reviewers": valid_reviewers}

# PAYMENT ROUTES
@api_router.post("/payments/initialize")
async def initialize_payment(
    payment_data: PaymentInitiate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    reference = f"tbr_{uuid.uuid4().hex[:16]}"

    # Bulk payment: linked to multiple orders via bulk_id
    if payment_data.bulk_id:
        orders = await db.orders.find(
            {"bulk_id": payment_data.bulk_id, "user_id": current_user.id, "status": OrderStatus.UNPAID},
            {"_id": 0}
        ).to_list(100)
        if not orders:
            raise HTTPException(status_code=404, detail="No unpaid orders found for this bulk ID")

        total_amount = 0
        for o in orders:
            order_amount = o.get("form_data", {}).get("agreed_amount", 0) or 0
            if order_amount <= 0:
                svc = await db.services.find_one({"id": o["service_id"]})
                if svc and svc.get("pricing_tiers"):
                    order_amount = float(svc["pricing_tiers"][0].get("price", 0) or 0)
            months = o.get("months_ahead", 1)
            total_amount += order_amount * months
        if total_amount <= 0:
            raise HTTPException(status_code=400, detail="Unable to determine payment amount. Please ensure services have pricing configured.")

        # Store payment_reference on all orders
        for o in orders:
            await db.orders.update_one(
                {"id": o["id"]},
                {"$set": {"payment_reference": reference}}
            )

        http_client = await get_korapay_client()
        response = await http_client.post(
            "/charges/initialize",
            headers={
                "Authorization": f"Bearer {settings.KORAPAY_SECRET_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "amount": total_amount,
                "currency": "NGN",
                "reference": reference,
                "redirect_url": payment_data.callback_url,
                "customer": {
                    "email": current_user.email,
                    "name": current_user.full_name or current_user.email,
                },
                "metadata": {
                    "bulk-id": payment_data.bulk_id,
                    "user-id": current_user.id,
                    "type": "order-payment",
                }
            }
        )
        result = response.json()

        if result.get("status"):
            payment_doc = {
                "id": str(uuid.uuid4()),
                "order_id": None,
                "bulk_id": payment_data.bulk_id,
                "user_id": current_user.id,
                "amount": total_amount,
                "reference": reference,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "paid_at": None
            }
            await db.payments.insert_one(payment_doc)

            return {
                "checkout_url": result["data"]["checkout_url"],
                "reference": result["data"]["reference"]
            }

        logger.warning("Korapay bulk payment init failed: %s", result)
        raise HTTPException(status_code=400, detail=result.get("message", "Payment initialization failed"))

    # Single order payment
    if not payment_data.order_id:
        raise HTTPException(status_code=400, detail="Either order_id or bulk_id is required")

    order = await db.orders.find_one({"id": payment_data.order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    amount = payment_data.amount
    if not amount:
        service = await db.services.find_one({"id": order["service_id"]})
        if service and service.get("pricing_tiers"):
            amount = float(service["pricing_tiers"][0].get("price", 0))
        if not amount or amount <= 0:
            raise HTTPException(status_code=400, detail="Unable to determine payment amount. Please provide an amount or ensure the service has pricing configured.")

    # Store payment reference on order
    await db.orders.update_one(
        {"id": order["id"]},
        {"$set": {"payment_reference": reference}}
    )

    http_client = await get_korapay_client()
    response = await http_client.post(
        "/charges/initialize",
        headers={
            "Authorization": f"Bearer {settings.KORAPAY_SECRET_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "amount": amount,
            "currency": "NGN",
            "reference": reference,
            "redirect_url": payment_data.callback_url,
            "customer": {
                "email": current_user.email,
                "name": current_user.full_name or current_user.email,
            },
            "metadata": {
                "order-id": payment_data.order_id,
                "user-id": current_user.id,
                "type": "order-payment",
            }
        }
    )
    result = response.json()

    if result.get("status"):
        payment_doc = {
            "id": str(uuid.uuid4()),
            "order_id": payment_data.order_id,
            "user_id": current_user.id,
            "amount": amount,
            "reference": reference,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "paid_at": None
        }
        await db.payments.insert_one(payment_doc)

        return {
            "checkout_url": result["data"]["checkout_url"],
            "reference": result["data"]["reference"]
        }

    logger.warning("Korapay payment init failed: %s", result)
    raise HTTPException(status_code=400, detail=result.get("message", "Payment initialization failed"))

@api_router.get("/payments/verify/{reference}")
async def verify_payment(
    reference: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    http_client = await get_korapay_client()
    response = await http_client.get(
        f"/charges/{reference}",
        headers={"Authorization": f"Bearer {settings.KORAPAY_SECRET_KEY}"}
    )
    result = response.json()
    
    if result.get("status") and result["data"]["status"] == "success":
        # Update payment status
        await db.payments.update_one(
            {"reference": reference},
            {"$set": {
                "status": "success",
                "paid_at": datetime.now(timezone.utc).isoformat(),
                "payment_method": result["data"].get("payment_method")
            }}
        )
        
        # Activate all unpaid orders linked to this payment
        await activate_orders_on_payment(reference, db)

        # Gather billing period info for response
        activated_orders = await db.orders.find(
            {"payment_reference": reference},
            {"_id": 0, "billing_period_start": 1, "billing_period_end": 1, "months_ahead": 1}
        ).to_list(100)
        billing_periods = [
            {
                "start": o.get("billing_period_start"),
                "end": o.get("billing_period_end"),
                "months": o.get("months_ahead", 1),
            }
            for o in activated_orders if o.get("billing_period_start")
        ]

        return {
            "status": "success",
            "data": result["data"],
            "activated_orders": len(activated_orders),
            "billing_periods": billing_periods,
        }
    
    # Update payment status to failed if not successful
    await db.payments.update_one(
        {"reference": reference, "status": "pending"},
        {"$set": {"status": "failed"}}
    )
    return {"status": "failed", "message": "Payment verification failed"}

@api_router.get("/payments", response_model=None)
async def list_payments(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
):
    if current_user.role == UserRole.CLIENT:
        query = {"user_id": current_user.id}
    else:
        query = {}
    payments, _ = await paginated_query(db.payments, query, "created_at", page, limit)
    return payments

# ──────────────────────────────────────────────
# ADMIN PAYMENT DASHBOARD ENDPOINTS
# ──────────────────────────────────────────────

@api_router.get("/admin/payments", response_model=None)
async def admin_list_payments(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    if current_user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    query = {}
    if status:
        query["status"] = status
    if search:
        query["$or"] = [
            {"reference": {"$regex": search, "$options": "i"}},
            {"order_id": {"$regex": search, "$options": "i"}},
            {"user_id": {"$regex": search, "$options": "i"}},
        ]
    if date_from:
        query.setdefault("created_at", {})["$gte"] = date_from
    if date_to:
        end = datetime.fromisoformat(date_to.replace("Z", "+00:00")) + timedelta(days=1)
        query.setdefault("created_at", {})["$lte"] = end.isoformat()

    payments, total = await paginated_query(db.payments, query, "created_at", page, limit)

    # Enrich with user info and service titles
    enriched = []
    for p in payments:
        user = await db.users.find_one({"id": p.get("user_id")}, {"_id": 0, "full_name": 1, "email": 1, "company_name": 1})
        p["client_name"] = user.get("full_name") if user else None
        p["client_email"] = user.get("email") if user else None
        p["client_company"] = user.get("company_name") if user else None
        # Get associated order info
        if p.get("order_id"):
            order = await db.orders.find_one({"id": p["order_id"]}, {"_id": 0, "service_id": 1, "bulk_id": 1})
            if order:
                svc = await db.services.find_one({"id": order.get("service_id")}, {"_id": 0, "title": 1})
                p["service_title"] = svc.get("title") if svc else None
                p["bulk_id"] = order.get("bulk_id")
        enriched.append(p)

    return {"payments": enriched, "total": total, "page": page, "limit": limit}


@api_router.get("/admin/payments/stats", response_model=None)
async def admin_payment_stats(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    if current_user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = {}
    if date_from:
        query.setdefault("created_at", {})["$gte"] = date_from
    if date_to:
        end = datetime.fromisoformat(date_to.replace("Z", "+00:00")) + timedelta(days=1)
        query.setdefault("created_at", {})["$lte"] = end.isoformat()

    all_payments = await db.payments.find(query, {"_id": 0}).to_list(10000)
    successful = [p for p in all_payments if p.get("status") == "success"]
    failed = [p for p in all_payments if p.get("status") == "failed"]
    pending = [p for p in all_payments if p.get("status") == "pending"]

    total_revenue = sum(p.get("amount", 0) for p in successful)

    # Refund stats
    refund_query = {}
    if date_from:
        refund_query.setdefault("created_at", {})["$gte"] = date_from
    if date_to:
        refund_end = datetime.fromisoformat(date_to.replace("Z", "+00:00")) + timedelta(days=1)
        refund_query.setdefault("created_at", {})["$lte"] = refund_end.isoformat()

    all_refunds = await db.refunds.find(refund_query, {"_id": 0}).to_list(10000)
    successful_refunds = [r for r in all_refunds if r.get("status") == "success"]
    total_refunded = sum(r.get("amount", 0) for r in successful_refunds)

    # Monthly revenue (last 12 months)
    now = datetime.now(timezone.utc)
    monthly_revenue = []
    monthly_labels = []
    for i in range(11, -1, -1):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = (now - timedelta(days=30 * (i - 1))).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            month_end = now
        month_amount = sum(
            p.get("amount", 0) for p in successful
            if p.get("paid_at") and
            month_start.isoformat() <= p["paid_at"] <= month_end.isoformat()
        )
        monthly_revenue.append(round(month_amount, 2))
        monthly_labels.append(month_start.strftime("%b %Y"))

    # Payment methods breakdown
    method_counter = Counter(p.get("payment_method", "Unknown") for p in successful)
    payment_methods = [{"method": m, "count": c} for m, c in method_counter.most_common()]

    return {
        "total_revenue": round(total_revenue, 2),
        "total_refunded": round(total_refunded, 2),
        "net_revenue": round(total_revenue - total_refunded, 2),
        "total_transactions": len(all_payments),
        "successful_payments": len(successful),
        "failed_payments": len(failed),
        "pending_payments": len(pending),
        "total_refunds": len(all_refunds),
        "monthly_revenue": monthly_revenue,
        "monthly_labels": monthly_labels,
        "payment_methods": payment_methods,
    }


@api_router.get("/admin/payments/{payment_id}", response_model=None)
async def admin_get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    payment = await db.payments.find_one({"id": payment_id}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    # Enrich
    user = await db.users.find_one({"id": payment.get("user_id")}, {"_id": 0, "full_name": 1, "email": 1, "company_name": 1})
    payment["client_name"] = user.get("full_name") if user else None
    payment["client_email"] = user.get("email") if user else None
    payment["client_company"] = user.get("company_name") if user else None
    if payment.get("order_id"):
        order = await db.orders.find_one({"id": payment["order_id"]}, {"_id": 0, "service_id": 1})
        if order:
            svc = await db.services.find_one({"id": order.get("service_id")}, {"_id": 0, "title": 1})
            payment["service_title"] = svc.get("title") if svc else None
    # Get refunds for this payment
    refunds = await db.refunds.find({"payment_reference": payment.get("reference")}, {"_id": 0}).to_list(100)
    payment["refunds"] = refunds
    return payment


@api_router.post("/admin/payments/refund", response_model=None)
async def admin_initiate_refund(
    refund_data: RefundInitiate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Find the original payment
    payment = await db.payments.find_one({"reference": refund_data.payment_reference})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.get("status") != "success":
        raise HTTPException(status_code=400, detail="Can only refund successful payments")

    # Calculate already refunded amount
    existing_refunds = await db.refunds.find(
        {"payment_reference": refund_data.payment_reference, "status": {"$in": ["success", "processing"]}}
    ).to_list(100)
    already_refunded = sum(r.get("amount", 0) for r in existing_refunds)
    original_amount = payment.get("amount", 0)

    refund_amount = refund_data.amount or (original_amount - already_refunded)
    if refund_amount <= 0:
        raise HTTPException(status_code=400, detail="Nothing left to refund")
    if refund_amount > (original_amount - already_refunded):
        raise HTTPException(status_code=400, detail=f"Refund amount exceeds available balance of ₦{original_amount - already_refunded:,.2f}")

    # Generate unique refund reference
    refund_ref = f"tbr_ref_{uuid.uuid4().hex[:12]}"

    # Call Korapay refund API
    http_client = await get_korapay_client()
    response = await http_client.post(
        "/refunds/initiate",
        headers={
            "Authorization": f"Bearer {settings.KORAPAY_SECRET_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "payment_reference": refund_data.payment_reference,
            "reference": refund_ref,
            "amount": refund_amount,
            "reason": refund_data.reason or "Admin initiated refund",
            "webhook_url": f"{settings.CORS_ORIGINS.split(',')[0] if settings.CORS_ORIGINS else 'http://localhost:3000'}/api/payments/refund-webhook",
        }
    )
    result = response.json()

    if result.get("status"):
        # Store refund record
        refund_doc = {
            "id": f"ref_{uuid.uuid4().hex[:16]}",
            "payment_id": payment["id"],
            "payment_reference": refund_data.payment_reference,
            "refund_reference": refund_ref,
            "amount": refund_amount,
            "reason": refund_data.reason,
            "status": "processing",
            "initiated_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.refunds.insert_one(refund_doc)
        logger.info("Refund initiated: %s for payment %s, amount ₦%.2f", refund_ref, refund_data.payment_reference, refund_amount)
        return {"status": "success", "refund_reference": refund_ref, "amount": refund_amount}
    else:
        logger.warning("Korapay refund failed: %s", result)
        raise HTTPException(status_code=400, detail=result.get("message", "Refund initiation failed"))


@api_router.get("/admin/payments/export/csv")
async def admin_export_payments_csv(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    if current_user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = {}
    if status:
        query["status"] = status
    if date_from:
        query.setdefault("created_at", {})["$gte"] = date_from
    if date_to:
        end = datetime.fromisoformat(date_to.replace("Z", "+00:00")) + timedelta(days=1)
        query.setdefault("created_at", {})["$lte"] = end.isoformat()

    payments = await db.payments.find(query, {"_id": 0}).sort("created_at", -1).to_list(10000)

    # Build CSV
    headers = ["Reference", "Client", "Company", "Amount (NGN)", "Status", "Payment Method", "Order ID", "Created At", "Paid At"]
    rows = []
    for p in payments:
        user = await db.users.find_one({"id": p.get("user_id")}, {"_id": 0, "full_name": 1, "company_name": 1})
        rows.append([
            p.get("reference", ""),
            user.get("full_name", "") if user else "",
            user.get("company_name", "") if user else "",
            f"{p.get('amount', 0):.2f}",
            p.get("status", ""),
            p.get("payment_method", ""),
            p.get("order_id", ""),
            p.get("created_at", ""),
            p.get("paid_at", ""),
        ])

    csv_content = ",".join(headers) + "\n" + "\n".join(",".join(str(cell) for cell in row) for row in rows)
    filename = f"payments-export-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@api_router.get("/admin/refunds", response_model=None)
async def admin_list_refunds(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 50,
):
    if current_user.role == UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    refunds, total = await paginated_query(db.refunds, {}, "created_at", page, limit)
    return {"refunds": refunds, "total": total}


@api_router.post("/payments/refund-webhook")
async def korapay_refund_webhook(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    raw_body = await request.body()
    body = json.loads(raw_body)
    event_type = body.get("event")
    data = body.get("data", {})

    refund_reference = data.get("refund_reference") or data.get("reference")
    if not refund_reference:
        return {"status": "ignored"}

    # Update refund status based on event
    new_status = "processing"
    if event_type == "refund.success":
        new_status = "success"
    elif event_type == "refund.failed":
        new_status = "failed"

    now = datetime.now(timezone.utc).isoformat()
    update_fields = {"status": new_status}
    if new_status == "success":
        update_fields["completed_at"] = now

    result = await db.refunds.update_one(
        {"refund_reference": refund_reference},
        {"$set": update_fields}
    )
    if result.modified_count:
        logger.info("Refund %s updated to %s", refund_reference, new_status)

    return {"status": "ok"}


# CONTACT FORM ENDPOINT
CONTACT_RECIPIENTS = ["admin@tbrsolutions.ng", "info.tbr@dateheight.com", "support@tbrsolutions.ng"]

class ContactForm(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    subject: str
    message: str

@api_router.post("/contact")
async def submit_contact_form(form: ContactForm):
    from services.email_service import send_support_email, send_email, build_contact_form_html, build_contact_confirmation_html

    html_body = build_contact_form_html(
        name=form.name,
        email=form.email,
        phone=form.phone or "",
        subject=form.subject,
        message=form.message,
    )

    email_subject = f"Contact Form: {form.subject}"

    for recipient in CONTACT_RECIPIENTS:
        try:
            await send_support_email(recipient, email_subject, html_body)
            logger.info("Contact notification email sent to %s", recipient)
        except Exception as e:
            logger.error("Contact notification email failed for %s: %s", recipient, e)

    confirmation_html = build_contact_confirmation_html(name=form.name, subject=form.subject)
    confirmation_subject = "We've received your message — TBR Solutions"
    try:
        await send_support_email(form.email, confirmation_subject, confirmation_html)
        logger.info("Contact confirmation email sent to %s", form.email)
    except Exception as e:
        logger.warning("Contact confirmation via support sender failed for %s (%s); trying primary sender", form.email, e)
        try:
            await send_email(form.email, confirmation_subject, confirmation_html)
            logger.info("Contact confirmation email sent to %s via primary sender", form.email)
        except Exception as e2:
            logger.error("Contact confirmation email could not be sent to %s: %s", form.email, e2)

    logger.info("Contact form submitted by %s <%s>: %s", form.name, form.email, form.subject)
    return {"status": "success", "message": "Your message has been sent. We will get back to you shortly."}


# KORAPAY WEBHOOK
@api_router.post("/payments/webhook")
async def korapay_webhook(request: Request, db: AsyncIOMotorDatabase = Depends(get_db)):
    raw_body = await request.body()
    body = json.loads(raw_body)
    event_type = body.get("event")
    data = body.get("data", {})

    # Verify webhook signature — Korapay signs JSON.stringify(data) with secret key
    signature = request.headers.get("x-korapay-signature", "")
    expected_sig = hmac.new(
        settings.KORAPAY_SECRET_KEY.encode(),
        json.dumps(data, separators=(",", ":")).encode(),
        hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_sig):
        logger.warning("Webhook signature mismatch for reference=%s", data.get("reference"))
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    reference = data.get("reference")
    if not reference or event_type not in ("charge.success", "charge.failed"):
        return {"status": "ignored"}

    is_wallet = reference.startswith("tbr_wallet_")

    if is_wallet:
        # Atomic: mark pending → completed in one operation (prevents double-credit)
        tx = await db.wallet_transactions.find_one_and_update(
            {"reference": reference, "status": "pending"},
            {"$set": {"status": "completed"}},
        )
        if not tx:
            return {"status": "ignored"}

        if event_type == "charge.success":
            now = datetime.now(timezone.utc).isoformat()
            amount = float(data.get("amount", 0))

            await db.wallets.update_one(
                {"id": tx["wallet_id"]},
                {"$inc": {"balance": amount}, "$set": {"updated_at": now}}
            )
            wallet = await db.wallets.find_one({"id": tx["wallet_id"]}, {"_id": 0})
            new_balance = wallet["balance"] if wallet else 0

            await db.wallet_transactions.update_one(
                {"reference": reference},
                {"$set": {"balance_after": new_balance, "amount": amount}}
            )
        else:
            # charge.failed — revert status back to failed
            await db.wallet_transactions.update_one(
                {"reference": reference},
                {"$set": {"status": "failed"}}
            )
    else:
        # Order payment — idempotent
        payment = await db.payments.find_one({"reference": reference})
        if not payment or payment["status"] == "success":
            return {"status": "ignored"}

        if event_type == "charge.success":
            await db.payments.update_one(
                {"reference": reference},
                {"$set": {
                    "status": "success",
                    "paid_at": datetime.now(timezone.utc).isoformat(),
                    "payment_method": data.get("payment_method")
                }}
            )
            # Activate all unpaid orders linked to this payment
            await activate_orders_on_payment(reference, db)
        else:
            await db.payments.update_one(
                {"reference": reference},
                {"$set": {"status": "failed"}}
            )

    return {"status": "received"}

# WALLET ROUTES
@api_router.get("/wallet")
async def get_wallet(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    wallet = await db.wallets.find_one({"user_id": current_user.id}, {"_id": 0})
    if not wallet:
        now = datetime.now(timezone.utc).isoformat()
        wallet = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "balance": 0.0,
            "currency": "NGN",
            "created_at": now,
            "updated_at": now,
        }
        await db.wallets.insert_one(wallet)
    
    # Aggregation for stats — single query instead of loading all transactions
    stats_pipeline = [
        {"$match": {"user_id": current_user.id, "status": "completed"}},
        {"$group": {
            "_id": "$type",
            "total": {"$sum": "$amount"},
        }},
    ]
    stats_result = await db.wallet_transactions.aggregate(stats_pipeline).to_list(10)
    total_funded = 0.0
    total_spent = 0.0
    for s in stats_result:
        if s["_id"] in ("credit", "transfer_in"):
            total_funded += s["total"]
        elif s["_id"] in ("debit", "transfer_out"):
            total_spent += s["total"]
    
    # Recent transactions (limit 5)
    recent = await db.wallet_transactions.find(
        {"user_id": current_user.id}, {"_id": 0}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "wallet": wallet,
        "stats": {
            "total_funded": total_funded,
            "total_spent": total_spent,
        },
        "recent_transactions": recent,
    }

@api_router.post("/wallet/fund")
async def fund_wallet(
    fund_data: WalletFundRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    wallet = await db.wallets.find_one({"user_id": current_user.id}, {"_id": 0})
    if not wallet:
        now = datetime.now(timezone.utc).isoformat()
        wallet = {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "balance": 0.0,
            "currency": "NGN",
            "created_at": now,
            "updated_at": now,
        }
        await db.wallets.insert_one(wallet)
    
    # Reject if user already has a recent pending fund transaction (double-click protection)
    # Auto-expire stale pending transactions older than 10 minutes
    stale_cutoff = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    await db.wallet_transactions.update_many(
        {"wallet_id": wallet["id"], "type": "credit", "status": "pending", "created_at": {"$lt": stale_cutoff}},
        {"$set": {"status": "expired"}}
    )
    pending_tx = await db.wallet_transactions.find_one({
        "wallet_id": wallet["id"],
        "type": "credit",
        "status": "pending",
    })
    if pending_tx:
        raise HTTPException(status_code=429, detail="A funding transaction is already in progress. Please complete or wait for it to expire.")
    
    reference = f"tbr_wallet_{uuid.uuid4().hex[:16]}"
    now = datetime.now(timezone.utc).isoformat()
    
    # Create pending transaction — balance_after set to 0 (updated on success)
    tx_doc = {
        "id": str(uuid.uuid4()),
        "wallet_id": wallet["id"],
        "user_id": current_user.id,
        "type": "credit",
        "amount": fund_data.amount,
        "balance_after": 0,
        "reference": reference,
        "description": f"Wallet funding via Korapay (₦{fund_data.amount:,.2f})",
        "status": "pending",
        "created_at": now,
    }
    await db.wallet_transactions.insert_one(tx_doc)
    
    http_client = await get_korapay_client()
    response = await http_client.post(
        "/charges/initialize",
        headers={
            "Authorization": f"Bearer {settings.KORAPAY_SECRET_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "amount": int(fund_data.amount),
            "currency": "NGN",
            "reference": reference,
            "redirect_url": f"{settings.CORS_ORIGINS.split(',')[0]}/portal/wallet",
            "customer": {
                "email": current_user.email,
                "name": current_user.full_name or current_user.email,
            },
            "metadata": {
                "wallet-id": wallet["id"],
                "user-id": current_user.id,
                "type": "wallet-fund",
            }
        }
    )
    result = response.json()
    
    if result.get("status"):
        return {
            "checkout_url": result["data"]["checkout_url"],
            "reference": result["data"]["reference"]
        }
    
    await db.wallet_transactions.update_one(
        {"reference": reference},
        {"$set": {"status": "failed"}}
    )
    logger.warning("Korapay wallet fund init failed: %s", result)
    raise HTTPException(status_code=400, detail=result.get("message", "Wallet funding failed"))

@api_router.get("/wallet/fund/verify/{reference}")
async def verify_wallet_fund(
    reference: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    http_client = await get_korapay_client()
    response = await http_client.get(
        f"/charges/{reference}",
        headers={"Authorization": f"Bearer {settings.KORAPAY_SECRET_KEY}"}
    )
    result = response.json()
    
    if result.get("status") and result["data"]["status"] == "success":
        # Atomically mark transaction as completed — prevents double-credit from concurrent webhook
        tx = await db.wallet_transactions.find_one_and_update(
            {"reference": reference, "status": "pending"},
            {"$set": {"status": "completed"}},
        )
        if tx:
            amount = float(result["data"].get("amount", 0))
            now = datetime.now(timezone.utc).isoformat()
            
            await db.wallets.update_one(
                {"id": tx["wallet_id"]},
                {"$inc": {"balance": amount}, "$set": {"updated_at": now}}
            )
            wallet = await db.wallets.find_one({"id": tx["wallet_id"]}, {"_id": 0})
            new_balance = wallet["balance"] if wallet else 0
            
            await db.wallet_transactions.update_one(
                {"reference": reference},
                {"$set": {"balance_after": new_balance, "amount": amount}}
            )
        
        return {"status": "success", "data": result["data"]}
    
    return {"status": "failed", "message": "Verification failed"}

@api_router.post("/wallet/pay")
async def pay_from_wallet(
    pay_data: WalletPayRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    wallet = await db.wallets.find_one({"user_id": current_user.id}, {"_id": 0})
    if not wallet:
        raise HTTPException(status_code=400, detail="Wallet not found")
    
    order = await db.orders.find_one({"id": pay_data.order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == UserRole.CLIENT and order["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Atomic balance deduction — prevents double-spend race conditions
    now = datetime.now(timezone.utc).isoformat()
    result = await db.wallets.update_one(
        {"id": wallet["id"], "balance": {"$gte": pay_data.amount}},
        {"$inc": {"balance": -pay_data.amount}, "$set": {"updated_at": now}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    
    new_balance = wallet["balance"] - pay_data.amount
    
    tx_doc = {
        "id": str(uuid.uuid4()),
        "wallet_id": wallet["id"],
        "user_id": current_user.id,
        "type": "debit",
        "amount": pay_data.amount,
        "balance_after": new_balance,
        "reference": f"tbr_wallet_pay_{uuid.uuid4().hex[:12]}",
        "description": f"Payment for order {pay_data.order_id[:8]}",
        "status": "completed",
        "related_order_id": pay_data.order_id,
        "created_at": now,
    }
    await db.wallet_transactions.insert_one(tx_doc)
    
    payment_doc = {
        "id": str(uuid.uuid4()),
        "order_id": pay_data.order_id,
        "user_id": current_user.id,
        "amount": pay_data.amount,
        "reference": tx_doc["reference"],
        "status": "success",
        "payment_method": "wallet",
        "created_at": now,
        "paid_at": now,
    }
    await db.payments.insert_one(payment_doc)
    
    await db.orders.update_one(
        {"id": pay_data.order_id},
        {"$set": {"status": OrderStatus.IN_PROGRESS}}
    )
    
    return {"status": "success", "balance": new_balance, "payment_reference": tx_doc["reference"]}

@api_router.post("/wallet/transfer")
async def transfer_from_wallet(
    transfer_data: WalletTransferRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if transfer_data.recipient_email == current_user.email:
        raise HTTPException(status_code=400, detail="Cannot transfer to yourself")
    
    sender_wallet = await db.wallets.find_one({"user_id": current_user.id}, {"_id": 0})
    if not sender_wallet:
        raise HTTPException(status_code=400, detail="Wallet not found")
    
    recipient = await db.users.find_one({"email": transfer_data.recipient_email}, {"_id": 0})
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Atomic sender deduction — prevents double-spend
    now = datetime.now(timezone.utc).isoformat()
    result = await db.wallets.update_one(
        {"id": sender_wallet["id"], "balance": {"$gte": transfer_data.amount}},
        {"$inc": {"balance": -transfer_data.amount}, "$set": {"updated_at": now}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    
    sender_new = sender_wallet["balance"] - transfer_data.amount
    
    # Get or create recipient wallet
    recipient_wallet = await db.wallets.find_one({"user_id": recipient["id"]}, {"_id": 0})
    if not recipient_wallet:
        recipient_wallet = {
            "id": str(uuid.uuid4()),
            "user_id": recipient["id"],
            "balance": 0.0,
            "currency": "NGN",
            "created_at": now,
            "updated_at": now,
        }
        await db.wallets.insert_one(recipient_wallet)
    
    recipient_new = recipient_wallet["balance"] + transfer_data.amount
    await db.wallets.update_one(
        {"id": recipient_wallet["id"]},
        {"$inc": {"balance": transfer_data.amount}, "$set": {"updated_at": now}}
    )
    
    ref = f"tbr_transfer_{uuid.uuid4().hex[:12]}"
    desc = transfer_data.description or f"Transfer to {recipient.get('full_name') or recipient['email']}"
    
    # Sender transaction
    await db.wallet_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "wallet_id": sender_wallet["id"],
        "user_id": current_user.id,
        "type": "transfer_out",
        "amount": transfer_data.amount,
        "balance_after": sender_new,
        "reference": ref,
        "description": desc,
        "status": "completed",
        "related_user_id": recipient["id"],
        "created_at": now,
    })
    # Recipient transaction
    await db.wallet_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "wallet_id": recipient_wallet["id"],
        "user_id": recipient["id"],
        "type": "transfer_in",
        "amount": transfer_data.amount,
        "balance_after": recipient_new,
        "reference": ref,
        "description": f"Transfer from {current_user.full_name or current_user.email}",
        "status": "completed",
        "related_user_id": current_user.id,
        "created_at": now,
    })
    
    return {"status": "success", "balance": sender_new, "recipient": recipient["email"]}

@api_router.get("/wallet/transactions")
async def list_wallet_transactions(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    tx_type: Optional[str] = None,
):
    query: Dict[str, Any] = {"user_id": current_user.id}
    if tx_type:
        query["type"] = tx_type
    transactions, total = await paginated_query(db.wallet_transactions, query, "created_at", page, limit)
    return {"transactions": transactions, "total": total, "page": page, "limit": limit}

# RESOURCES/BLOG ROUTES
@api_router.get("/resources", response_model=List[Resource])
async def list_resources(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    cache_key = f"resources_{category or 'all'}_{search or ''}"
    if not search and cache_key in resources_cache:
        return resources_cache[cache_key]

    query = {}
    if category:
        query["category"] = category
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"excerpt": {"$regex": search, "$options": "i"}}
        ]
    
    resources = await db.resources.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    if not search:
        resources_cache[cache_key] = resources
    return resources

@api_router.get("/resources/{slug}", response_model=Resource)
async def get_resource(slug: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    resource = await db.resources.find_one({"slug": slug}, {"_id": 0})
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Increment views
    await db.resources.update_one({"slug": slug}, {"$inc": {"views": 1}})
    
    return resource

@api_router.post("/resources", response_model=Resource)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.OPERATIONS_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    resource_doc = resource_data.model_dump()
    resource_doc["id"] = str(uuid.uuid4())
    resource_doc["created_at"] = datetime.now(timezone.utc).isoformat()
    resource_doc["views"] = 0
    
    await db.resources.insert_one(resource_doc)
    return Resource(**{k: v for k, v in resource_doc.items() if k != "_id"})

# AI CHECKLIST ROUTE
@api_router.post("/ai/checklist", response_model=ChecklistResponse)
async def generate_checklist(
    request_data: ChecklistRequest,
    current_user: User = Depends(get_current_user_dep)
):
    openai_api_key = settings.OPENAI_API_KEY
    if openai_api_key:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=openai_api_key)
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert regulatory and compliance advisor for TBR Solutions. Generate detailed document checklists and recommendations for various business services in Nigeria. Always respond with valid JSON only."},
                    {"role": "user", "content": f"""Generate a comprehensive document checklist for the following service request:

Service Type: {request_data.service_type}
Company Type: {request_data.company_type or 'Not specified'}
Additional Context: {request_data.additional_context or 'None'}

Provide a JSON object with:
- "checklist": array of objects with keys "document", "description", "priority" ("required" or "optional"), "tips"
- "recommendations": array of strings"""}
                ],
                response_format={"type": "json_object"}
            )
            import json
            result = json.loads(response.choices[0].message.content)
            return ChecklistResponse(**result)
        except Exception:
            pass
    
    return ChecklistResponse(
        checklist=[
            {
                "document": "Certificate of Incorporation",
                "description": "Official company registration certificate",
                "priority": "required",
                "tips": "Ensure all names match exactly"
            }
        ],
        recommendations=["Ensure all documents are current and certified"]
    )

# DASHBOARD STATS
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    cache_key = f"dash_{current_user.id}"
    if cache_key in dashboard_cache:
        return dashboard_cache[cache_key]

    if current_user.role == UserRole.CLIENT:
        total_orders = await db.orders.count_documents({"user_id": current_user.id})
        pending_orders = await db.orders.count_documents({
            "user_id": current_user.id,
            "status": {"$in": [OrderStatus.PENDING_REVIEW, OrderStatus.DOCUMENTS_REQUIRED]}
        })
        completed_orders = await db.orders.count_documents({
            "user_id": current_user.id,
            "status": OrderStatus.COMPLETED
        })
        
        result = {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "completed_orders": completed_orders,
            "active_orders": total_orders - completed_orders
        }
    else:
        total_orders = await db.orders.count_documents({})
        pending_review = await db.orders.count_documents({"status": OrderStatus.PENDING_REVIEW})
        in_progress = await db.orders.count_documents({"status": OrderStatus.IN_PROGRESS})
        total_clients = await db.users.count_documents({"role": UserRole.CLIENT})
        
        result = {
            "total_orders": total_orders,
            "pending_review": pending_review,
            "in_progress": in_progress,
            "total_clients": total_clients
        }

    dashboard_cache[cache_key] = result
    return result

# NOTIFICATIONS
@api_router.get("/notifications", response_model=List[Notification])
async def list_notifications(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    limit: int = 50,
):
    notifications = await db.notifications.find(
        {"user_id": current_user.id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(min(limit, 100))
    return notifications

# TICKET ROUTES
@api_router.post("/tickets", response_model=Ticket)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    ticket_doc = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "subject": ticket_data.subject,
        "category": ticket_data.category,
        "priority": ticket_data.priority,
        "status": TicketStatus.OPEN,
        "description": ticket_data.description,
        "order_id": ticket_data.order_id,
        "assigned_to": None,
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
    }
    await db.tickets.insert_one(ticket_doc)

    # Notify all admins about the new ticket
    priority_value = ticket_data.priority.value if hasattr(ticket_data.priority, 'value') else str(ticket_data.priority)
    admin_users = await db.users.find(
        {"role": {"$in": ["super_admin", "operations_manager"]}, "is_active": True},
        {"_id": 0, "id": 1, "email": 1}
    ).to_list(100)

    for admin in admin_users:
        await send_notification(
            admin["id"],
            f"THERE IS A {priority_value.upper()} PROBLEM",
            f"New support ticket: {ticket_data.subject} (Priority: {priority_value.upper()})",
            db
        )

    # Send email notification to admins
    if admin_users:
        html = build_ticket_notification_html(
            priority_value,
            ticket_data.subject,
            current_user.full_name or current_user.email,
            ticket_data.description or "",
        )
        for admin in admin_users:
            if admin.get("email"):
                try:
                    await send_internal_email(
                        admin["email"],
                        f"THERE IS A {priority_value.upper()} PROBLEM — {ticket_data.subject}",
                        html
                    )
                except Exception as e:
                    logger.error("Failed to send ticket email to %s: %s", admin["email"], e)

    # Send confirmation email to client
    from services.email_service import send_support_email, build_ticket_opened_html
    client_email = current_user.email
    if client_email:
        try:
            confirmation_html = build_ticket_opened_html(
                client_name=current_user.full_name or "there",
                subject=ticket_data.subject,
                ticket_id=ticket_doc["id"],
                priority=priority_value,
            )
            await send_support_email(
                client_email,
                f"Your Support Ticket Has Been Opened — {ticket_data.subject}",
                confirmation_html,
            )
        except Exception as e:
            logger.error("Failed to send ticket confirmation to client %s: %s", client_email, e)

    return Ticket(**{k: v for k, v in ticket_doc.items() if k != "_id"})

@api_router.get("/tickets", response_model=List[Ticket])
async def list_tickets(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
):
    query = {}
    if current_user.role == UserRole.CLIENT:
        query["user_id"] = current_user.id
    tickets, _ = await paginated_query(db.tickets, query, "created_at", page, limit)
    return tickets

@api_router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == UserRole.CLIENT and ticket["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ticket

@api_router.patch("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(
    ticket_id: str,
    update_data: TicketUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    ticket = await db.tickets.find_one({"id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == UserRole.CLIENT and ticket["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    update_dict["updated_at"] = datetime.now(timezone.utc).isoformat()
    if update_dict.get("status") == TicketStatus.RESOLVED:
        update_dict["resolved_at"] = datetime.now(timezone.utc).isoformat()

    await db.tickets.update_one({"id": ticket_id}, {"$set": update_dict})
    updated = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    return Ticket(**updated)

@api_router.post("/tickets/{ticket_id}/messages", response_model=Ticket)
async def add_ticket_message(
    ticket_id: str,
    message_data: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    ticket = await db.tickets.find_one({"id": ticket_id})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user.role == UserRole.CLIENT and ticket["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    message = message_data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    attachments = message_data.get("attachments", [])

    msg = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "user_name": current_user.full_name,
        "message": message,
        "attachments": attachments,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.tickets.update_one(
        {"id": ticket_id},
        {
            "$push": {"messages": msg},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    updated = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    return Ticket(**updated)

# FILE UPLOADS
@api_router.post("/upload/service-doc")
async def upload_service_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dep),
):
    await validate_file_extension(file)
    if current_user.role in ADMIN_ROLES:
        check_permission(current_user, PERMISSION_UPLOAD)
    SERVICE_DOC_DIR = UPLOAD_DIR / 'service-docs'
    SERVICE_DOC_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = SERVICE_DOC_DIR / unique_name
    content = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    url = f"/uploads/service-docs/{unique_name}"
    return {"url": url, "filename": file.filename, "size": len(content)}

@api_router.post("/upload/ticket")
async def upload_ticket_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dep),
):
    await validate_file_extension(file)
    
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = TICKET_UPLOAD_DIR / unique_name
    
    content = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    url = f"/uploads/tickets/{unique_name}"
    return {"url": url, "filename": file.filename, "size": len(content)}

@api_router.get("/files/download")
async def download_file(
    path: str,
    name: str = "download",
    current_user: User = Depends(get_current_user_dep),
):
    allowed_prefixes = ["uploads/orders/", "uploads/service-docs/", "uploads/tickets/"]
    if not any(path.startswith(p) for p in allowed_prefixes):
        raise HTTPException(status_code=400, detail="Invalid file path")
    full_path = ROOT_DIR / path
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(full_path),
        filename=name,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{name}"'}
    )

# ADMIN ROUTES
ADMIN_ROLES = ["super_admin", "operations_manager", "compliance_officer", "tax_officer", "legal_officer", "finance_officer"]

@api_router.get("/admin/stats", response_model=None)
async def get_admin_stats(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    is_super = current_user.role == UserRole.SUPER_ADMIN
    scope = {} if is_super else {"assigned_to": current_user.id}

    # Always exclude unpaid orders from admin stats
    paid_scope = {**scope, "status": {"$ne": OrderStatus.UNPAID}}

    if is_super and "admin_stats" in admin_stats_cache:
        return admin_stats_cache["admin_stats"]

    total_orders = await db.orders.count_documents(paid_scope)
    pending_review = await db.orders.count_documents({**paid_scope, "status": OrderStatus.PENDING_REVIEW})
    in_progress = await db.orders.count_documents({**paid_scope, "status": OrderStatus.IN_PROGRESS})
    completed = await db.orders.count_documents({**paid_scope, "status": OrderStatus.COMPLETED})
    cancelled = await db.orders.count_documents({**paid_scope, "status": OrderStatus.CANCELLED})
    total_clients = await db.users.count_documents({"role": UserRole.CLIENT})
    open_tickets = await db.tickets.count_documents({"status": {"$in": [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_ON_CLIENT]}})
    unassigned_orders = await db.orders.count_documents({**paid_scope, "assigned_to": None}) if is_super else 0

    # Completion rate (completed / non-cancelled)
    non_cancelled = total_orders - cancelled
    completion_rate = round(completed / non_cancelled * 100, 1) if non_cancelled > 0 else 0.0

    # Completed tasks grouped by admin (super admin only)
    completion_by_admin = []
    if is_super:
        pipeline = [
            {"$match": {"status": OrderStatus.COMPLETED}},
            {"$group": {"_id": "$assigned_to", "count": {"$sum": 1}}},
            {"$match": {"_id": {"$ne": None}}},
        ]
        async for doc in db.orders.aggregate(pipeline):
            assignee_id = doc["_id"]
            assignee = await db.users.find_one({"id": assignee_id}, {"_id": 0, "full_name": 1})
            name = assignee.get("full_name", assignee_id[:8]) if assignee else assignee_id[:8]
            completion_by_admin.append({"name": name, "completed": doc["count"]})
        completion_by_admin.sort(key=lambda x: x["completed"], reverse=True)
    
    # Monthly order counts for chart (last 6 months)
    now = datetime.now(timezone.utc)
    monthly_labels = []
    monthly_counts = []
    for i in range(5, -1, -1):
        month_start = now.replace(day=1) - timedelta(days=30 * i)
        month_start = month_start.replace(hour=0, minute=0, second=0, microsecond=0)
        if i > 0:
            month_end = now.replace(day=1) - timedelta(days=30 * (i - 1))
        else:
            month_end = now
        label = month_start.strftime("%b")
        q = {**paid_scope, "created_at": {"$gte": month_start.isoformat(), "$lt": month_end.isoformat()}}
        count = await db.orders.count_documents(q)
        monthly_labels.append(label)
        monthly_counts.append(count)
    
    result = {
        "total_orders": total_orders,
        "pending_review": pending_review,
        "in_progress": in_progress,
        "completed": completed,
        "cancelled": cancelled,
        "completion_rate": completion_rate,
        "completion_by_admin": completion_by_admin,
        "total_clients": total_clients,
        "open_tickets": open_tickets,
        "unassigned_orders": unassigned_orders,
        "monthly_labels": monthly_labels,
        "monthly_counts": monthly_counts,
    }
    admin_stats_cache["admin_stats"] = result
    return result

@api_router.get("/admin/deadlines", response_model=None)
async def get_upcoming_deadlines(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    days: int = 7,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    now = datetime.now(timezone.utc)
    scope = {} if current_user.role == UserRole.SUPER_ADMIN else {"assigned_to": current_user.id}
    threshold = (now + timedelta(days=days)).isoformat()

    orders = await db.orders.find({
        **scope,
        "deadline": {"$ne": None, "$lte": threshold},
        "status": {"$nin": [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.UNPAID]},
    }, {"_id": 0, "hashed_password": 0}).to_list(50)

    result = []
    for o in orders:
        try:
            deadline = datetime.fromisoformat(o["deadline"])
            remaining = (deadline - now).total_seconds() / 86400
            o["time_remaining_days"] = round(remaining, 1)
        except Exception:
            o["time_remaining_days"] = None
        svc = await db.services.find_one({"id": o.get("service_id")}, {"_id": 0, "title": 1})
        o["service_title"] = svc.get("title", "") if svc else ""
        result.append(o)
    return {"deadlines": result}

@api_router.get("/admin/tickets", response_model=None)
async def list_admin_tickets(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    mine: bool = True,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {}
    if mine or current_user.role != UserRole.SUPER_ADMIN:
        query["assigned_to"] = current_user.id
    tickets, total = await paginated_query(db.tickets, query, "updated_at", page, limit)
    enriched = []
    for t in tickets:
        enriched.append(await enrich_ticket(t, db))
    return {"tickets": enriched, "total": total, "page": page, "limit": limit}

def get_default_permissions(role: str) -> dict:
    from permissions import get_default_permissions as _get
    return _get(role)

# ── Permission Management Endpoints (Super Admin only) ──────────────────────

@api_router.get("/admin/permissions/schema")
async def get_permissions_schema(current_user: User = Depends(get_current_user_dep)):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can view permission schema")
    from permissions import get_permission_groups, PERMISSION_SCHEMA
    return {"schema": PERMISSION_SCHEMA, "groups": get_permission_groups()}

@api_router.get("/admin/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can view user permissions")
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "permissions": 1, "role": 1, "full_name": 1, "email": 1})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    from permissions import get_default_permissions as _get_defaults
    perms = user_doc.get("permissions") or _get_defaults(user_doc.get("role", "client"))
    return {
        "user_id": user_id,
        "full_name": user_doc.get("full_name"),
        "email": user_doc.get("email"),
        "role": user_doc.get("role"),
        "permissions": perms,
    }

@api_router.put("/admin/users/{user_id}/permissions")
async def set_user_permissions(
    user_id: str,
    body: PermissionUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can set user permissions")
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    if user_doc.get("role") == "super_admin":
        raise HTTPException(status_code=400, detail="Cannot modify super admin permissions")
    from permissions import get_modules_from_permissions
    visible_modules = get_modules_from_permissions(body.permissions)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"permissions": body.permissions, "visible_modules": visible_modules}},
    )
    return {"message": "Permissions updated", "permissions": body.permissions, "visible_modules": visible_modules}

@api_router.patch("/admin/users/{user_id}/permissions")
async def patch_user_permissions(
    user_id: str,
    body: PermissionUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can update user permissions")
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    if user_doc.get("role") == "super_admin":
        raise HTTPException(status_code=400, detail="Cannot modify super admin permissions")
    from permissions import get_modules_from_permissions
    current_perms = user_doc.get("permissions") or {}
    current_perms.update(body.permissions)
    visible_modules = get_modules_from_permissions(current_perms)
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"permissions": current_perms, "visible_modules": visible_modules}},
    )
    return {"message": "Permissions updated", "permissions": current_perms, "visible_modules": visible_modules}

@api_router.post("/admin/users", response_model=User)
async def create_admin_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can create admin users")

    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        if existing.get("role") == UserRole.CLIENT:
            raise HTTPException(status_code=400, detail="This email is already used by a client account")
        raise HTTPException(status_code=400, detail="This email is already used by an admin account")

    role_val = user_data.role.value if hasattr(user_data.role, 'value') else user_data.role
    if role_val == UserRole.SUPER_ADMIN:
        super_count = await db.users.count_documents({"role": UserRole.SUPER_ADMIN})
        if super_count >= 2:
            raise HTTPException(status_code=400, detail="Maximum of 2 super admins allowed")

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    now = datetime.now(timezone.utc).isoformat()
    permissions = get_default_permissions(user_data.role.value if hasattr(user_data.role, 'value') else user_data.role)
    visible_modules = get_default_visible_modules(user_data.role.value if hasattr(user_data.role, 'value') else user_data.role)

    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "company_name": user_data.company_name,
        "role": user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
        "hashed_password": hashed_password,
        "is_active": True,
        "email_verified": True,
        "created_at": now,
        "permissions": permissions,
        "visible_modules": visible_modules,
    }

    await db.users.insert_one(user_doc)
    user = User(**{k: v for k, v in user_doc.items() if k != "hashed_password"})
    return user

@api_router.patch("/admin/users/{user_id}", response_model=User)
async def update_admin_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can update users")

    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        try:
            from bson.objectid import ObjectId
            oid = ObjectId(user_id)
            user_doc = await db.users.find_one({"_id": oid})
            if user_doc and "id" not in user_doc:
                await db.users.update_one({"_id": oid}, {"$set": {"id": user_id}})
        except Exception:
            pass
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = {k: v for k, v in update_data.model_dump(exclude_none=True).items()}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")

    if password := update_dict.get("password"):
        update_dict["hashed_password"] = get_password_hash(password)
        del update_dict["password"]

    if "role" in update_dict:
        role_val = update_dict["role"].value if hasattr(update_dict["role"], 'value') else update_dict["role"]
        update_dict["role"] = role_val
        if role_val == UserRole.SUPER_ADMIN and user_doc.get("role") != UserRole.SUPER_ADMIN:
            super_count = await db.users.count_documents({"role": UserRole.SUPER_ADMIN})
            if super_count >= 2:
                raise HTTPException(status_code=400, detail="Maximum of 2 super admins allowed")

    match_id = user_doc.get("id") or str(user_doc["_id"])
    await db.users.update_one({"id": match_id}, {"$set": update_dict})
    updated = await db.users.find_one({"id": match_id}, {"_id": 0, "hashed_password": 0})
    return User(**updated)

@api_router.delete("/admin/users/{user_id}")
async def delete_admin_user(
    user_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can delete users")

    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    if user_doc.get("role") == UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="Cannot delete another super admin")

    await db.users.delete_one({"id": user_id})
    return {"message": "User deleted"}

@api_router.get("/admin/users", response_model=None)
async def list_staff_users(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 20,
):
    if current_user.role not in ["super_admin", "operations_manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    users, total = await paginated_query(
        db.users,
        {"role": {"$ne": UserRole.CLIENT}},
        None, page, limit,
        {"hashed_password": 0}
    )
    for u in users:
        if "id" not in u:
            uid = str(u["_id"])
            u["id"] = uid
            try:
                await db.users.update_one({"_id": u["_id"]}, {"$set": {"id": uid}})
            except Exception:
                pass
        u.pop("_id", None)
    return {"users": users, "total": total, "page": page, "limit": limit}


@api_router.get("/admin/clients", response_model=None)
async def list_clients(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    type: Optional[str] = None,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {"role": UserRole.CLIENT.value}
    if type in ("individual", "organization"):
        query["account_type"] = type
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"company_name": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]
    users, total = await paginated_query(
        db.users,
        query,
        "created_at", page, limit,
        {"hashed_password": 0}
    )
    for u in users:
        u.pop("_id", None)
        if "id" not in u:
            continue
        # Count active orders for each client
        order_count = await db.orders.count_documents({"user_id": u["id"], "status": {"$nin": ["cancelled", "completed"]}})
        total_orders = await db.orders.count_documents({"user_id": u["id"]})
        total_invoiced = await db.invoices.count_documents({"user_id": u["id"]})
        u["active_orders"] = order_count
        u["total_orders"] = total_orders
        u["total_invoices"] = total_invoiced
    return {"clients": users, "total": total, "page": page, "limit": limit}


# ─── ADMIN ORGANIZATION MANAGEMENT ─────────────────────────────────────

@api_router.get("/admin/orgs", response_model=None)
async def admin_list_orgs(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can manage organizations")
    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"company_name": {"$regex": search, "$options": "i"}},
            {"rc_number": {"$regex": search, "$options": "i"}},
        ]
    orgs, total = await paginated_query(db.organizations, query, "created_at", page, limit)
    for o in orgs:
        o.pop("_id", None)
        member_count = await db.users.count_documents({"org_id": o.get("id")})
        o["member_count"] = member_count
        head_user = await db.users.find_one({"org_id": o.get("id"), "org_role": "head_of_operations"}, {"_id": 0, "id": 1, "full_name": 1, "email": 1})
        o["head_of_operations"] = head_user
        created_by_user = await db.users.find_one({"id": o.get("created_by")}, {"_id": 0, "full_name": 1, "email": 1})
        o["created_by_name"] = created_by_user.get("full_name") if created_by_user else None
        pending_invites = await db.organization_invites.count_documents({"org_id": o.get("id"), "accepted_at": None})
        o["pending_invites"] = pending_invites
    return {"orgs": orgs, "total": total, "page": page, "limit": limit}


@api_router.post("/admin/orgs")
async def admin_create_org(
    data: OrgCreateRequest,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can create organizations")

    existing = await db.organizations.find_one({"name": data.name})
    if existing:
        raise HTTPException(status_code=409, detail="An organization with this name already exists.")

    org_id = str(uuid.uuid4())
    join_code = _generate_join_code()
    while await db.organizations.find_one({"join_code": join_code}):
        join_code = _generate_join_code()

    org_doc = {
        "id": org_id,
        "name": data.name,
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "join_code": join_code,
        "rc_number": data.rc_number,
        "company_name": data.company_name,
    }
    await db.organizations.insert_one(org_doc)
    return {"message": "Organization created successfully", "org_id": org_id, "join_code": join_code}


@api_router.get("/admin/orgs/{org_id}")
async def admin_get_org(
    org_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can manage organizations")
    org = await db.organizations.find_one({"id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    members = await db.users.find({"org_id": org_id}, {"_id": 0, "id": 1, "full_name": 1, "email": 1, "role": 1, "org_role": 1}).to_list(200)
    head = await db.users.find_one({"org_id": org_id, "org_role": "head_of_operations"}, {"_id": 0, "id": 1, "full_name": 1, "email": 1})
    pending_invites = await db.organization_invites.find({"org_id": org_id, "accepted_at": None}, {"_id": 0}).to_list(100)
    return {"org": org, "members": members, "head_of_operations": head, "pending_invites": pending_invites}


@api_router.patch("/admin/orgs/{org_id}")
async def admin_update_org(
    org_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can manage organizations")
    org = await db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    allowed_fields = {"name", "rc_number", "company_name"}
    update_dict = {k: v for k, v in body.items() if k in allowed_fields and v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    await db.organizations.update_one({"id": org_id}, {"$set": update_dict})
    return {"message": "Organization updated"}


@api_router.post("/admin/orgs/{org_id}/invite")
async def admin_invite_to_org(
    org_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can manage organizations")
    org = await db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    email = body.get("email", "").strip().lower()
    org_role = body.get("org_role", "member")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    target_user = await db.users.find_one({"email": email})
    if target_user and target_user.get("org_id") and target_user["org_id"] != org_id:
        raise HTTPException(status_code=409, detail="This user already belongs to another organization")

    existing_invite = await db.organization_invites.find_one({
        "org_id": org_id, "email": email, "accepted_at": None,
    })
    if existing_invite:
        if existing_invite.get("expires_at") and datetime.fromisoformat(existing_invite["expires_at"]) < datetime.now(timezone.utc):
            await db.organization_invites.delete_one({"token": existing_invite["token"]})
        else:
            raise HTTPException(status_code=409, detail="An active invite already exists for this email.")

    invite_token = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    invite_doc = {
        "id": str(uuid.uuid4()),
        "org_id": org_id,
        "org_name": org["name"],
        "email": email,
        "token": invite_token,
        "created_by": current_user.id,
        "invited_by_name": current_user.full_name,
        "created_at": now.isoformat(),
        "expires_at": (now + timedelta(days=7)).isoformat(),
        "user_id": target_user["id"] if target_user else None,
        "accepted_at": None,
        "org_role": org_role,
    }
    await db.organization_invites.insert_one(invite_doc)

    frontend_url = os.getenv("FRONTEND_URL", settings.cors_origins_list[0] if settings.cors_origins_list else "http://localhost:3000")
    is_admin_role = org_role in ("admin", "head_of_operations")
    register_link = f"{frontend_url}/portal/register?invite={invite_token}"
    recipient_name = target_user.get("full_name", email) if target_user else email

    if is_admin_role:
        role_label = "Head of TBR Operations" if org_role == "head_of_operations" else "Organization Admin"
        html = build_org_invitation_html(
            recipient_name=recipient_name,
            invited_by=current_user.full_name,
            org_name=org["name"],
            join_code=org["join_code"],
            rc_number=org.get("rc_number", ""),
            portal_url=register_link,
        )
        subject = f"You've been invited as {role_label} for {org['name']}"
    else:
        html = build_org_invite_registration_email_html(
            recipient_name=recipient_name,
            invited_by=current_user.full_name,
            org_name=org["name"],
            register_link=register_link,
        )
        subject = f"You've been invited to join {org['name']} on TBR Solutions"

    try:
        await send_email(email, subject, html)
    except Exception as e:
        logger.error("Failed to send invitation email to %s: %s", email, e)
        await db.organization_invites.delete_one({"token": invite_token})
        raise HTTPException(status_code=500, detail="Failed to send invitation email.")

    return {"message": f"Invitation sent to {email}"}


@api_router.post("/admin/orgs/{org_id}/assign-head")
async def admin_assign_head_of_operations(
    org_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can assign operations heads")
    org = await db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.update_one(
        {"org_id": org_id, "org_role": "head_of_operations"},
        {"$set": {"org_role": "member"}}
    )
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"org_id": org_id, "org_role": "head_of_operations"}}
    )
    return {"message": f"{target_user.get('full_name', target_user['email'])} is now Head of TBR Operations for {org['name']}"}


@api_router.post("/admin/orgs/{org_id}/remove-member")
async def admin_remove_org_member(
    org_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can manage organizations")
    org = await db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user_id = body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    target_user = await db.users.find_one({"id": user_id})
    if not target_user or target_user.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail="User is not a member of this organization")

    await db.users.update_one(
        {"id": user_id},
        {"$unset": {"org_id": "", "org_role": ""}}
    )
    return {"message": f"Removed {target_user.get('full_name', target_user['email'])} from {org['name']}"}


@api_router.post("/admin/orgs/{org_id}/regenerate-code")
async def admin_regenerate_join_code(
    org_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only super admins can manage organizations")
    org = await db.organizations.find_one({"id": org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    new_code = _generate_join_code()
    while await db.organizations.find_one({"join_code": new_code}):
        new_code = _generate_join_code()

    await db.organizations.update_one({"id": org_id}, {"$set": {"join_code": new_code}})
    return {"message": "Join code regenerated", "join_code": new_code}


# ─── WORKFLOW QUEUE ROUTES ────────────────────────────────────────────

# Map old OrderStatus values to new WorkflowStage values for backwards compatibility
STATUS_TO_WORKFLOW = {
    "pending_review": "intake_review",
    "documents_required": "documents_required",
    "in_progress": "in_progress",
    "submitted": "ready_for_submission",
    "approved": "approved",
    "completed": "completed",
    "cancelled": "archived",
    "new_request": "new_request",
    "intake_review": "intake_review",
    "documents_received": "documents_received",
    "assigned_to_officer": "assigned_to_officer",
    "internal_review": "internal_review",
    "compliance_review": "compliance_review",
    "awaiting_client_feedback": "awaiting_client_feedback",
    "ready_for_submission": "ready_for_submission",
    "submitted_to_regulator": "submitted_to_regulator",
    "archived": "archived",
}

def normalize_stage(status):
    return STATUS_TO_WORKFLOW.get(status, status)

def stage_query(stage):
    """Return a query that matches both old and new status values for a given workflow stage."""
    mapped = normalize_stage(stage)
    # Collect all raw status values that map to this stage
    matching = [s for s, v in STATUS_TO_WORKFLOW.items() if v == mapped]
    if len(matching) == 1:
        return {"status": matching[0]}
    return {"status": {"$in": matching}}

async def get_priority(order: dict) -> str:
    """Calculate priority based on deadline proximity, client tier, revenue."""
    if order.get("status") in ("completed", "cancelled", "archived"):
        return PriorityLevel.LOW.value
    remaining_days = None
    if order.get("deadline"):
        try:
            dl = datetime.fromisoformat(order["deadline"])
            remaining_days = (dl - datetime.now(timezone.utc)).total_seconds() / 86400
        except Exception:
            pass
    if remaining_days is not None:
        if remaining_days < 0:
            return PriorityLevel.CRITICAL.value
        if remaining_days <= 2:
            return PriorityLevel.HIGH.value
        if remaining_days <= 7:
            return PriorityLevel.MEDIUM.value
    return PriorityLevel.LOW.value

async def log_audit(job_id: str, action: AuditAction, user_id: str, user_name: str, details: str, db: AsyncIOMotorDatabase, meta: Optional[dict] = None):
    log = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "action": action.value if hasattr(action, 'value') else action,
        "user_id": user_id,
        "user_name": user_name,
        "details": details,
        "metadata": meta or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db.audit_logs.insert_one(log)
    except Exception:
        pass

async def send_workflow_notification(user_id: str, title: str, message: str, job_id: str, db: AsyncIOMotorDatabase):
    notif = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": "workflow",
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {"job_id": job_id}
    }
    try:
        await db.notifications.insert_one(notif)
    except Exception as e:
        logger.error(f"Failed to create workflow notification: {e}")

async def trigger_workflow_actions(order: dict, new_status: str, current_user: User, db: AsyncIOMotorDatabase):
    """Automation rules when workflow status changes."""
    actions = []
    if new_status == WorkflowStage.DOCUMENTS_REQUIRED.value:
        client_id = order.get("user_id")
        if client_id:
            await send_workflow_notification(
                client_id, "Documents Required",
                f"Additional documents are needed for job #{order['id'][:8]}. Please check your portal.",
                order["id"], db
            )
            actions.append("client_notified_docs_required")
    elif new_status == WorkflowStage.ASSIGNED_TO_OFFICER.value:
        assigned = order.get("assigned_to")
        if assigned:
            await send_workflow_notification(
                assigned, "New Assignment",
                f"You have been assigned to job #{order['id'][:8]}.",
                order["id"], db
            )
            actions.append("assigned_officer_notified")
    elif new_status == WorkflowStage.READY_FOR_SUBMISSION.value:
        supers = await db.users.find({"role": UserRole.SUPER_ADMIN}, {"_id": 0, "id": 1}).to_list(100)
        for sa in supers:
            await send_workflow_notification(
                sa["id"], "Ready for Submission",
                f"Job #{order['id'][:8]} is ready for submission and requires approval.",
                order["id"], db
            )
        actions.append("super_admins_notified_ready")
    elif new_status == WorkflowStage.COMPLETED.value:
        client_id = order.get("user_id")
        if client_id:
            await send_workflow_notification(
                client_id, "Job Completed",
                f"Your job #{order['id'][:8]} has been completed successfully.",
                order["id"], db
            )
        actions.append("client_notified_completed")
    return actions

@api_router.get("/workflow/queue", response_model=None)
async def get_workflow_queue(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    stage: Optional[str] = None,
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {}
    if stage:
        query["status"] = stage
    if assigned_to:
        query["assigned_to"] = assigned_to
    if search:
        query["$or"] = [
            {"id": {"$regex": search, "$options": "i"}},
            {"form_data.company_name": {"$regex": search, "$options": "i"}},
            {"form_data.contact_person": {"$regex": search, "$options": "i"}},
        ]
    orders, total = await paginated_query(db.orders, query, "updated_at", page, limit)
    enriched = []
    for o in orders:
        e = await enrich_order(o, db)
        e["priority"] = await get_priority(o)
        enriched.append(e)
    if priority:
        enriched = [e for e in enriched if e.get("priority") == priority]
    return {"jobs": enriched, "total": total, "page": page, "limit": limit}

@api_router.get("/workflow/kanban", response_model=None)
async def get_workflow_kanban(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    stages = {}
    for ws in WORKFLOW_STAGES_ORDER:
        val = ws.value if hasattr(ws, 'value') else ws
        query = stage_query(val)
        if current_user.role != UserRole.SUPER_ADMIN:
            query["assigned_to"] = current_user.id
        stage_orders = await db.orders.find(query, {"_id": 0}).sort("updated_at", -1).to_list(50)
        enriched = []
        for o in stage_orders:
            e = await enrich_order(o, db)
            e["priority"] = await get_priority(o)
            enriched.append(e)
        now = datetime.now(timezone.utc)
        overdue = 0
        total_hours = 0
        for o in enriched:
            if o.get("deadline"):
                try:
                    dl = datetime.fromisoformat(o["deadline"])
                    if dl < now:
                        overdue += 1
                    created = datetime.fromisoformat(o.get("created_at", now.isoformat()))
                    total_hours += (now - created).total_seconds() / 3600
                except Exception:
                    pass
        avg_hours = round(total_hours / len(enriched), 1) if enriched else 0
        stages[val] = {
            "jobs": enriched,
            "count": len(enriched),
            "avg_processing_hours": avg_hours,
            "overdue": overdue,
            "sla_risk": "red" if overdue > len(enriched) * 0.3 else ("amber" if overdue > 0 else "green"),
        }
    return {"stages": stages}

@api_router.patch("/workflow/{job_id}/status", response_model=None)
async def update_workflow_status(
    job_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    new_status = body.get("status")
    comment = body.get("comment", "")
    if not new_status:
        raise HTTPException(status_code=400, detail="status is required")
    # Normalize to the workflow stage mapping
    new_status = normalize_stage(new_status)
    order = await db.orders.find_one({"id": job_id})
    if not order:
        raise HTTPException(status_code=404, detail="Job not found")
    old_status = order.get("status", "")
    update_dict = {
        "status": new_status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.orders.update_one({"id": job_id}, {"$set": update_dict})
    await log_audit(
        job_id, AuditAction.STATUS_CHANGE, current_user.id, current_user.full_name,
        f"Status changed from {old_status} to {new_status}{f': {comment}' if comment else ''}",
        db, {"from": old_status, "to": new_status}
    )
    if comment:
        await log_audit(
            job_id, AuditAction.COMMENT, current_user.id, current_user.full_name,
            comment, db
        )
    actions = await trigger_workflow_actions(order, new_status, current_user, db)
    updated = await db.orders.find_one({"id": job_id}, {"_id": 0})
    enriched = await enrich_order(updated, db)
    enriched["priority"] = await get_priority(updated)
    return {"job": enriched, "triggered_actions": actions}

@api_router.get("/workflow/{job_id}/audit", response_model=None)
async def get_job_audit_trail(
    job_id: str,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    logs = await db.audit_logs.find({"job_id": job_id}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"audit_logs": logs}

@api_router.post("/workflow/{job_id}/comment", response_model=None)
async def add_workflow_comment(
    job_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    comment = body.get("comment", "")
    if not comment:
        raise HTTPException(status_code=400, detail="comment is required")
    await log_audit(
        job_id, AuditAction.COMMENT, current_user.id, current_user.full_name,
        comment, db
    )
    return {"message": "Comment added"}

@api_router.get("/workflow/analytics", response_model=None)
async def get_workflow_analytics(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    is_super = current_user.role == UserRole.SUPER_ADMIN
    scope = {} if is_super else {"assigned_to": current_user.id}
    stage_analytics = []
    for ws in WORKFLOW_STAGES_ORDER:
        val = ws.value if hasattr(ws, 'value') else ws
        query = {**scope, **stage_query(val)}
        count = await db.orders.count_documents(query)
        stage_orders = await db.orders.find(query, {"_id": 0, "deadline": 1, "created_at": 1}).to_list(100)
        now = datetime.now(timezone.utc)
        overdue = 0
        total_hours = 0
        for o in stage_orders:
            if o.get("deadline"):
                try:
                    dl = datetime.fromisoformat(o["deadline"])
                    if dl < now:
                        overdue += 1
                except Exception:
                    pass
            if o.get("created_at"):
                try:
                    created = datetime.fromisoformat(o["created_at"])
                    total_hours += (now - created).total_seconds() / 3600
                except Exception:
                    pass
        avg_hours = round(total_hours / count, 1) if count else 0
        sla_risk = "red" if count > 0 and overdue / count > 0.3 else ("amber" if overdue > 0 else "green")
        stage_analytics.append({
            "stage": val, "count": count,
            "avg_processing_hours": avg_hours,
            "overdue": overdue, "sla_risk": sla_risk,
        })
    active = sum(a["count"] for a in stage_analytics if a["stage"] not in ("completed", "archived", "cancelled"))
    overdue_items = sum(a["overdue"] for a in stage_analytics)
    return {"stage_analytics": stage_analytics, "active_engagements": active, "total_overdue": overdue_items}

@api_router.get("/workflow/workload", response_model=None)
async def get_workflow_workload(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    admins = await db.users.find({"role": {"$in": ["super_admin", "operations_manager", "compliance_officer", "tax_officer", "legal_officer", "finance_officer"]}}, {"_id": 0, "hashed_password": 0}).to_list(100)
    workload = []
    for admin in admins:
        admin_id = admin.get("id")
        if not admin_id:
            continue
        active = await db.orders.count_documents({"assigned_to": admin_id, "status": {"$nin": ["completed", "cancelled", "archived"]}})
        overdue = await db.orders.count_documents({"assigned_to": admin_id, "deadline": {"$ne": None, "$lte": datetime.now(timezone.utc).isoformat()}, "status": {"$nin": ["completed", "cancelled", "archived"]}})
        completed = await db.orders.count_documents({"assigned_to": admin_id, "status": "completed"})
        total_jobs = await db.orders.count_documents({"assigned_to": admin_id})
        completion_rate = round(completed / total_jobs * 100, 1) if total_jobs > 20 else None
        capacity_pct = min(round(active / 15 * 100), 100) if active > 0 else 0
        workload.append({
            "user_id": admin_id,
            "name": admin.get("full_name", "Unknown"),
            "email": admin.get("email", ""),
            "role": admin.get("role", ""),
            "active": active,
            "overdue": overdue,
            "completed": completed,
            "completion_rate": completion_rate,
            "capacity_pct": capacity_pct,
        })
    workload.sort(key=lambda x: x["overdue"], reverse=True)
    return {"workload": workload}

@api_router.post("/workflow/{job_id}/escalate", response_model=None)
async def escalate_job(
    job_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    order = await db.orders.find_one({"id": job_id})
    if not order:
        raise HTTPException(status_code=404, detail="Job not found")
    reason = body.get("reason", "Manual escalation")
    severity = body.get("severity", PriorityLevel.HIGH.value)
    escalation = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "reason": reason,
        "severity": severity,
        "assigned_to": order.get("assigned_to"),
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
        "resolved_by": None,
        "notes": body.get("notes"),
    }
    await db.escalations.insert_one(escalation)
    await log_audit(
        job_id, AuditAction.ESCALATION, current_user.id, current_user.full_name,
        f"Escalated: {reason} (severity: {severity})", db
    )
    supers = await db.users.find({"role": UserRole.SUPER_ADMIN}, {"_id": 0, "id": 1}).to_list(100)
    for sa in supers:
        await send_workflow_notification(
            sa["id"], "Job Escalated",
            f"Job #{job_id[:8]} has been escalated. Reason: {reason}",
            job_id, db
        )
    return {"escalation": escalation}

@api_router.get("/workflow/escalations", response_model=None)
async def list_escalations(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    status: Optional[str] = None,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {}
    if status:
        query["status"] = status
    escalations = await db.escalations.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    enriched = []
    for esc in escalations:
        order = await db.orders.find_one({"id": esc["job_id"]}, {"_id": 0, "status": 1, "form_data": 1})
        if order:
            esc["job_status"] = order.get("status")
            fd = order.get("form_data", {})
            esc["client_name"] = fd.get("contact_person", fd.get("company_name", "N/A"))
            esc["company_name"] = fd.get("company_name", "")
        enriched.append(esc)
    return {"escalations": enriched}

@api_router.patch("/workflow/escalations/{esc_id}/resolve", response_model=None)
async def resolve_escalation(
    esc_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await db.escalations.update_one(
        {"id": esc_id},
        {"$set": {
            "status": "resolved",
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolved_by": current_user.id,
            "notes": body.get("notes", ""),
        }}
    )
    return {"message": "Escalation resolved"}

@api_router.get("/workflow/review-queue", response_model=None)
async def get_review_queues(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
    review_type: Optional[str] = None,
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    query = {"status": {"$in": ["pending", "in_review"]}}
    if review_type:
        query["review_type"] = review_type
    review_items = await db.review_queue.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    enriched = []
    for r in review_items:
        order = await db.orders.find_one({"id": r["job_id"]}, {"_id": 0})
        if order:
            e = await enrich_order(order, db)
            r["job"] = e
        enriched.append(r)
    counts = {}
    for rt in ReviewQueueType:
        val = rt.value if hasattr(rt, 'value') else rt
        counts[val] = await db.review_queue.count_documents({"review_type": val, "status": {"$in": ["pending", "in_review"]}})
    return {"review_items": enriched, "counts": counts}

@api_router.get("/workflow/team-tasks", response_model=None)
async def get_team_tasks(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    orders_with_reviewers = await db.orders.find(
        {"assigned_reviewers": {"$exists": True, "$not": {"$size": 0}}},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)

    shared_jobs = []
    for o in orders_with_reviewers:
        reviewers = o.get("assigned_reviewers", [])
        if len(reviewers) < 2:
            continue
        enriched = await enrich_order(o, db)
        reviewer_users = await db.users.find(
            {"id": {"$in": reviewers}},
            {"_id": 0, "id": 1, "full_name": 1, "role": 1}
        ).to_list(100)
        reviewer_map = {u["id"]: u["full_name"] for u in reviewer_users}
        enriched["reviewer_names"] = [reviewer_map.get(rid, rid) for rid in reviewers]
        enriched["reviewed_by_names"] = []
        reviewed_by = o.get("reviewed_by", [])
        if reviewed_by:
            enriched["reviewed_by_names"] = [reviewer_map.get(rid, rid) for rid in reviewed_by]
        enriched["pending_reviewers"] = [name for rid, name in zip(reviewers, enriched["reviewer_names"]) if rid not in reviewed_by]
        shared_jobs.append(enriched)

    active_reviews = await db.review_queue.find(
        {"status": "in_review"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)

    for r in active_reviews:
        order = await db.orders.find_one({"id": r["job_id"]}, {"_id": 0})
        if order:
            e = await enrich_order(order, db)
            r["job"] = e

    return {
        "shared_jobs": shared_jobs,
        "active_reviews": active_reviews,
    }

@api_router.post("/workflow/{job_id}/review", response_model=None)
async def submit_review_decision(
    job_id: str,
    body: dict,
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    decision = body.get("decision")  # approved, rejected, changes_requested
    review_type = body.get("review_type", "compliance_review")
    comments = body.get("comments", "")
    if not decision:
        raise HTTPException(status_code=400, detail="decision is required")
    review_item = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "review_type": review_type,
        "reviewer_id": current_user.id,
        "reviewer_name": current_user.full_name,
        "status": decision,
        "comments": comments,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.review_queue.insert_one(review_item)
    action = AuditAction.APPROVAL if decision == "approved" else (AuditAction.REJECTION if decision == "rejected" else AuditAction.REVIEW)
    await log_audit(job_id, action, current_user.id, current_user.full_name,
                    f"Review ({review_type}): {decision}. Comments: {comments}", db)
    if decision == "changes_requested":
        await db.orders.update_one({"id": job_id}, {"$set": {"status": WorkflowStage.AWAITING_CLIENT_FEEDBACK.value, "updated_at": datetime.now(timezone.utc).isoformat()}})
    elif decision == "rejected":
        await db.orders.update_one({"id": job_id}, {"$set": {"status": WorkflowStage.INTERNAL_REVIEW.value, "updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"review": review_item}

@api_router.get("/workflow/overview", response_model=None)
async def get_workflow_overview(
    current_user: User = Depends(get_current_user_dep),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    if current_user.role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    is_super = current_user.role == UserRole.SUPER_ADMIN
    scope = {} if is_super else {"assigned_to": current_user.id}
    total = await db.orders.count_documents(scope)
    terminal_stages = ["completed", "archived"]
    terminal_raw = [s for s, v in STATUS_TO_WORKFLOW.items() if v in terminal_stages]
    active = await db.orders.count_documents({**scope, "status": {"$nin": terminal_raw}})
    overdue = 0
    now = datetime.now(timezone.utc)
    async for o in db.orders.find({**scope, "deadline": {"$ne": None}, "status": {"$nin": ["completed", "archived"]}}, {"_id": 0, "deadline": 1}):
        try:
            if datetime.fromisoformat(o["deadline"]) < now:
                overdue += 1
        except Exception:
            pass
    escalations_open = await db.escalations.count_documents({"status": "open"})
    users = await db.users.find({"role": {"$ne": UserRole.CLIENT}}, {"_id": 0, "id": 1, "full_name": 1, "role": 1}).to_list(100)
    staff_count = len(users)
    return {
        "total_engagements": total,
        "active_engagements": active,
        "overdue_engagements": overdue,
        "open_escalations": escalations_open,
        "staff_count": staff_count,
    }

# Root route
@api_router.get("/")
async def root():
    return {"message": "TBR Solutions API v1.0", "status": "active"}

# Include router
app.include_router(api_router)

UPLOAD_DIR = ROOT_DIR / 'uploads'
TICKET_UPLOAD_DIR = UPLOAD_DIR / 'tickets'
TICKET_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=settings.cors_origins_list,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "X-API-Key", "X-CSRF-Token"],
    expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(DomainRestrictionMiddleware)
app.add_middleware(RateLimitMiddleware)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Register centralized error handlers
register_error_handlers(app)


async def handle_email_job(payload: dict):
    from services.email_service import send_email
    to_email = payload.get("to_email", "")
    subject = payload.get("subject", "")
    html_body = payload.get("html_body", "")
    if to_email and subject and html_body:
        await send_email(to_email, subject, html_body)


async def handle_ai_request_job(payload: dict):
    service_type = payload.get("service_type", "")
    prompt = payload.get("prompt", "")
    if service_type and prompt:
        from openai import AsyncOpenAI
        openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        payload["result"] = response.choices[0].message.content


async def handle_pdf_parse_job(payload: dict):
    file_path = payload.get("file_path", "")
    if file_path and os.path.exists(file_path):
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        payload["result"] = text


async def register_job_handlers(job_queue: JobQueue):
    job_queue.register_handler(JobType.SEND_EMAIL, handle_email_job)
    job_queue.register_handler(JobType.PROCESS_AI_REQUEST, handle_ai_request_job)
    job_queue.register_handler(JobType.PARSE_PDF, handle_pdf_parse_job)


@app.on_event("startup")
async def startup_db_client():
    await ensure_db_connected()

    # Ensure MongoDB indexes for performance
    await ensure_indexes(db)

    # Start job queue for async processing
    job_queue = get_job_queue(db)
    await register_job_handlers(job_queue)
    await job_queue.start()

    _background_tasks.append(asyncio.create_task(mongo_keepalive()))
    _background_tasks.append(asyncio.create_task(retry_pending_otps()))
    _background_tasks.append(asyncio.create_task(send_billing_reminders()))
    _background_tasks.append(asyncio.create_task(render_keepalive()))
    logger.info("Background tasks and job queue started")

@app.on_event("shutdown")
async def shutdown_db_client():
    for task in _background_tasks:
        task.cancel()
    await asyncio.gather(*_background_tasks, return_exceptions=True)
    _background_tasks.clear()

    job_queue = get_job_queue_instance()
    if job_queue:
        await job_queue.stop()

    global _korapay_client
    if _korapay_client:
        await _korapay_client.aclose()
    client.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
