from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500, details: dict = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", resource: str = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource} if resource else None,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details,
        )


class RateLimitException(AppException):
    def __init__(self, message: str = "Too many requests", retry_after: int = 60):
        super().__init__(
            message=message,
            code="RATE_LIMITED",
            status_code=429,
            details={"retry_after_seconds": retry_after},
        )


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
        )


class ServiceUnavailableException(AppException):
    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(
            message=message,
            code="SERVICE_UNAVAILABLE",
            status_code=503,
        )


ERROR_STATUS_MAP = {
    400: "VALIDATION_ERROR",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}


def create_error_response(status_code: int, message: str, code: str = None, details: dict = None) -> dict:
    return {
        "error": message,
        "code": code or ERROR_STATUS_MAP.get(status_code, "UNKNOWN"),
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **(details or {}),
    }


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.status_code, exc.message, exc.code, exc.details),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    code = ERROR_STATUS_MAP.get(exc.status_code, "UNKNOWN")
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.status_code, exc.detail, code),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = {}
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error.get("loc", []))
        msg = error.get("msg", "")
        if loc:
            details[loc] = msg
        else:
            details["_error"] = msg

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            status_code=422,
            message="Validation failed",
            code="VALIDATION_ERROR",
            details=details if details else None,
        ),
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            status_code=500,
            message="An unexpected error occurred",
            code="INTERNAL_ERROR",
        ),
    )


def register_error_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
