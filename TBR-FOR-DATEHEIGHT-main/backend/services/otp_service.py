import secrets
import bcrypt
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
MAX_OTP_PER_HOUR = 10
RATE_LIMIT_WINDOW_HOURS = 1


def generate_otp() -> str:
    return f"{secrets.randbelow(10**OTP_LENGTH):06d}"


def hash_otp(otp: str) -> str:
    return bcrypt.hashpw(otp.encode(), bcrypt.gensalt(12)).decode()


def verify_otp_hash(otp: str, otp_hash: str) -> bool:
    return bcrypt.checkpw(otp.encode(), otp_hash.encode())


async def check_otp_rate_limit(email: str, purpose: str, db: AsyncIOMotorDatabase):
    since = datetime.now(timezone.utc) - timedelta(hours=RATE_LIMIT_WINDOW_HOURS)
    count = await db.otps.count_documents({
        "email": email,
        "purpose": purpose,
        "created_at": {"$gte": since.isoformat()}
    })
    if count >= MAX_OTP_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Too many OTP requests. Please try again later.",
                "code": "RATE_LIMIT_EXCEEDED",
                "retry_after": 3600
            }
        )


async def store_otp(email: str, purpose: str, db: AsyncIOMotorDatabase, metadata: dict | None = None) -> str:
    otp = generate_otp()
    otp_hash = hash_otp(otp)
    now = datetime.now(timezone.utc)
    doc = {
        "email": email,
        "otp_hash": otp_hash,
        "purpose": purpose,
        "expires_at": (now + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat(),
        "used": False,
        "sent": False,
        "send_attempts": 0,
        "created_at": now.isoformat(),
    }
    if metadata:
        doc.update(metadata)
    await db.otps.insert_one(doc)
    return otp


MAX_OTP_VALIDATION_ATTEMPTS = 5


async def validate_otp(email: str, otp: str, purpose: str, db: AsyncIOMotorDatabase):
    pending = await db.otps.find_one(
        {
            "email": email,
            "purpose": purpose,
            "used": False,
            "expires_at": {"$gte": datetime.now(timezone.utc).isoformat()}
        },
        sort=[("created_at", -1)]
    )
    if not pending:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid or expired OTP.", "code": "INVALID_OTP"}
        )

    validation_attempts = pending.get("validation_attempts", 0)
    if validation_attempts >= MAX_OTP_VALIDATION_ATTEMPTS:
        await db.otps.update_one(
            {"_id": pending["_id"]},
            {"$set": {"used": True}}
        )
        raise HTTPException(
            status_code=400,
            detail={"error": "Too many invalid attempts. Request a new OTP.", "code": "OTP_LOCKED"}
        )

    if not verify_otp_hash(otp, pending["otp_hash"]):
        await db.otps.update_one(
            {"_id": pending["_id"]},
            {"$inc": {"validation_attempts": 1}}
        )
        remaining = MAX_OTP_VALIDATION_ATTEMPTS - validation_attempts - 1
        raise HTTPException(
            status_code=400,
            detail={
                "error": f"Invalid OTP code. {remaining} attempt{'s' if remaining != 1 else ''} remaining.",
                "code": "INVALID_OTP",
                "remaining_attempts": remaining,
            }
        )

    await db.otps.update_one(
        {"_id": pending["_id"]},
        {"$set": {"used": True}}
    )


async def invalidate_pending_otps(email: str, purpose: str, db: AsyncIOMotorDatabase):
    await db.otps.update_many(
        {"email": email, "purpose": purpose, "used": False},
        {"$set": {"used": True}}
    )


async def mark_otp_sent(email: str, purpose: str, db: AsyncIOMotorDatabase):
    await db.otps.find_one_and_update(
        {"email": email, "purpose": purpose, "sent": False, "used": False},
        {"$set": {"sent": True, "sent_at": datetime.now(timezone.utc).isoformat()}},
        sort=[("created_at", -1)],
    )
