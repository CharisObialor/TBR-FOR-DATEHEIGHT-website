import json
import logging
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from email_service import (
    get_contact_recipients,
    send_email,
    send_support_email,
    build_contact_form_html,
    build_contact_confirmation_html,
)

load_dotenv(Path(__file__).resolve().parent / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("website-backend")

BASE_PATH = Path(__file__).resolve().parent
SERVICES_PATH = BASE_PATH / "services_data.json"

with open(SERVICES_PATH, encoding="utf-8") as f:
    SERVICES = json.load(f)


class ContactForm(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    subject: str
    message: str


def cors_origins():
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://tbrsolutions.ng")
    return [o.strip() for o in raw.split(",") if o.strip()]


class ContactRateLimiter:
    def __init__(self, limit: int = 5, window_seconds: int = 3600):
        self.limit = limit
        self.window = window_seconds
        self.hits = {}

    def allow(self, key: str):
        now = time.time()
        window_start = now - self.window
        bucket = [t for t in self.hits.get(key, []) if t > window_start]
        if len(bucket) >= self.limit:
            retry_after = int(self.window - (now - bucket[0]))
            self.hits[key] = bucket
            return False, max(retry_after, 1)
        bucket.append(now)
        self.hits[key] = bucket
        return True, 0


rate_limiter = ContactRateLimiter(limit=int(os.getenv("CONTACT_RATE_LIMIT", "5")),
                                  window_seconds=int(os.getenv("CONTACT_RATE_WINDOW", "3600")))

app = FastAPI(title="TBR Solutions Website API", docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "website", "services_count": len(SERVICES)}


@app.get("/api/services")
async def list_services(category: Optional[str] = None, limit: Optional[int] = None):
    services = SERVICES
    if category:
        services = [s for s in services if s["category"] == category]
    if limit and limit > 0:
        services = services[:limit]
    return services


@app.post("/api/contact")
async def submit_contact_form(request: Request, form: ContactForm):
    client = request.client.host if request.client else "unknown"
    allowed, retry_after = rate_limiter.allow(client)
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many messages. Please try again later.", "retry_after_seconds": retry_after},
        )

    html_body = build_contact_form_html(
        name=form.name,
        email=form.email,
        phone=form.phone or "",
        subject=form.subject,
        message=form.message,
    )
    email_subject = f"Contact Form: {form.subject}"

    for recipient in get_contact_recipients():
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


@app.exception_handler(404)
async def not_found(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
