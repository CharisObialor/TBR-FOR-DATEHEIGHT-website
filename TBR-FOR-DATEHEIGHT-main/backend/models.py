from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    TAX_OFFICER = "tax_officer"
    LEGAL_OFFICER = "legal_officer"
    FINANCE_OFFICER = "finance_officer"
    OPERATIONS_MANAGER = "operations_manager"
    CLIENT = "client"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CLIENT = "waiting_on_client"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class OrderStatus(str, Enum):
    UNPAID = "unpaid"
    NEW_REQUEST = "new_request"
    PENDING_REVIEW = "pending_review"
    DOCUMENTS_REQUIRED = "documents_required"
    ASSIGNED_TO_OFFICER = "assigned_to_officer"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class WorkflowStage(str, Enum):
    NEW_REQUEST = "new_request"
    INTAKE_REVIEW = "intake_review"
    DOCUMENTS_REQUIRED = "documents_required"
    DOCUMENTS_RECEIVED = "documents_received"
    ASSIGNED_TO_OFFICER = "assigned_to_officer"
    IN_PROGRESS = "in_progress"
    INTERNAL_REVIEW = "internal_review"
    COMPLIANCE_REVIEW = "compliance_review"
    AWAITING_CLIENT_FEEDBACK = "awaiting_client_feedback"
    READY_FOR_SUBMISSION = "ready_for_submission"
    SUBMITTED_TO_REGULATOR = "submitted_to_regulator"
    APPROVED = "approved"
    COMPLETED = "completed"
    ARCHIVED = "archived"

WORKFLOW_STAGES_ORDER = [
    WorkflowStage.NEW_REQUEST,
    WorkflowStage.INTAKE_REVIEW,
    WorkflowStage.DOCUMENTS_REQUIRED,
    WorkflowStage.DOCUMENTS_RECEIVED,
    WorkflowStage.ASSIGNED_TO_OFFICER,
    WorkflowStage.IN_PROGRESS,
    WorkflowStage.INTERNAL_REVIEW,
    WorkflowStage.COMPLIANCE_REVIEW,
    WorkflowStage.AWAITING_CLIENT_FEEDBACK,
    WorkflowStage.READY_FOR_SUBMISSION,
    WorkflowStage.SUBMITTED_TO_REGULATOR,
    WorkflowStage.APPROVED,
    WorkflowStage.COMPLETED,
    WorkflowStage.ARCHIVED,
]

class PriorityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ReviewQueueType(str, Enum):
    TAX = "tax_review"
    COMPLIANCE = "compliance_review"
    LEGAL = "legal_review"
    FINANCE = "finance_review"

class AuditAction(str, Enum):
    STATUS_CHANGE = "status_change"
    COMMENT = "comment"
    FILE_UPLOAD = "file_upload"
    ASSIGNMENT = "assignment"
    APPROVAL = "approval"
    REJECTION = "rejection"
    ESCALATION = "escalation"
    NOTIFICATION = "notification"
    REVIEW = "review"

class WorkflowAnalytics(BaseModel):
    stage: str
    count: int
    avg_processing_hours: float
    overdue: int
    sla_risk: str  # green, amber, red

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    job_id: str
    action: AuditAction
    user_id: str
    user_name: str
    details: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str

class Escalation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    job_id: str
    reason: str
    severity: PriorityLevel
    assigned_to: Optional[str] = None
    status: str  # open, in_progress, resolved
    created_at: str
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None

class ReviewQueueItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    job_id: str
    review_type: ReviewQueueType
    reviewer_id: Optional[str] = None
    reviewer_name: Optional[str] = None
    status: str  # pending, in_review, approved, changes_requested, rejected
    comments: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class ServiceCategory(str, Enum):
    TAX = "tax"
    BUSINESS = "business"
    REGULATORY = "regulatory"
    DIGITAL = "digital"
    ESG = "esg"
    RISK = "risk"

class ServiceDivision(str, Enum):
    TAX_SERVICES = "Tax Services"
    BUSINESS_SERVICES = "Business Services"
    REGULATORY_SERVICES = "Regulatory Services"
    MODERN_SERVICES = "Modern Services"

# Permission Keys
PERMISSION_UPLOAD = "can_upload"
PERMISSION_REVIEW = "can_review"
PERMISSION_DOWNLOAD = "can_download"
PERMISSION_APPROVE = "can_approve"

DEFAULT_ADMIN_PERMISSIONS = {
    PERMISSION_UPLOAD: True,
    PERMISSION_REVIEW: True,
    PERMISSION_DOWNLOAD: True,
    PERMISSION_APPROVE: False,
}

DEFAULT_SUPER_ADMIN_PERMISSIONS = {
    PERMISSION_UPLOAD: True,
    PERMISSION_REVIEW: True,
    PERMISSION_DOWNLOAD: True,
    PERMISSION_APPROVE: True,
}

# Module visibility keys for admin portal sidebar
VISIBLE_MODULES_OPERATIONS = "operations"
VISIBLE_MODULES_DASHBOARD = "dashboard"
VISIBLE_MODULES_MY_TASKS = "my_tasks"
VISIBLE_MODULES_TEAM_TASKS = "team_tasks"
VISIBLE_MODULES_TICKETS = "tickets"
VISIBLE_MODULES_JOBS = "jobs"
VISIBLE_MODULES_WORKFLOW = "workflow"
VISIBLE_MODULES_REVIEW = "review"
VISIBLE_MODULES_ESCALATIONS = "escalations"
VISIBLE_MODULES_SLA = "sla"
VISIBLE_MODULES_PAYMENTS = "payments"
VISIBLE_MODULES_HISTORY = "history"
VISIBLE_MODULES_ADMIN_USERS = "admin_users"

DEFAULT_ADMIN_VISIBLE_MODULES = [
    VISIBLE_MODULES_MY_TASKS,
    VISIBLE_MODULES_TICKETS,
    VISIBLE_MODULES_JOBS,
    VISIBLE_MODULES_REVIEW,
    VISIBLE_MODULES_PAYMENTS,
    VISIBLE_MODULES_HISTORY,
]

SUPER_ADMIN_VISIBLE_MODULES = [
    VISIBLE_MODULES_OPERATIONS,
    VISIBLE_MODULES_DASHBOARD,
    VISIBLE_MODULES_MY_TASKS,
    VISIBLE_MODULES_TEAM_TASKS,
    VISIBLE_MODULES_JOBS,
    VISIBLE_MODULES_WORKFLOW,
    VISIBLE_MODULES_REVIEW,
    VISIBLE_MODULES_ESCALATIONS,
    VISIBLE_MODULES_SLA,
    VISIBLE_MODULES_PAYMENTS,
    VISIBLE_MODULES_HISTORY,
    VISIBLE_MODULES_ADMIN_USERS,
    "organizations",
]

def get_default_visible_modules(role: str) -> list:
    if role == UserRole.SUPER_ADMIN:
        return list(SUPER_ADMIN_VISIBLE_MODULES)
    if role == UserRole.CLIENT:
        return []
    return list(DEFAULT_ADMIN_VISIBLE_MODULES)

class AccountType(str, Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"

class OTPPurpose(str, Enum):
    SIGNUP = "signup"
    PASSWORD_RESET = "password_reset"

# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None
    role: UserRole = UserRole.CLIENT
    account_type: AccountType = AccountType.INDIVIDUAL
    email_verified: bool = False
    email_verified_at: Optional[str] = None
    org_id: Optional[str] = None
    org_role: Optional[str] = None

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    account_type: AccountType = AccountType.INDIVIDUAL
    rc_number: Optional[str] = None
    company_name: Optional[str] = None
    invite_token: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    created_at: str
    is_active: bool = True
    permissions: Optional[Dict[str, bool]] = None
    visible_modules: Optional[List[str]] = None

class UserInDB(User):
    hashed_password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    permissions: Optional[Dict[str, bool]] = None
    visible_modules: Optional[List[str]] = None
    email_verified: Optional[bool] = None
    email_verified_at: Optional[str] = None

class PermissionUpdate(BaseModel):
    permissions: Dict[str, bool]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User
    pending_invite: Optional[Dict] = None

class OTPRequest(BaseModel):
    email: EmailStr
    purpose: OTPPurpose

class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

class OTPResend(BaseModel):
    email: EmailStr
    purpose: OTPPurpose

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str
    confirm_password: str

class RegisterResponse(BaseModel):
    message: str
    token: Optional[str] = None
    user: Optional[User] = None

class VerifyEmailResponse(BaseModel):
    message: str
    next: Optional[str] = None
    token: Optional[str] = None
    user: Optional[User] = None

class ForgotPasswordResponse(BaseModel):
    message: str

class VerifyResetOTPResponse(BaseModel):
    reset_token: str

class ResetPasswordResponse(BaseModel):
    message: str

class ResendOTPResponse(BaseModel):
    message: str

# CAC Verification Models
from pydantic import Field

class CACVerificationRequest(BaseModel):
    id: str
    registration_type: str = Field(..., description="One of RC, BN, IT, LP, or LLP")
    registration_name: Optional[str] = None
    verification_consent: bool

class CACVerificationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class APIError(BaseModel):
    error: str
    code: str

class APISuccess(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None

# Service Models
class PricingTier(BaseModel):
    name: str
    price: float
    description: Optional[str] = None

class ServiceBase(BaseModel):
    title: str
    slug: str
    category: str
    division: Optional[str] = None
    subcategory: Optional[str] = None
    description: str
    features: List[str]
    process_steps: List[str]
    required_documents: List[str]
    estimated_timeline: str
    price_range: str
    pricing_tiers: Optional[List[PricingTier]] = None
    is_active: bool = True
    is_recurring: bool = False
    billing_cycle: Optional[str] = None  # monthly, quarterly, annually
    base_price_per_cycle: Optional[float] = None

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    category: Optional[str] = None
    division: Optional[str] = None
    subcategory: Optional[str] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    process_steps: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None
    estimated_timeline: Optional[str] = None
    price_range: Optional[str] = None
    pricing_tiers: Optional[List[PricingTier]] = None
    is_active: Optional[bool] = None

class Service(ServiceBase):
    model_config = ConfigDict(extra="ignore")
    id: str
    created_at: str

# Order/Service Request Models
class OrderCreate(BaseModel):
    service_id: str
    form_data: Dict[str, Any]
    notes: Optional[str] = None
    months_ahead: int = 1  # 1-24 months for recurring services

class OrderBulkCreate(BaseModel):
    orders: List[Dict[str, Any]]  # [{ service_id, notes?, form_data? }]

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    service_id: str
    status: OrderStatus
    form_data: Dict[str, Any]
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: str
    updated_at: str
    deadline: Optional[str] = None
    progress: Optional[int] = 0
    payment_reference: Optional[str] = None
    bulk_id: Optional[str] = None
    months_ahead: int = 1
    billing_period_start: Optional[str] = None
    billing_period_end: Optional[str] = None
    next_billing_date: Optional[str] = None
    billing_reminder_sent: bool = False

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
    deadline: Optional[str] = None
    form_data: Optional[dict] = None
    progress: Optional[int] = None  # 0-100 percentage

# Map service divisions to admin roles for auto-assignment
DIVISION_ROLE_MAP = {
    "Tax Services": "tax_officer",
    "Business Services": "operations_manager",
    "Regulatory Services": "compliance_officer",
    "Modern Services": "operations_manager",
}

# Document Models
class DocumentUpload(BaseModel):
    order_id: str
    document_type: str
    file_name: str
    file_url: str
    file_size: int

class Document(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    order_id: str
    user_id: str
    document_type: str
    file_name: str
    file_url: str
    file_size: int
    uploaded_at: str

# Payment Models
class PaymentInitiate(BaseModel):
    order_id: Optional[str] = None
    bulk_id: Optional[str] = None
    amount: Optional[float] = None
    callback_url: str

class Payment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    order_id: Optional[str] = None
    user_id: str
    amount: float
    reference: str
    status: str
    payment_method: Optional[str] = None
    bulk_id: Optional[str] = None
    created_at: str
    paid_at: Optional[str] = None

class RefundInitiate(BaseModel):
    payment_reference: str
    amount: Optional[float] = None
    reason: Optional[str] = None

class Refund(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    payment_id: str
    payment_reference: str
    refund_reference: str
    amount: float
    reason: Optional[str] = None
    status: str
    initiated_by: str
    created_at: str
    completed_at: Optional[str] = None

class AdminPaymentStats(BaseModel):
    model_config = ConfigDict(extra="ignore")
    total_revenue: float = 0
    total_refunded: float = 0
    net_revenue: float = 0
    total_transactions: int = 0
    successful_payments: int = 0
    failed_payments: int = 0
    pending_payments: int = 0
    total_refunds: int = 0
    monthly_revenue: List[float] = []
    monthly_labels: List[str] = []
    payment_methods: List[Dict[str, Any]] = []

# Invoice Models
class Invoice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    order_id: str
    user_id: str
    invoice_number: str
    amount: float
    items: List[Dict[str, Any]]
    status: str
    created_at: str
    paid_at: Optional[str] = None

# Resource/Blog Models
class ResourceCreate(BaseModel):
    title: str
    slug: str
    category: str
    excerpt: str
    content: str
    author: str
    tags: List[str]
    featured_image: Optional[str] = None

class Resource(ResourceCreate):
    model_config = ConfigDict(extra="ignore")
    id: str
    created_at: str
    views: int = 0

# Notification Models
class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    title: str
    message: str
    type: str
    read: bool = False
    created_at: str

# Ticket Models
class TicketCreate(BaseModel):
    subject: str
    category: str
    priority: TicketPriority = TicketPriority.MEDIUM
    description: str
    order_id: Optional[str] = None

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class TicketMessage(BaseModel):
    id: str
    user_id: str
    user_name: str
    message: str
    attachments: List[str] = []
    created_at: str

class Ticket(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    subject: str
    category: str
    priority: TicketPriority
    status: TicketStatus
    description: str
    order_id: Optional[str] = None
    assigned_to: Optional[str] = None
    messages: List[TicketMessage] = []
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None

# Review Models
class ReviewAction(str, Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"

class ReviewCreate(BaseModel):
    action: ReviewAction
    comments: str
    rating: Optional[int] = None

class Review(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    order_id: str
    reviewer_id: str
    reviewer_name: str
    action: ReviewAction
    comments: str
    rating: Optional[int] = None
    created_at: str

# Admin enriched order
class AdminOrder(Order):
    assigned_to_name: Optional[str] = None
    assigned_to_email: Optional[str] = None
    time_remaining_days: Optional[float] = None
    review: Optional[Review] = None
    reviews: List[Review] = []
    assigned_reviewers: Optional[List[str]] = None
    reviewed_by: Optional[List[str]] = None

# AI Checklist Models
class ChecklistRequest(BaseModel):
    service_type: str
    company_type: Optional[str] = None
    additional_context: Optional[str] = None

class ChecklistResponse(BaseModel):
    checklist: List[Dict[str, Any]]
    recommendations: List[str]

# Organization Models
class Organization(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    created_by: str
    created_at: str
    join_code: str
    rc_number: Optional[str] = None
    company_name: Optional[str] = None

class OrgCreateRequest(BaseModel):
    name: str
    rc_number: Optional[str] = None
    company_name: Optional[str] = None

class OrgJoinRequest(BaseModel):
    code: str

class OrgAddMemberRequest(BaseModel):
    email: str
    org_role: str = "member"

class OrgInviteAcceptRequest(BaseModel):
    token: str

class OrgInviteInfoResponse(BaseModel):
    org_name: str
    email: str
    invited_by: str


# Job / Task Queue Models
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
    model_config = ConfigDict(extra="ignore")
    id: str
    type: JobType
    status: JobStatus = JobStatus.PENDING
    payload: dict
    user_id: Optional[str] = None
    priority: int = 0
    max_retries: int = 3
    retry_count: int = 0
    error_message: Optional[str] = None
    scheduled_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = ""


class JobCreate(BaseModel):
    type: JobType
    payload: dict
    user_id: Optional[str] = None
    priority: int = 0
    max_retries: int = 3
    scheduled_at: Optional[str] = None


# Audit / Log Entry
class AuditLogEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    user_name: str
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: str


# Wallet Models
class WalletFundRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in Naira to fund wallet")

class WalletPayRequest(BaseModel):
    order_id: str
    amount: float = Field(..., gt=0)

class WalletTransferRequest(BaseModel):
    recipient_email: EmailStr
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class Wallet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    balance: float = 0.0
    currency: str = "NGN"
    created_at: str
    updated_at: str

class WalletTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    wallet_id: str
    user_id: str
    type: str  # "credit", "debit", "transfer_in", "transfer_out"
    amount: float
    balance_after: float
    reference: Optional[str] = None
    description: str
    status: str  # "pending", "completed", "failed"
    related_order_id: Optional[str] = None
    related_user_id: Optional[str] = None
    created_at: str

# API Key Model
class APIKey(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    key_hash: str
    prefix: str
    name: str
    user_id: str
    is_active: bool = True
    last_used_at: Optional[str] = None
    created_at: str
    expires_at: Optional[str] = None
