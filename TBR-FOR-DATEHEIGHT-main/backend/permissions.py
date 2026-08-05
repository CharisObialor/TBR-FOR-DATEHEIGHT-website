from fastapi import HTTPException, status
from typing import Dict, Any, List

# ──────────────────────────────────────────────────────────────────────────────
# PERMISSION SCHEMA
# ──────────────────────────────────────────────────────────────────────────────

PERMISSION_SCHEMA = {
    # ── Dashboard ─────────────────────────────────────────────────────────
    "dashboard.view": {
        "label": "View Dashboard",
        "description": "Access the admin dashboard",
        "module": "dashboard",
        "group": "Dashboard",
    },
    "dashboard.view_global": {
        "label": "View Global Stats",
        "description": "See stats across all admins (not just own)",
        "module": "dashboard",
        "group": "Dashboard",
    },

    # ── Orders / Jobs ─────────────────────────────────────────────────────
    "orders.view_all": {
        "label": "View All Orders",
        "description": "See all orders in the system",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.view_assigned": {
        "label": "View Assigned Orders",
        "description": "See only orders assigned to you",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.edit": {
        "label": "Edit Orders",
        "description": "Modify order details and progress",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.approve": {
        "label": "Approve Orders",
        "description": "Approve completed orders",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.cancel_complete": {
        "label": "Cancel / Complete Orders",
        "description": "Cancel or mark orders as completed",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.assign": {
        "label": "Assign Orders",
        "description": "Assign orders to admin staff",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.assign_reviewers": {
        "label": "Assign Reviewers",
        "description": "Assign reviewers to orders for multi-review",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.remind": {
        "label": "Send Reminders",
        "description": "Send reminders to assigned admins",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.delete": {
        "label": "Delete Orders",
        "description": "Delete orders from the system",
        "module": "jobs",
        "group": "Orders",
    },
    "orders.pick": {
        "label": "Self-Assign Jobs",
        "description": "Pick unassigned jobs from the queue",
        "module": "jobs",
        "group": "Orders",
    },

    # ── Documents ─────────────────────────────────────────────────────────
    "documents.upload": {
        "label": "Upload Documents",
        "description": "Upload documents to orders",
        "module": "jobs",
        "group": "Documents",
    },
    "documents.download": {
        "label": "Download Documents",
        "description": "Download order documents",
        "module": "jobs",
        "group": "Documents",
    },
    "documents.review": {
        "label": "Review Documents",
        "description": "Review and approve/reject documents",
        "module": "review",
        "group": "Documents",
    },
    "documents.submit_final": {
        "label": "Submit Final Documents",
        "description": "Submit final documents for completed orders",
        "module": "jobs",
        "group": "Documents",
    },

    # ── Users ─────────────────────────────────────────────────────────────
    "users.view": {
        "label": "View Admin Users",
        "description": "See the list of admin users",
        "module": "admin_users",
        "group": "User Management",
    },
    "users.create": {
        "label": "Create Admin Users",
        "description": "Create new admin accounts",
        "module": "admin_users",
        "group": "User Management",
    },
    "users.edit": {
        "label": "Edit Admin Users",
        "description": "Edit admin roles, permissions, and status",
        "module": "admin_users",
        "group": "User Management",
    },
    "users.delete": {
        "label": "Delete Admin Users",
        "description": "Remove admin accounts",
        "module": "admin_users",
        "group": "User Management",
    },

    # ── Organizations ─────────────────────────────────────────────────────
    "organizations.view": {
        "label": "View Organizations",
        "description": "See all organizations",
        "module": "organizations",
        "group": "Organizations",
    },
    "organizations.manage": {
        "label": "Manage Organizations",
        "description": "Create, edit, and delete organizations",
        "module": "organizations",
        "group": "Organizations",
    },

    # ── Tickets ───────────────────────────────────────────────────────────
    "tickets.view": {
        "label": "View Tickets",
        "description": "See support tickets",
        "module": "tickets",
        "group": "Support Tickets",
    },
    "tickets.manage": {
        "label": "Manage Tickets",
        "description": "Respond to and resolve tickets",
        "module": "tickets",
        "group": "Support Tickets",
    },

    # ── Workflow ──────────────────────────────────────────────────────────
    "workflow.view": {
        "label": "View Workflow",
        "description": "Access the workflow queue and kanban",
        "module": "workflow",
        "group": "Workflow",
    },
    "workflow.manage": {
        "label": "Manage Workflow",
        "description": "Update workflow statuses and stages",
        "module": "workflow",
        "group": "Workflow",
    },
    "workflow.escalate": {
        "label": "Escalate Jobs",
        "description": "Escalate jobs and manage escalations",
        "module": "escalations",
        "group": "Workflow",
    },
    "workflow.review": {
        "label": "Submit Reviews",
        "description": "Submit review decisions on jobs",
        "module": "workflow",
        "group": "Workflow",
    },
    "workflow.analytics": {
        "label": "View Analytics",
        "description": "See workflow analytics and performance data",
        "module": "workflow",
        "group": "Workflow",
    },
    "workflow.workload": {
        "label": "View Workload",
        "description": "See team workload distribution",
        "module": "workflow",
        "group": "Workflow",
    },
    "workflow.team_tasks": {
        "label": "View Team Tasks",
        "description": "See shared team tasks and review queue",
        "module": "team_tasks",
        "group": "Workflow",
    },

    # ── Payments ──────────────────────────────────────────────────────────
    "payments.view": {
        "label": "View Payments",
        "description": "See payment records and invoices",
        "module": "payments",
        "group": "Payments",
    },
    "payments.manage": {
        "label": "Manage Payments",
        "description": "Initiate and manage payments",
        "module": "payments",
        "group": "Payments",
    },

    # ── Services ──────────────────────────────────────────────────────────
    "services.view": {
        "label": "View Services",
        "description": "See available services",
        "module": "my_tasks",
        "group": "Services & Resources",
    },
    "services.manage": {
        "label": "Manage Services",
        "description": "Create, edit, and delete services",
        "module": "my_tasks",
        "group": "Services & Resources",
    },

    # ── Resources ─────────────────────────────────────────────────────────
    "resources.view": {
        "label": "View Resources",
        "description": "See blog posts and resources",
        "module": "my_tasks",
        "group": "Services & Resources",
    },
    "resources.manage": {
        "label": "Manage Resources",
        "description": "Create, edit, and delete resources",
        "module": "my_tasks",
        "group": "Services & Resources",
    },

    # ── Clients ───────────────────────────────────────────────────────────
    "clients.view": {
        "label": "View Clients",
        "description": "See client list and profiles",
        "module": "clients",
        "group": "Clients",
    },

    # ── SLA ───────────────────────────────────────────────────────────────
    "sla.view": {
        "label": "View SLA",
        "description": "See SLA monitoring data",
        "module": "sla",
        "group": "SLA & History",
    },

    # ── History ───────────────────────────────────────────────────────────
    "history.view": {
        "label": "View History",
        "description": "See order and activity history",
        "module": "history",
        "group": "SLA & History",
    },

    # ── Operations ────────────────────────────────────────────────────────
    "operations.view": {
        "label": "View Operations",
        "description": "Access the operations overview",
        "module": "operations",
        "group": "Operations",
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# DEFAULT PERMISSIONS BY ROLE
# ──────────────────────────────────────────────────────────────────────────────

SUPER_ADMIN_DEFAULTS = {key: True for key in PERMISSION_SCHEMA}

DEFAULT_ADMIN_PERMISSIONS: Dict[str, bool] = {
    "dashboard.view": True,
    "dashboard.view_global": False,
    "orders.view_all": False,
    "orders.view_assigned": True,
    "orders.edit": True,
    "orders.approve": False,
    "orders.cancel_complete": False,
    "orders.assign": False,
    "orders.assign_reviewers": False,
    "orders.remind": True,
    "orders.delete": False,
    "orders.pick": True,
    "documents.upload": True,
    "documents.download": True,
    "documents.review": True,
    "documents.submit_final": False,
    "users.view": False,
    "users.create": False,
    "users.edit": False,
    "users.delete": False,
    "organizations.view": False,
    "organizations.manage": False,
    "tickets.view": True,
    "tickets.manage": True,
    "workflow.view": True,
    "workflow.manage": True,
    "workflow.escalate": True,
    "workflow.review": True,
    "workflow.analytics": False,
    "workflow.workload": False,
    "workflow.team_tasks": True,
    "payments.view": True,
    "payments.manage": False,
    "services.view": True,
    "services.manage": False,
    "resources.view": True,
    "resources.manage": False,
    "clients.view": True,
    "sla.view": False,
    "history.view": True,
    "operations.view": False,
}

ROLE_DEFAULTS: Dict[str, Dict[str, bool]] = {
    "super_admin": dict(SUPER_ADMIN_DEFAULTS),
    "operations_manager": {
        **DEFAULT_ADMIN_PERMISSIONS,
        "dashboard.view_global": True,
        "orders.view_all": True,
        "orders.assign": True,
        "orders.cancel_complete": True,
        "users.view": True,
        "services.manage": True,
        "resources.manage": True,
        "operations.view": True,
        "workflow.analytics": True,
        "workflow.workload": True,
    },
    "compliance_officer": {
        **DEFAULT_ADMIN_PERMISSIONS,
        "orders.approve": True,
        "orders.cancel_complete": True,
    },
    "tax_officer": {
        **DEFAULT_ADMIN_PERMISSIONS,
        "orders.approve": True,
    },
    "legal_officer": {
        **DEFAULT_ADMIN_PERMISSIONS,
        "orders.approve": True,
    },
    "finance_officer": {
        **DEFAULT_ADMIN_PERMISSIONS,
        "payments.manage": True,
    },
    "client": {key: False for key in PERMISSION_SCHEMA},
}

# ──────────────────────────────────────────────────────────────────────────────
# MODULES derived from permissions (sidebar visibility)
# ──────────────────────────────────────────────────────────────────────────────

MODULE_PERMISSION_MAP = {
    "dashboard": ["dashboard.view"],
    "my_tasks": ["orders.view_assigned", "services.view", "resources.view"],
    "team_tasks": ["workflow.team_tasks"],
    "admin_users": ["users.view"],
    "organizations": ["organizations.view"],
    "clients": ["clients.view"],
    "jobs": ["orders.view_all", "orders.view_assigned"],
    "workflow": ["workflow.view"],
    "review": ["documents.review"],
    "escalations": ["workflow.escalate"],
    "sla": ["sla.view"],
    "payments": ["payments.view"],
    "history": ["history.view"],
    "operations": ["operations.view"],
    "tickets": ["tickets.view"],
}


# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_default_permissions(role: str) -> Dict[str, bool]:
    return dict(ROLE_DEFAULTS.get(role, DEFAULT_ADMIN_PERMISSIONS))


def migrate_old_permissions(old_perms: dict, role: str) -> Dict[str, bool]:
    new_perms = get_default_permissions(role)
    mapping = {
        "can_upload": "documents.upload",
        "can_review": "documents.review",
        "can_download": "documents.download",
        "can_approve": "orders.approve",
    }
    for old_key, new_key in mapping.items():
        if old_key in old_perms:
            new_perms[new_key] = bool(old_perms[old_key])
    return new_perms


def get_modules_from_permissions(perms: Dict[str, bool]) -> List[str]:
    modules = []
    for mod, required_perms in MODULE_PERMISSION_MAP.items():
        if any(perms.get(p, False) for p in required_perms):
            modules.append(mod)
    return modules


def check_permission(user, permission: str):
    from models import UserRole
    if user.role == UserRole.SUPER_ADMIN:
        return
    perms = user.permissions or {}
    if not perms.get(permission, False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing permission: {permission}",
            headers={"X-Missing-Permission": permission},
        )


def require_permission(permission: str):
    from fastapi import Depends
    from auth import get_current_user

    async def checker(current_user=Depends(get_current_user)):
        check_permission(current_user, permission)
        return current_user
    return Depends(checker)


def get_permission_groups() -> Dict[str, List[dict]]:
    groups = {}
    for key, meta in PERMISSION_SCHEMA.items():
        group = meta["group"]
        if group not in groups:
            groups[group] = []
        groups[group].append({"key": key, **meta})
    return groups
