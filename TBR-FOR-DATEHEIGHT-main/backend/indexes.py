from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

INDEXES = {
    "users": [
        {"keys": [("email", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("org_id", 1)], "options": {"background": True}},
        {"keys": [("role", 1)], "options": {"background": True}},
        {"keys": [("is_active", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
        {"keys": [("google_id", 1)], "options": {"sparse": True, "background": True}},
    ],
    "orders": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("status", 1)], "options": {"background": True}},
        {"keys": [("assigned_to", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
        {"keys": [("service_id", 1)], "options": {"background": True}},
        {"keys": [("user_id", 1), ("status", 1)], "options": {"background": True}},
        {"keys": [("assigned_to", 1), ("status", 1)], "options": {"background": True}},
        {"keys": [("deadline", 1)], "options": {"sparse": True, "background": True}},
    ],
    "tickets": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("assigned_to", 1)], "options": {"background": True}},
        {"keys": [("status", 1)], "options": {"background": True}},
        {"keys": [("priority", -1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
        {"keys": [("order_id", 1)], "options": {"sparse": True, "background": True}},
    ],
    "payments": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("order_id", 1)], "options": {"background": True}},
        {"keys": [("reference", 1)], "options": {"unique": True, "sparse": True, "background": True}},
        {"keys": [("status", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
    ],
    "documents": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("order_id", 1)], "options": {"background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("uploaded_at", -1)], "options": {"background": True}},
    ],
    "notifications": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("user_id", 1), ("read", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
    ],
    "otps": [
        {"keys": [("email", 1), ("purpose", 1)], "options": {"background": True}},
        {"keys": [("expires_at", 1)], "options": {"expireAfterSeconds": 0, "background": True}},
    ],
    "organizations": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("join_code", 1)], "options": {"unique": True, "sparse": True, "background": True}},
        {"keys": [("created_by", 1)], "options": {"background": True}},
    ],
    "organization_invites": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("email", 1)], "options": {"background": True}},
        {"keys": [("token", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("expires_at", 1)], "options": {"expireAfterSeconds": 0, "background": True}},
    ],
    "services": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("slug", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("category", 1)], "options": {"background": True}},
        {"keys": [("division", 1)], "options": {"background": True}},
        {"keys": [("is_active", 1)], "options": {"background": True}},
    ],
    "resources": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("slug", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("category", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
    ],
    "industries": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("slug", 1)], "options": {"unique": True, "background": True}},
    ],
    "audit_logs": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("job_id", 1)], "options": {"background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("action", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
    ],
    "reviews": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("order_id", 1)], "options": {"background": True}},
        {"keys": [("reviewer_id", 1)], "options": {"background": True}},
    ],
    "review_queue": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("job_id", 1)], "options": {"background": True}},
        {"keys": [("reviewer_id", 1)], "options": {"background": True}},
        {"keys": [("status", 1)], "options": {"background": True}},
    ],
    "escalations": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("job_id", 1)], "options": {"background": True}},
        {"keys": [("assigned_to", 1)], "options": {"background": True}},
        {"keys": [("status", 1)], "options": {"background": True}},
        {"keys": [("severity", 1)], "options": {"background": True}},
    ],
    "invoices": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("order_id", 1)], "options": {"background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("invoice_number", 1)], "options": {"unique": True, "background": True}},
    ],
    "wallets": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("user_id", 1)], "options": {"unique": True, "background": True}},
    ],
    "wallet_transactions": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("wallet_id", 1)], "options": {"background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
        {"keys": [("reference", 1)], "options": {"sparse": True, "background": True}},
        {"keys": [("status", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
        {"keys": [("user_id", 1), ("type", 1)], "options": {"background": True}},
    ],
    "jobs": [
        {"keys": [("id", 1)], "options": {"unique": True, "background": True}},
        {"keys": [("type", 1), ("status", 1)], "options": {"background": True}},
        {"keys": [("scheduled_at", 1)], "options": {"background": True}},
        {"keys": [("created_at", -1)], "options": {"background": True}},
        {"keys": [("user_id", 1)], "options": {"background": True}},
    ],
}


async def ensure_indexes(db: AsyncIOMotorDatabase):
    for collection_name, index_defs in INDEXES.items():
        try:
            collection = db[collection_name]
            existing_indexes = await collection.index_information()
            for idx_def in index_defs:
                keys = idx_def["keys"]
                options = idx_def.get("options", {})
                try:
                    await collection.create_indexes([{"key": dict(keys), **options}])
                except Exception:
                    await collection.create_index([(k, d) for k, d in keys], **options)
            logger.info(f"Indexes ensured for collection: {collection_name} ({len(index_defs)} indexes)")
        except Exception as e:
            logger.error(f"Failed to ensure indexes for {collection_name}: {e}")
