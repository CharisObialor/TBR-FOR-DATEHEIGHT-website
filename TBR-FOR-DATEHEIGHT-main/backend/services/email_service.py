import os
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, make_msgid
import aiosmtplib
from email_logo import EMAIL_LOGO_DATA_URI

logger = logging.getLogger(__name__)

def _support_email():
    return os.getenv("SUPPORT_EMAIL", "")


def email_logo_url():
    return os.getenv("EMAIL_LOGO_URL", "") or EMAIL_LOGO_DATA_URI


def _logo_header():
    url = email_logo_url()
    if not url:
        return ""
    return (
        f'<div style="text-align: center; padding: 24px 0 12px;">'
        f'<img src="{url}" alt="TBR Solutions" width="220" '
        f'style="max-width: 220px; width: 220px; height: auto; border: 0; display: inline-block;" />'
        f'</div>'
    )

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "email_templates"

_otp_html_template: str | None = None
_password_changed_html_template: str | None = None
_verification_link_html_template: str | None = None
_org_invitation_html_template: str | None = None
_org_invite_registration_html_template: str | None = None


def _load_template(filename: str) -> str:
    path = TEMPLATES_DIR / filename
    if not path.exists():
        logger.warning("Email template not found: %s", path)
        return "<p>__BODY__</p>"
    return path.read_text(encoding="utf-8")


def _ensure_templates():
    global _otp_html_template, _password_changed_html_template, _verification_link_html_template, _org_invitation_html_template, _org_invite_registration_html_template
    if _otp_html_template is None:
        _otp_html_template = _load_template("otp_email.html")
    if _password_changed_html_template is None:
        _password_changed_html_template = _load_template("password_changed.html")
    if _verification_link_html_template is None:
        _verification_link_html_template = _load_template("verification_link_email.html")
    if _org_invitation_html_template is None:
        _org_invitation_html_template = _load_template("org_invitation.html")
    if _org_invite_registration_html_template is None:
        _org_invite_registration_html_template = _load_template("org_invite_registration.html")


def build_otp_email_html(
    recipient_name: str,
    title: str,
    description: str,
    otp_code: str,
) -> str:
    _ensure_templates()
    return (
        _otp_html_template
        .replace("__RECIPIENT_NAME__", recipient_name)
        .replace("__TITLE__", title)
        .replace("__DESCRIPTION__", description)
        .replace("__OTP_CODE__", otp_code)
        .replace("__SUPPORT_EMAIL__", _support_email())
    )


def build_password_changed_html(
    changed_at: str = "",
    ip_address: str = "",
    device_info: str = "",
) -> str:
    _ensure_templates()
    return (
        _password_changed_html_template
        .replace("__CHANGED_AT__", changed_at)
        .replace("__IP_ADDRESS__", ip_address)
        .replace("__DEVICE_INFO__", device_info)
        .replace("__SUPPORT_EMAIL__", _support_email())
    )


def build_verification_link_email_html(
    recipient_name: str,
    verification_link: str,
) -> str:
    _ensure_templates()
    return (
        _verification_link_html_template
        .replace("__RECIPIENT_NAME__", recipient_name)
        .replace("__TITLE__", "Verify Your Account")
        .replace("__DESCRIPTION__", "Welcome to TBR! Click the button below to verify your email address and activate your account.")
        .replace("__VERIFICATION_LINK__", verification_link)
        .replace("__SUPPORT_EMAIL__", _support_email())
    )


def build_org_invite_registration_email_html(
    recipient_name: str,
    invited_by: str,
    org_name: str,
    register_link: str,
) -> str:
    _ensure_templates()
    return (
        _org_invite_registration_html_template
        .replace("__RECIPIENT_NAME__", recipient_name)
        .replace("__INVITED_BY__", invited_by)
        .replace("__ORG_NAME__", org_name)
        .replace("__REGISTER_LINK__", register_link)
        .replace("__SUPPORT_EMAIL__", _support_email())
    )


def build_org_invitation_html(
    recipient_name: str,
    invited_by: str,
    org_name: str,
    join_code: str,
    rc_number: str = "",
    portal_url: str = "http://localhost:3000/portal",
) -> str:
    _ensure_templates()
    rc_row = ""
    if rc_number:
        rc_row = f'<div class="details-row"><span class="details-label">RC Number</span><span class="details-value">{rc_number}</span></div>'
    return (
        _org_invitation_html_template
        .replace("__RECIPIENT_NAME__", recipient_name)
        .replace("__INVITED_BY__", invited_by)
        .replace("__ORG_NAME__", org_name)
        .replace("__JOIN_CODE__", join_code)
        .replace("__RC_NUMBER_ROW__", rc_row)
        .replace("__PORTAL_URL__", portal_url)
        .replace("__SUPPORT_EMAIL__", _support_email())
    )


async def send_email(to: str, subject: str, html_body: str, from_email_override: str = None):
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    if not smtp_password:
        logger.warning("SMTP_PASSWORD not set — skipping email send")
        return

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    from_email = from_email_override or os.getenv("FROM_EMAIL")
    from_name = os.getenv("FROM_NAME", "TBR Solutions")

    if not all([smtp_host, smtp_user, from_email]):
        logger.warning("SMTP_HOST, SMTP_USER, or FROM_EMAIL not set — skipping email send")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = _support_email()
    msg["Message-ID"] = make_msgid(domain="tbrsolutions.ng")
    msg["X-Mailer"] = "TBR Solutions Mail"
    msg["List-Unsubscribe"] = f"<mailto:{_support_email()}?subject=unsubscribe>"
    msg.attach(MIMEText(html_body, "html"))

    try:
        use_tls = smtp_port == 465
        await aiosmtplib.send(
            msg,
            sender=from_email,
            recipients=[to],
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=use_tls,
            start_tls=not use_tls,
            validate_certs=False,
            timeout=30,
        )
        logger.info("Email sent to %s: %s", to, subject)
    except Exception as e:
        logger.error("SMTP send error: %s", e)
        raise


INTERNAL_SENDER = "internal@tbrsolutions.ng"


async def send_internal_email(to: str, subject: str, html_body: str):
    """Send email from internal@tbrsolutions.ng for internal notifications."""
    await send_email(to, subject, html_body, from_email_override=INTERNAL_SENDER)


def build_payment_success_html(client_name: str, amount: float, service_title: str, reference: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1e293b; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">TBR GOT PAID!!</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">A payment has been received successfully.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Client</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{client_name}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Amount</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #16a34a;">₦{amount:,.2f}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Service</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{service_title}</td></tr>
                <tr><td style="padding: 8px; color: #64748b;"><strong>Reference</strong></td><td style="padding: 8px; font-family: monospace; font-size: 13px;">{reference}</td></tr>
            </table>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Internal Notification
        </div>
    </div>
    """


def build_ticket_notification_html(priority: str, subject: str, client_name: str, description: str) -> str:
    priority_upper = priority.upper()
    colors = {"low": "#3b82f6", "medium": "#eab308", "high": "#f97316", "urgent": "#ef4444"}
    color = colors.get(priority, "#64748b")
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: {color}; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 22px;">THERE IS A {priority_upper} PROBLEM</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">A new support ticket has been raised.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Subject</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{subject}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Priority</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: {color};">{priority_upper}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Client</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{client_name}</td></tr>
                <tr><td style="padding: 8px; color: #64748b;"><strong>Description</strong></td><td style="padding: 8px;">{description[:200]}</td></tr>
            </table>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Internal Notification
        </div>
    </div>
    """


def build_reminder_html(title: str, message: str, job_id: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #f59e0b; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 22px;">{title}</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">{message}</p>
            <p style="font-size: 14px; color: #64748b; margin-top: 12px;">Job ID: <code>{job_id[:8]}</code></p>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Internal Notification
        </div>
    </div>
    """


def build_contact_form_html(name: str, email: str, phone: str, subject: str, message: str) -> str:
    phone_row = ""
    if phone:
        phone_row = f'<tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Phone</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{phone}</td></tr>'
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        {_logo_header()}
        <div style="background: #1e293b; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 22px;">NEW CONTACT FORM SUBMISSION</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">A new message has been submitted through the contact form.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Name</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{name}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Email</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;"><a href="mailto:{email}">{email}</a></td></tr>
                {phone_row}
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Subject</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{subject}</td></tr>
                <tr><td style="padding: 8px; color: #64748b;"><strong>Message</strong></td><td style="padding: 8px; white-space: pre-wrap;">{message}</td></tr>
            </table>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Contact Form Notification
        </div>
    </div>
    """


async def send_billing_email(to: str, subject: str, html_body: str):
    """Send email from billing@tbrsolutions.ng for billing notifications."""
    smtp_host = os.getenv("BILLING_SMTP_HOST", "")
    smtp_port = int(os.getenv("BILLING_SMTP_PORT", "465"))
    smtp_user = os.getenv("BILLING_SMTP_USER", "")
    smtp_password = os.getenv("BILLING_SMTP_PASSWORD", "")
    from_email = os.getenv("BILLING_FROM_EMAIL", "")
    from_name = "TBR Solutions Billing"

    if not smtp_password:
        logger.warning("BILLING_SMTP_PASSWORD not set — skipping billing email send")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = from_email
    msg["Message-ID"] = make_msgid(domain="tbrsolutions.ng")
    msg["X-Mailer"] = "TBR Solutions Billing"
    msg.attach(MIMEText(html_body, "html"))

    try:
        use_tls = smtp_port == 465
        await aiosmtplib.send(
            msg,
            sender=from_email,
            recipients=[to],
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=use_tls,
            start_tls=not use_tls,
            validate_certs=False,
            timeout=30,
        )
        logger.info("Billing email sent to %s: %s", to, subject)
    except Exception as e:
        logger.error("Billing SMTP send error: %s", e)
        raise


async def send_support_email(to: str, subject: str, html_body: str):
    """Send email from support@tbrsolutions.ng for support/contact notifications."""
    smtp_host = os.getenv("SUPPORT_SMTP_HOST", "")
    smtp_port = int(os.getenv("SUPPORT_SMTP_PORT", "465"))
    smtp_user = os.getenv("SUPPORT_SMTP_USER", "")
    smtp_password = os.getenv("SUPPORT_SMTP_PASSWORD", "")
    from_email = os.getenv("SUPPORT_FROM_EMAIL", "support@tbrsolutions.ng")
    from_name = "TBR Solutions Support"

    if not smtp_password:
        logger.warning("SUPPORT_SMTP_PASSWORD not set — skipping support email send")
        return
    if not smtp_host or not smtp_user:
        logger.warning("SUPPORT_SMTP_HOST or SUPPORT_SMTP_USER not set — skipping support email send")
        return

    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = from_email
    msg["Message-ID"] = make_msgid(domain="tbrsolutions.ng")
    msg["X-Mailer"] = "TBR Solutions Support"
    msg.attach(MIMEText(html_body, "html"))

    try:
        use_tls = smtp_port == 465
        await aiosmtplib.send(
            msg,
            sender=from_email,
            recipients=[to],
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            use_tls=use_tls,
            start_tls=not use_tls,
            validate_certs=False,
            timeout=30,
        )
        logger.info("Support email sent to %s: %s", to, subject)
    except Exception as e:
        logger.error("Support SMTP send error: %s", e)
        raise


def build_ticket_opened_html(client_name: str, subject: str, ticket_id: str, priority: str) -> str:
    colors = {"low": "#3b82f6", "medium": "#eab308", "high": "#f97316", "urgent": "#ef4444"}
    color = colors.get(priority.lower(), "#64748b")
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #1e293b; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">SUPPORT TICKET OPENED</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">Hi {client_name},</p>
            <p style="font-size: 16px; color: #334155;">We have received your support request and a ticket has been created for you. Our team will review it and get back to you as soon as possible.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Ticket ID</strong></td><td style="padding: 8px; font-family: monospace; border-bottom: 1px solid #e2e8f0;">{ticket_id[:8]}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Subject</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{subject}</td></tr>
                <tr><td style="padding: 8px; color: #64748b;"><strong>Priority</strong></td><td style="padding: 8px; font-weight: bold; color: {color};">{priority.upper()}</td></tr>
            </table>
            <p style="font-size: 14px; color: #64748b;">You can track the status of your ticket by logging in to the client portal.</p>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Support
        </div>
    </div>
    """


def build_contact_confirmation_html(name: str, subject: str) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        {_logo_header()}
        <div style="background: #1e293b; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 24px;">WE'VE RECEIVED YOUR MESSAGE</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">Hi {name},</p>
            <p style="font-size: 16px; color: #334155;">Thank you for reaching out to us. We have received your message and our team will get back to you shortly.</p>
            <div style="background: #f1f5f9; border: 1px solid #e2e8f0; padding: 12px; margin: 16px 0; border-radius: 4px;">
                <p style="margin: 0; font-size: 14px; color: #475569;"><strong>Subject:</strong> {subject}</p>
            </div>
            <p style="font-size: 14px; color: #64748b;">If your matter is urgent, please call us directly or reply to this email.</p>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Support
        </div>
    </div>
    """


def build_billing_reminder_html(
    client_name: str,
    service_title: str,
    billing_period_end: str,
    days_remaining: int,
    months_paid: int,
    total_amount: float,
) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #f59e0b; color: white; padding: 20px; text-align: center;">
            <h1 style="margin: 0; font-size: 22px;">BILLING PERIOD ENDING SOON</h1>
        </div>
        <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155;">Your billing period for <strong>{service_title}</strong> is ending in <strong>{days_remaining} day{'s' if days_remaining != 1 else ''}</strong>.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Client</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{client_name}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Service</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{service_title}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Period Ends</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{billing_period_end}</td></tr>
                <tr><td style="padding: 8px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Months Paid</strong></td><td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{months_paid} month{'s' if months_paid != 1 else ''}</td></tr>
                <tr><td style="padding: 8px; color: #64748b;"><strong>Total Paid</strong></td><td style="padding: 8px; font-weight: bold; color: #16a34a;">&#8358;{total_amount:,.2f}</td></tr>
            </table>
            <div style="background: #fef3c7; border: 1px solid #fde68a; padding: 12px; margin-top: 16px; border-radius: 4px;">
                <p style="margin: 0; font-size: 14px; color: #92400e;">
                    <strong>Action Required:</strong> Please log in to the portal to renew your service before the billing period expires.
                </p>
            </div>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Billing Notification
        </div>
    </div>
    """


def build_login_alert_html(
    client_name: str,
    email: str,
    ip_address: str,
    device_info: str,
    location: str,
    attempt_count: int,
    timestamp: str,
) -> str:
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #dc2626; color: white; padding: 24px; text-align: center;">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin: 0 auto 12px;">
                <path d="M12 9v4m0 4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h1 style="margin: 0; font-size: 22px; letter-spacing: 0.5px;">UNAUTHORIZED LOGIN ATTEMPT</h1>
        </div>
        <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0;">
            <p style="font-size: 16px; color: #334155; margin: 0 0 16px;">Hi {client_name},</p>
            <p style="font-size: 16px; color: #334155; margin: 0 0 20px;">We detected <strong>{attempt_count} failed login attempt{'s' if attempt_count != 1 else ''}</strong> on your account. If this wasn't you, please reset your password immediately.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr>
                    <td style="padding: 10px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0; width: 40%;"><strong>Email</strong></td>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{email}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>IP Address</strong></td>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0; font-family: monospace;">{ip_address}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Location</strong></td>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{location}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 12px; color: #64748b; border-bottom: 1px solid #e2e8f0;"><strong>Device</strong></td>
                    <td style="padding: 10px 12px; border-bottom: 1px solid #e2e8f0;">{device_info}</td>
                </tr>
                <tr>
                    <td style="padding: 10px 12px; color: #64748b;"><strong>Time</strong></td>
                    <td style="padding: 10px 12px;">{timestamp}</td>
                </tr>
            </table>
            <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 14px; margin-top: 20px; border-radius: 4px;">
                <p style="margin: 0; font-size: 14px; color: #991b1b;">
                    <strong>What to do:</strong> If you did not attempt this login, please reset your password immediately or contact our support team at <a href="mailto:support@tbrsolutions.ng" style="color: #991b1b;">support@tbrsolutions.ng</a>.
                </p>
            </div>
        </div>
        <div style="text-align: center; padding: 12px; color: #94a3b8; font-size: 12px;">
            TBR Solutions — Security Alert
        </div>
    </div>
    """
