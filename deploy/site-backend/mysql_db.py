import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import pymysql
from pymysql.cursors import DictCursor

load_dotenv(Path(__file__).resolve().parent / ".env")

logger = logging.getLogger(__name__)


def get_conn():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", ""),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", ""),
        cursorclass=DictCursor,
        connect_timeout=10,
        charset="utf8mb4",
    )


_resources_cache = {"fetched_at": 0.0, "docs": []}
_RESOURCES_CACHE_TTL = float(os.getenv("RESOURCES_CACHE_TTL", "60"))


def _fetch_resources() -> list:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, doc FROM resources ORDER BY created_at DESC")
            rows = cur.fetchall()
    finally:
        conn.close()

    docs = []
    for row in rows:
        try:
            doc = json.loads(row["doc"])
        except (TypeError, ValueError):
            continue
        if not isinstance(doc, dict):
            continue
        docs.append(doc)
    return docs


def load_resources(published: Optional[bool] = None) -> list:
    now = time.monotonic()
    if now - _resources_cache["fetched_at"] >= _RESOURCES_CACHE_TTL or _resources_cache["docs"] is None:
        try:
            _resources_cache["docs"] = _fetch_resources()
            _resources_cache["fetched_at"] = now
        except Exception:
            if not _resources_cache["docs"]:
                raise
            logger.warning("Resources refresh failed — serving cached copy")

    docs = _resources_cache["docs"]

    if published is not None:
        docs = [d for d in docs if bool(d.get("published")) is published]
    return docs


def load_resource_by_slug(slug: str):
    for doc in load_resources():
        if doc.get("slug") == slug:
            return doc
    return None


_newsletter_table_ready = False


def ensure_newsletter_table():
    global _newsletter_table_ready
    if _newsletter_table_ready:
        return
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS newsletter_subscribers (
                    id VARCHAR(36) PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    name VARCHAR(255) DEFAULT NULL,
                    created_at VARCHAR(40) NOT NULL,
                    subscribed TINYINT(1) NOT NULL DEFAULT 1
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        conn.commit()
        _newsletter_table_ready = True
    finally:
        conn.close()


def create_subscriber(email: str, name: str = "") -> bool:
    """Insert a subscriber; returns True if newly added, False if already subscribed."""
    ensure_newsletter_table()
    normalized_name = (name or "").strip() or None
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT IGNORE INTO newsletter_subscribers (id, email, name, created_at, subscribed) "
                "VALUES (%s, %s, %s, %s, 1)",
                (
                    str(uuid.uuid4()),
                    email.lower().strip(),
                    normalized_name,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


_contact_table_ready = False


def ensure_contact_table():
    global _contact_table_ready
    if _contact_table_ready:
        return
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS contact_submissions (
                    id VARCHAR(36) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) DEFAULT NULL,
                    subject VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    created_at VARCHAR(40) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'new',
                    INDEX idx_contact_created_at (created_at),
                    INDEX idx_contact_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
            )
        conn.commit()
        _contact_table_ready = True
    finally:
        conn.close()


def create_contact_submission(name: str, email: str, phone: str, subject: str, message: str) -> str:
    """Persist a contact form submission and return its id."""
    ensure_contact_table()
    submission_id = str(uuid.uuid4())
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO contact_submissions "
                "(id, name, email, phone, subject, message, created_at, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, 'new')",
                (
                    submission_id,
                    name.strip(),
                    email.strip().lower(),
                    (phone or "").strip() or None,
                    subject.strip(),
                    message.strip(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        conn.commit()
        return submission_id
    finally:
        conn.close()


def load_contact_submissions(limit: int = 100) -> list:
    ensure_contact_table()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email, phone, subject, message, created_at, status "
                "FROM contact_submissions ORDER BY created_at DESC LIMIT %s",
                (max(1, int(limit)),),
            )
            return list(cur.fetchall())
    finally:
        conn.close()


def load_newsletter_subscribers(limit: int = 1000) -> list:
    ensure_newsletter_table()
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, name, created_at, subscribed "
                "FROM newsletter_subscribers ORDER BY created_at DESC LIMIT %s",
                (max(1, int(limit)),),
            )
            return list(cur.fetchall())
    finally:
        conn.close()