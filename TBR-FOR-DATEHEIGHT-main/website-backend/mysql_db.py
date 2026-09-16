import json
import logging
import os
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


def load_resources(published: Optional[bool] = None) -> list:
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

    if published is not None:
        docs = [d for d in docs if bool(d.get("published")) is published]
    return docs


def load_resource_by_slug(slug: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, doc FROM resources WHERE slug = %s LIMIT 1", (slug,))
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return None
    try:
        doc = json.loads(row["doc"])
    except (TypeError, ValueError):
        return None
    return doc if isinstance(doc, dict) else None


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