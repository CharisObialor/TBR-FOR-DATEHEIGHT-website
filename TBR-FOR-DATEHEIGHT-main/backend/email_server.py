import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from services.email_service import (
    send_email,
    build_password_changed_html,
)

load_dotenv(Path(__file__).resolve().parent / ".env")

POLL_INTERVAL_SECONDS = int(os.getenv("EMAIL_POLL_INTERVAL", "5"))
MAX_SEND_ATTEMPTS = int(os.getenv("EMAIL_MAX_SEND_ATTEMPTS", "3"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - email_server - %(levelname)s - %(message)s",
)
logger = logging.getLogger("email_server")


async def send_password_changed_email(user_doc: dict, db) -> bool:
    email = user_doc["email"]
    html = build_password_changed_html()

    try:
        await send_email(email, "Your TBR password was changed", html)
        return True
    except Exception as e:
        logger.error("Failed to send password changed email to %s: %s", email, e)
        return False


async def process_pending_notifications(db):
    cursor = db.notifications.find(
        {
            "type": "password_changed",
            "sent": False,
            "send_attempts": {"$lt": MAX_SEND_ATTEMPTS},
        },
        sort=[("created_at", 1)],
    )

    processed = 0
    async for notif_doc in cursor:
        user = await db.users.find_one({"id": notif_doc.get("user_id")})
        if not user:
            await db.notifications.update_one(
                {"_id": notif_doc["_id"]},
                {"$set": {"sent": True, "sent_at": datetime.now(timezone.utc).isoformat()}},
            )
            continue

        success = await send_password_changed_email(user, db)

        if success:
            await db.notifications.update_one(
                {"_id": notif_doc["_id"]},
                {
                    "$set": {
                        "sent": True,
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                    }
                },
            )
            logger.info("Delivered password changed notification to %s", user["email"])
        else:
            await db.notifications.update_one(
                {"_id": notif_doc["_id"]},
                {"$inc": {"send_attempts": 1}},
            )

        processed += 1

    return processed


async def poll_loop(db):
    logger.info("Email server started — polling every %ds", POLL_INTERVAL_SECONDS)
    while True:
        try:
            notif_count = await process_pending_notifications(db)
            if notif_count:
                logger.info("Sent %d notification(s)", notif_count)
        except Exception as e:
            logger.exception("Poll iteration error: %s", e)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


async def main():
    mongo_url = os.environ.get("MONGO_URL")
    if not mongo_url:
        logger.error("MONGO_URL environment variable is required")
        sys.exit(1)

    db_name = os.environ.get("DB_NAME", "tbrtest")

    client = AsyncIOMotorClient(
        mongo_url,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
        maxPoolSize=5,
        tls=True,
        tlsAllowInvalidCertificates=True,
        tlsAllowInvalidHostnames=True,
    )

    db = client[db_name]

    try:
        await client.admin.command("ping")
        logger.info("MongoDB connected — watching database: %s", db_name)
    except Exception as e:
        logger.error("MongoDB connection failed: %s", e)
        sys.exit(1)

    try:
        await poll_loop(db)
    except KeyboardInterrupt:
        logger.info("Shutting down email server...")
    finally:
        client.close()
        logger.info("Disconnected from MongoDB")


if __name__ == "__main__":
    asyncio.run(main())
