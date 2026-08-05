import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, make_msgid

import aiosmtplib
from email_logo import EMAIL_LOGO_DATA_URI

logger = logging.getLogger(__name__)

CONTACT_RECIPIENTS_DEFAULT = ["admin@tbrsolutions.ng", "support@tbrsolutions.ng"]


def get_contact_recipients():
    raw = os.getenv("CONTACT_RECIPIENTS", "")
    if not raw:
        return CONTACT_RECIPIENTS_DEFAULT
    return [r.strip() for r in raw.split(",") if r.strip()]


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


def _make_message(to: str, subject: str, html_body: str, from_name: str, from_email: str, reply_to: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = reply_to
    msg["Message-ID"] = make_msgid(domain="tbrsolutions.ng")
    msg["X-Mailer"] = "TBR Solutions"
    msg.attach(MIMEText(html_body, "html"))
    return msg


async def _smtp_send(host, port, user, password, from_email, to, msg, label):
    use_tls = int(port) == 465
    await aiosmtplib.send(
        msg,
        sender=from_email,
        recipients=[to],
        hostname=host,
        port=int(port),
        username=user,
        password=password,
        use_tls=use_tls,
        start_tls=not use_tls,
        validate_certs=False,
        timeout=30,
    )
    logger.info("%s email sent to %s: %s", label, to, msg["Subject"])


async def send_support_email(to: str, subject: str, html_body: str):
    host = os.getenv("SUPPORT_SMTP_HOST", "")
    port = os.getenv("SUPPORT_SMTP_PORT", "465")
    user = os.getenv("SUPPORT_SMTP_USER", "")
    password = os.getenv("SUPPORT_SMTP_PASSWORD", "")
    from_email = os.getenv("SUPPORT_FROM_EMAIL", "support@tbrsolutions.ng")

    if not password:
        logger.warning("SUPPORT_SMTP_PASSWORD not set — skipping support email send")
        return
    if not host or not user:
        logger.warning("SUPPORT_SMTP_HOST or SUPPORT_SMTP_USER not set — skipping support email send")
        return

    msg = _make_message(to, subject, html_body, "TBR Solutions Support", from_email, from_email)
    await _smtp_send(host, port, user, password, from_email, to, msg, "Support")


async def send_email(to: str, subject: str, html_body: str):
    password = os.getenv("SMTP_PASSWORD", "")
    if not password:
        logger.warning("SMTP_PASSWORD not set — skipping email send")
        return

    host = os.getenv("SMTP_HOST", "")
    port = os.getenv("SMTP_PORT", "587")
    user = os.getenv("SMTP_USER", "")
    from_email = os.getenv("FROM_EMAIL", "")
    from_name = os.getenv("FROM_NAME", "TBR Solutions")
    reply_to = os.getenv("SUPPORT_EMAIL", from_email)

    if not all([host, user, from_email]):
        logger.warning("SMTP_HOST, SMTP_USER, or FROM_EMAIL not set — skipping email send")
        return

    msg = _make_message(to, subject, html_body, from_name, from_email, reply_to)
    await _smtp_send(host, port, user, password, from_email, to, msg, "Main")


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
