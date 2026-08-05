import os
from typing import List, Optional
from functools import lru_cache


class Settings:
    def __init__(self):
        self.APP_NAME = "TBR Solutions API"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

        # MongoDB
        self.MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.DB_NAME = os.getenv("DB_NAME", "tbrtest")
        self.MONGO_MAX_POOL_SIZE = int(os.getenv("MONGO_MAX_POOL_SIZE", "100"))
        self.MONGO_MIN_POOL_SIZE = int(os.getenv("MONGO_MIN_POOL_SIZE", "10"))
        self.MONGO_MAX_IDLE_TIME_MS = int(os.getenv("MONGO_MAX_IDLE_TIME_MS", "120000"))
        self.MONGO_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "5000"))
        self.MONGO_CONNECT_TIMEOUT_MS = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "10000"))

        # JWT
        self.JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production-use-a-strong-random-secret")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "72"))
        self.JWT_REFRESH_EXPIRY_DAYS = int(os.getenv("JWT_REFRESH_EXPIRY_DAYS", "30"))

        # Password Reset
        self.PASSWORD_RESET_TOKEN_EXPIRY_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRY_MINUTES", "30"))

        # CORS
        self.CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://tbrsolutions.ng,https://9knq02tx-3000.uks1.devtunnels.ms")
        self.ALLOWED_DOMAINS = os.getenv("ALLOWED_DOMAINS", "localhost:3000,tbrsolutions.ng,20pq6blj-3000.uks1.devtunnels.ms,9knq02tx-3000.uks1.devtunnels.ms")

        # Cookies
        self.COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)
        self.COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

        # Rate Limiting
        self.RATE_LIMIT_GLOBAL = int(os.getenv("RATE_LIMIT_GLOBAL", "100"))
        self.RATE_LIMIT_GLOBAL_WINDOW = int(os.getenv("RATE_LIMIT_GLOBAL_WINDOW", "60"))
        self.RATE_LIMIT_AUTH = int(os.getenv("RATE_LIMIT_AUTH", "10"))
        self.RATE_LIMIT_AUTH_WINDOW = int(os.getenv("RATE_LIMIT_AUTH_WINDOW", "60"))
        self.RATE_LIMIT_OTP = int(os.getenv("RATE_LIMIT_OTP", "5"))
        self.RATE_LIMIT_OTP_WINDOW = int(os.getenv("RATE_LIMIT_OTP_WINDOW", "300"))
        self.RATE_LIMIT_API = int(os.getenv("RATE_LIMIT_API", "60"))
        self.RATE_LIMIT_API_WINDOW = int(os.getenv("RATE_LIMIT_API_WINDOW", "60"))

        # Email
        self.SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USER = os.getenv("SMTP_USER", "")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
        self.FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@tbrsolutions.ng")
        self.SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@tbrsolutions.ng")

        # Payment Gateway
        self.KORAPAY_SECRET_KEY = os.getenv("KORAPAY_SECRET_KEY", "")
        self.KORAPAY_PUBLIC_KEY = os.getenv("KORAPAY_PUBLIC_KEY", "")

        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

        # Google OAuth
        self.GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

        # AWS
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self.AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
        self.S3_BUCKET = os.getenv("S3_BUCKET", "")

        # Security
        self.ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "")
        self.BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
        self.SESSION_IDLE_TIMEOUT_MINUTES = int(os.getenv("SESSION_IDLE_TIMEOUT_MINUTES", "30"))

        # File Uploads
        self.MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
        self.ALLOWED_EXTENSIONS_STR = os.getenv("ALLOWED_EXTENSIONS", ".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg")

        # Async Job Queue
        self.JOB_QUEUE_POLL_INTERVAL = float(os.getenv("JOB_QUEUE_POLL_INTERVAL", "2.0"))
        self.MAX_JOB_RETRIES = int(os.getenv("MAX_JOB_RETRIES", "3"))

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_domains_list(self) -> List[str]:
        return [d.strip() for d in self.ALLOWED_DOMAINS.split(",") if d.strip()]

    @property
    def allowed_extensions_set(self) -> set:
        return {ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS_STR.split(",") if ext.strip()}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
