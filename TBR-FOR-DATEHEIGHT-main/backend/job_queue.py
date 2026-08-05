import asyncio
import logging
import uuid
import traceback
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional, Callable, Awaitable, Dict, Any, List
from pydantic import BaseModel

from motor.motor_asyncio import AsyncIOMotorDatabase

from config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


class JobType(str, Enum):
    SEND_EMAIL = "send_email"
    PROCESS_AI_REQUEST = "process_ai_request"
    PARSE_PDF = "parse_pdf"
    GENERATE_DOCUMENT = "generate_document"
    CLEANUP_TEMP_FILES = "cleanup_temp_files"
    WEBHOOK_CALLBACK = "webhook_callback"
    SEND_NOTIFICATION = "send_notification"


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class Job(BaseModel):
    id: str
    type: JobType
    status: JobStatus = JobStatus.PENDING
    payload: Dict[str, Any]
    user_id: Optional[str] = None
    priority: int = 0
    max_retries: int = 3
    retry_count: int = 0
    error_message: Optional[str] = None
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = datetime.now(timezone.utc).isoformat()


class JobQueue:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self._handlers: Dict[JobType, Callable] = {}
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._scheduler_task: Optional[asyncio.Task] = None
        self._in_memory_queue: asyncio.Queue = asyncio.Queue()
        self._active_jobs: Dict[str, asyncio.Task] = {}

    def register_handler(self, job_type: JobType, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        self._handlers[job_type] = handler

    async def enqueue(self, job_type: JobType, payload: Dict[str, Any],
                      user_id: Optional[str] = None, priority: int = 0,
                      max_retries: int = None, scheduled_at: Optional[str] = None) -> str:
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            type=job_type,
            payload=payload,
            user_id=user_id,
            priority=priority,
            max_retries=max_retries or settings.MAX_JOB_RETRIES,
            scheduled_at=scheduled_at,
        )
        try:
            await self.db.jobs.insert_one(job.model_dump())
        except Exception:
            pass
        await self._in_memory_queue.put(job)
        return job_id

    async def enqueue_email(self, to_email: str, subject: str, html_body: str,
                            user_id: Optional[str] = None, priority: int = 1) -> str:
        return await self.enqueue(
            JobType.SEND_EMAIL,
            {"to_email": to_email, "subject": subject, "html_body": html_body},
            user_id=user_id,
            priority=priority,
        )

    async def enqueue_ai_request(self, service_type: str, payload: Dict[str, Any],
                                 user_id: Optional[str] = None) -> str:
        return await self.enqueue(
            JobType.PROCESS_AI_REQUEST,
            {"service_type": service_type, **payload},
            user_id=user_id,
            priority=0,
        )

    async def enqueue_pdf_parse(self, file_path: str, options: Dict[str, Any] = None,
                                user_id: Optional[str] = None) -> str:
        return await self.enqueue(
            JobType.PARSE_PDF,
            {"file_path": file_path, "options": options or {}},
            user_id=user_id,
            priority=0,
        )

    async def _process_job(self, job: Job):
        if job.type not in self._handlers:
            logger.warning(f"No handler registered for job type: {job.type}")
            return

        handler = self._handlers[job.type]
        job_id = job.id

        try:
            await self.db.jobs.update_one(
                {"id": job_id},
                {"$set": {"status": JobStatus.RUNNING.value, "started_at": datetime.now(timezone.utc).isoformat()}}
            )

            await handler(job.payload)

            await self.db.jobs.update_one(
                {"id": job_id},
                {"$set": {
                    "status": JobStatus.COMPLETED.value,
                    "completed_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            logger.info(f"Job {job_id} ({job.type.value}) completed successfully")

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error(f"Job {job_id} ({job.type.value}) failed: {error_msg}")

            if job.retry_count < job.max_retries:
                new_retry_count = job.retry_count + 1
                await self.db.jobs.update_one(
                    {"id": job_id},
                    {"$set": {
                        "status": JobStatus.RETRYING.value,
                        "retry_count": new_retry_count,
                        "error_message": error_msg[:1000],
                    }}
                )

                delay = min(2 ** new_retry_count * 5, 300)
                retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                job.retry_count = new_retry_count
                job.status = JobStatus.RETRYING
                job.scheduled_at = retry_at.isoformat()

                await self.db.jobs.update_one(
                    {"id": job_id},
                    {"$set": {"scheduled_at": job.scheduled_at}}
                )

                await asyncio.sleep(delay)
                await self._in_memory_queue.put(job)
                logger.info(f"Job {job_id} scheduled for retry #{new_retry_count} in {delay}s")
            else:
                await self.db.jobs.update_one(
                    {"id": job_id},
                    {"$set": {
                        "status": JobStatus.FAILED.value,
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "error_message": error_msg[:1000],
                    }}
                )
                logger.error(f"Job {job_id} failed after {job.max_retries} retries")

    async def _worker_loop(self):
        while self._running:
            try:
                job = await asyncio.wait_for(self._in_memory_queue.get(), timeout=1.0)
                task = asyncio.create_task(self._process_job(job))
                self._active_jobs[job.id] = task
                task.add_done_callback(lambda t, jid=job.id: self._active_jobs.pop(jid, None))
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker loop error: {e}")

    async def _scheduler_loop(self):
        while self._running:
            try:
                now = datetime.now(timezone.utc).isoformat()
                cursor = self.db.jobs.find({
                    "status": {"$in": [JobStatus.PENDING.value, JobStatus.RETRYING.value]},
                    "$or": [
                        {"scheduled_at": None},
                        {"scheduled_at": {"$lte": now}}
                    ]
                }).sort("priority", -1).limit(50)

                async for job_doc in cursor:
                    job = Job(**job_doc)
                    await self._in_memory_queue.put(job)
                    await self.db.jobs.update_one(
                        {"id": job.id},
                        {"$set": {"status": JobStatus.PENDING.value}}
                    )
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

            await asyncio.sleep(settings.JOB_QUEUE_POLL_INTERVAL)

    async def start(self):
        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Job queue started")

    async def stop(self):
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
        if self._scheduler_task:
            self._scheduler_task.cancel()
        for task in self._active_jobs.values():
            task.cancel()
        if self._active_jobs:
            await asyncio.gather(*self._active_jobs.values(), return_exceptions=True)
        self._active_jobs.clear()
        logger.info("Job queue stopped")

    async def get_job_status(self, job_id: str) -> Optional[Job]:
        doc = await self.db.jobs.find_one({"id": job_id}, {"_id": 0})
        if doc:
            return Job(**doc)
        return None

    async def get_pending_count(self, job_type: Optional[JobType] = None) -> int:
        query = {"status": JobStatus.PENDING.value}
        if job_type:
            query["type"] = job_type.value
        return await self.db.jobs.count_documents(query)

    async def get_failed_jobs(self, limit: int = 50) -> List[Job]:
        cursor = self.db.jobs.find(
            {"status": JobStatus.FAILED.value},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        return [Job(**doc) async for doc in cursor]


_job_queue_instance = None


def get_job_queue(db: AsyncIOMotorDatabase) -> JobQueue:
    global _job_queue_instance
    if _job_queue_instance is None:
        _job_queue_instance = JobQueue(db)
    return _job_queue_instance


def get_job_queue_instance() -> Optional[JobQueue]:
    return _job_queue_instance
