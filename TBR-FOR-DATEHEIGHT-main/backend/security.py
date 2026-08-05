import time
import re
import hashlib
import html
from typing import Dict, Tuple, Optional, Callable
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorDatabase

from config import get_settings


settings = get_settings()


# ──────────────────────────────────────────────
# INPUT SANITIZER
# ──────────────────────────────────────────────

_script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
_on_event_pattern = re.compile(r'\bon\w+\s*=', re.IGNORECASE)
_js_protocol_pattern = re.compile(r'javascript\s*:', re.IGNORECASE)
_html_tag_pattern = re.compile(r'<[^>]*>')
_sql_injection_patterns = [
    re.compile(r"(\bSELECT\b.*\bFROM\b)", re.IGNORECASE),
    re.compile(r"(\bINSERT\b.*\bINTO\b)", re.IGNORECASE),
    re.compile(r"(\bUPDATE\b.*\bSET\b)", re.IGNORECASE),
    re.compile(r"(\bDELETE\b.*\bFROM\b)", re.IGNORECASE),
    re.compile(r"(\bDROP\b.*\bTABLE\b)", re.IGNORECASE),
    re.compile(r"(\bUNION\b.*\bSELECT\b)", re.IGNORECASE),
    re.compile(r"(\bALTER\b.*\bTABLE\b)", re.IGNORECASE),
    re.compile(r"(\bCREATE\b.*\bTABLE\b)", re.IGNORECASE),
    re.compile(r"(\bEXEC\b|\bEXECUTE\b)", re.IGNORECASE),
    re.compile(r"(--)", re.IGNORECASE),
    re.compile(r"(\bOR\b.*\b=\b.*\bOR\b)", re.IGNORECASE),
]


def sanitize_string(value: str, max_length: int = 10000) -> str:
    if not isinstance(value, str):
        return str(value) if value is not None else ""
    value = value[:max_length]
    value = _script_pattern.sub("", value)
    value = _on_event_pattern.sub("", value)
    value = _js_protocol_pattern.sub("", value)
    value = html.escape(value, quote=True)
    return value


def sanitize_html(value: str, max_length: int = 50000) -> str:
    if not isinstance(value, str):
        return str(value) if value is not None else ""
    value = value[:max_length]
    value = _script_pattern.sub("", value)
    value = _on_event_pattern.sub("", value)
    value = _js_protocol_pattern.sub("", value)
    return value


def has_sql_injection(value: str) -> bool:
    if not isinstance(value, str):
        return False
    for pattern in _sql_injection_patterns:
        if pattern.search(value):
            return True
    return False


def sanitize_object(obj, max_depth: int = 10):
    if max_depth <= 0:
        return obj
    if isinstance(obj, str):
        sanitized = sanitize_string(obj)
        if has_sql_injection(obj):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Potential SQL injection detected in input"
            )
        return sanitized
    elif isinstance(obj, dict):
        return {k: sanitize_object(v, max_depth - 1) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_object(item, max_depth - 1) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_object(item, max_depth - 1) for item in obj)
    return obj


# ──────────────────────────────────────────────
# RATE LIMITER (in-memory sliding window)
# ──────────────────────────────────────────────

class RateLimiter:
    def __init__(self):
        self._windows: Dict[str, list] = defaultdict(list)
        self._cleanup_interval = 300
        self._last_cleanup = time.time()

    def _cleanup(self):
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        cutoff = now - 3600
        for key in list(self._windows.keys()):
            self._windows[key] = [t for t in self._windows[key] if t > cutoff]
            if not self._windows[key]:
                del self._windows[key]
        self._last_cleanup = now

    def _get_client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        return client_ip

    def check(self, request: Request, limit: int, window: int, key_prefix: str = "rl") -> Tuple[bool, int]:
        self._cleanup()
        client_key = self._get_client_key(request)
        route_key = f"{key_prefix}:{client_key}:{request.url.path}"
        now = time.time()
        window_start = now - window

        timestamps = self._windows[route_key]
        timestamps[:] = [t for t in timestamps if t > window_start]

        if len(timestamps) >= limit:
            oldest = timestamps[0] if timestamps else now
            retry_after = int(window - (now - oldest))
            return False, max(retry_after, 1)

        timestamps.append(now)
        remaining = limit - len(timestamps)
        return True, remaining

    def check_user_bucket(self, user_id: str, limit: int, window: int, bucket: str = "default") -> Tuple[bool, int]:
        self._cleanup()
        key = f"user:{bucket}:{user_id}"
        now = time.time()
        window_start = now - window

        timestamps = self._windows[key]
        timestamps[:] = [t for t in timestamps if t > window_start]

        if len(timestamps) >= limit:
            oldest = timestamps[0] if timestamps else now
            retry_after = int(window - (now - oldest))
            return False, max(retry_after, 1)

        timestamps.append(now)
        remaining = limit - len(timestamps)
        return True, remaining


_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    return _rate_limiter


# ──────────────────────────────────────────────
# DOMAIN RESTRICTION MIDDLEWARE
# ──────────────────────────────────────────────

class DomainRestrictionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            origin = request.headers.get("Origin", "")
            referer = request.headers.get("Referer", "")
            host = request.headers.get("Host", "")

            allowed_domains = settings.allowed_domains_list

            if origin or referer:
                source = origin or referer
                from urllib.parse import urlparse
                parsed = urlparse(source)
                domain = parsed.netloc or parsed.hostname or ""
                if ":" in domain:
                    domain = domain.split(":")[0]
                domain_port = parsed.netloc or ""

                if domain not in [d.split(":")[0] for d in allowed_domains] and \
                   domain_port not in allowed_domains:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"error": "Requests from this domain are not allowed", "code": "FORBIDDEN_DOMAIN"}
                    )
        return await call_next(request)


# ──────────────────────────────────────────────
# SECURITY HEADERS MIDDLEWARE
# ──────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        csp_connect = ["'self'", "https://api.korapay.com", "https://checkout.korapay.com", "https://apis.google.com"]
        if settings.ENVIRONMENT != "production":
            csp_connect.extend(["http://localhost:8000", "http://localhost:3000", "ws://localhost:3000"])

        csp_font = ["'self'", "https://fonts.gstatic.com", "https://api.fontshare.com"]
        csp_style = ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com", "https://api.fontshare.com"]

        csp_directives = [
            "default-src 'self'",
            f"script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com https://js.stripe.com",
            f"style-src {' '.join(csp_style)}",
            "img-src 'self' data: blob: https:",
            f"font-src {' '.join(csp_font)}",
            f"connect-src {' '.join(csp_connect)}",
            "frame-src 'self' https://js.stripe.com https://accounts.google.com",
            "object-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        if settings.COOKIE_SECURE:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response


# ──────────────────────────────────────────────
# RATE LIMITING MIDDLEWARE
# ──────────────────────────────────────────────

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            path = request.url.path
            limiter = get_rate_limiter()

            if path.startswith("/api/auth/"):
                allowed, remaining = limiter.check(request, settings.RATE_LIMIT_AUTH, settings.RATE_LIMIT_AUTH_WINDOW, "auth")
            elif path.startswith("/api/otp") or "otp" in path or "verify-email" in path:
                allowed, remaining = limiter.check(request, settings.RATE_LIMIT_OTP, settings.RATE_LIMIT_OTP_WINDOW, "otp")
            else:
                allowed, remaining = limiter.check(request, settings.RATE_LIMIT_API, settings.RATE_LIMIT_API_WINDOW, "api")

            if not allowed:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too many requests. Please try again later.",
                        "code": "RATE_LIMITED",
                        "retry_after_seconds": remaining,
                    },
                    headers={"Retry-After": str(remaining)},
                )
        return await call_next(request)


# ──────────────────────────────────────────────
# ROW-LEVEL SECURITY MIDDLEWARE
# ──────────────────────────────────────────────

def enforce_user_data_isolation(query: dict, user_id: str, allowed_roles: Optional[list] = None) -> dict:
    query = query.copy()
    if "user_id" not in query:
        query["user_id"] = user_id
    return query


def get_user_scoped_query(query: dict, user_id: str, user_role: str) -> dict:
    admin_roles = ["super_admin", "operations_manager", "compliance_officer",
                   "tax_officer", "legal_officer", "finance_officer"]
    if user_role in admin_roles:
        return query
    return enforce_user_data_isolation(query, user_id)


# ──────────────────────────────────────────────
# TOKEN MANAGEMENT
# ──────────────────────────────────────────────

def generate_api_key() -> str:
    import secrets
    return f"tbr_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
