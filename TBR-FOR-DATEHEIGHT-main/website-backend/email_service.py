import html as html_lib
import logging
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate, make_msgid

import aiosmtplib

logger = logging.getLogger(__name__)

CONTACT_RECIPIENTS_DEFAULT = ["admin@tbrsolutions.ng", "support@tbrsolutions.ng"]


def get_contact_recipients():
    raw = os.getenv("CONTACT_RECIPIENTS", "")
    if not raw:
        return CONTACT_RECIPIENTS_DEFAULT
    return [r.strip() for r in raw.split(",") if r.strip()]


_EMAIL_BG = "#f4f4f5"
_EMAIL_FONT = "Arial,Helvetica,sans-serif"
_EMAIL_TEXT = "#374151"
_EMAIL_MUTED = "#6b7280"
_EMAIL_INK = "#111827"
_EMAIL_BORDER = "#e4e4e7"


def email_logo_url():
    return os.getenv("EMAIL_LOGO_URL", "").strip() or "https://tbrsolutions.ng/images/logo.png"


def _logo_header():
    url = email_logo_url()
    if not url:
        return (
            f'<span style="font-family:{_EMAIL_FONT};font-size:18px;font-weight:700;'
            f'color:{_EMAIL_INK};">TBR Solutions</span>'
        )
    return (
        f'<img src="{url}" alt="TBR Solutions" height="34" '
        'style="height:34px;width:auto;max-width:200px;border:0;display:block;" />'
    )


def _heading(text):
    return (
        f'<h1 style="margin:0 0 16px;font-family:{_EMAIL_FONT};font-size:20px;'
        f'line-height:1.35;font-weight:700;color:{_EMAIL_INK};">{text}</h1>'
    )


def _paragraph(text, margin_bottom=14):
    return (
        f'<p style="margin:0 0 {margin_bottom}px;font-family:{_EMAIL_FONT};'
        f'font-size:14px;line-height:1.65;color:{_EMAIL_TEXT};">{text}</p>'
    )


def _section_label(text):
    return (
        f'<p style="margin:0 0 8px;font-family:{_EMAIL_FONT};font-size:11px;'
        'font-weight:700;letter-spacing:0.08em;text-transform:uppercase;'
        f'color:{_EMAIL_MUTED};">{text}</p>'
    )


def _details_table(rows):
    cells = []
    for label, value in rows:
        if not value:
            continue
        cells.append(
            '<tr>'
            f'<td style="padding:9px 16px 9px 0;border-bottom:1px solid #f1f1f2;'
            f'font-family:{_EMAIL_FONT};font-size:13px;line-height:1.5;color:{_EMAIL_MUTED};'
            'vertical-align:top;white-space:nowrap;">' + label + '</td>'
            f'<td style="padding:9px 0;border-bottom:1px solid #f1f1f2;'
            f'font-family:{_EMAIL_FONT};font-size:13px;line-height:1.5;color:{_EMAIL_INK};">'
            + value + '</td>'
            '</tr>'
        )
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        'style="width:100%;border-collapse:collapse;margin:0 0 20px;">'
        + ''.join(cells) + '</table>'
    )


def _message_block(text):
    return (
        f'<div style="background:#f9fafb;border:1px solid {_EMAIL_BORDER};'
        'padding:14px 16px;margin:0 0 20px;">'
        f'<p style="margin:0;font-family:{_EMAIL_FONT};font-size:13px;line-height:1.65;'
        f'color:{_EMAIL_TEXT};white-space:pre-wrap;">{text}</p>'
        '</div>'
    )


def _email_shell(body_html, preheader="", footer_note=""):
    preheader_html = ""
    if preheader:
        preheader_html = (
            f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{preheader}</div>'
        )
    footer_note_html = ""
    if footer_note:
        footer_note_html = (
            f'<p style="margin:10px 0 0;font-family:{_EMAIL_FONT};font-size:11px;'
            f'line-height:1.5;color:#9ca3af;">{footer_note}</p>'
        )
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
        '<title>TBR Solutions</title></head>'
        f'<body style="margin:0;padding:0;background-color:{_EMAIL_BG};">'
        + preheader_html
        + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'style="background-color:{_EMAIL_BG};"><tr><td align="center" style="padding:32px 16px;">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
        'style="width:600px;max-width:100%;background-color:#ffffff;'
        f'border:1px solid {_EMAIL_BORDER};">'
        '<tr><td style="padding:24px 32px 18px;'
        f'border-bottom:1px solid {_EMAIL_BORDER};">' + _logo_header() + '</td></tr>'
        '<tr><td style="padding:28px 32px 8px;">' + body_html + '</td></tr>'
        '<tr><td style="padding:18px 32px 24px;'
        f'border-top:1px solid {_EMAIL_BORDER};">'
        f'<p style="margin:0 0 4px;font-family:{_EMAIL_FONT};font-size:12px;'
        f'line-height:1.5;color:{_EMAIL_MUTED};">TBR Solutions</p>'
        f'<p style="margin:0 0 4px;font-family:{_EMAIL_FONT};font-size:12px;'
        f'line-height:1.5;color:{_EMAIL_MUTED};">'
        'Plot 5A, Block A10, Admiralty Way, Lekki, Lagos, Nigeria</p>'
        f'<p style="margin:0;font-family:{_EMAIL_FONT};font-size:12px;'
        f'line-height:1.5;color:{_EMAIL_MUTED};">'
        '<a href="https://tbrsolutions.ng" style="color:#4b5563;text-decoration:underline;">'
        'tbrsolutions.ng</a> &nbsp;|&nbsp; '
        '<a href="mailto:support@tbrsolutions.ng" style="color:#4b5563;text-decoration:underline;">'
        'support@tbrsolutions.ng</a></p>'
        + footer_note_html
        + '</td></tr>'
        '</table></td></tr></table></body></html>'
    )


def _html_to_text(html_body: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html_body, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</(p|div|h1|h2|h3|li|tr)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html_lib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _make_message(to: str, subject: str, html_body: str, from_name: str, from_email: str, reply_to: str) -> MIMEMultipart:
    support_email = os.getenv("SUPPORT_EMAIL", "support@tbrsolutions.ng")
    msg = MIMEMultipart("alternative")
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Reply-To"] = reply_to or support_email
    msg["Message-ID"] = make_msgid(domain="tbrsolutions.ng")
    msg["X-Mailer"] = "TBR Solutions"
    msg["List-Unsubscribe"] = f"<mailto:{support_email}?subject=unsubscribe>"
    msg.attach(MIMEText(_html_to_text(html_body), "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
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
        local_hostname=os.getenv("SMTP_HELO_HOSTNAME", "tbrsolutions.ng"),
    )
    logger.info("%s email sent to %s: %s", label, to, msg["Subject"])


async def send_support_email(to: str, subject: str, html_body: str):
    senders = (
        ("Primary", {
            "host": os.getenv("SMTP_HOST", ""),
            "port": os.getenv("SMTP_PORT", "465"),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("SMTP_USER", ""),
            "from_name": os.getenv("FROM_NAME", "TBR Solutions"),
        }),
        ("Support", {
            "host": os.getenv("SUPPORT_SMTP_HOST", ""),
            "port": os.getenv("SUPPORT_SMTP_PORT", "465"),
            "user": os.getenv("SUPPORT_SMTP_USER", ""),
            "password": os.getenv("SUPPORT_SMTP_PASSWORD", ""),
            "from_email": os.getenv("SUPPORT_FROM_EMAIL", "support@tbrsolutions.ng"),
            "from_name": "TBR Solutions Support",
        }),
    )

    reply_to = os.getenv("SUPPORT_EMAIL", "support@tbrsolutions.ng")
    last_error = None
    for label, cfg in senders:
        if not all([cfg["host"], cfg["user"], cfg["password"], cfg["from_email"]]):
            logger.warning("%s sender missing SMTP settings — skipping", label)
            continue
        msg = _make_message(to, subject, html_body, cfg["from_name"], cfg["from_email"], reply_to)
        try:
            await _smtp_send(cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["from_email"], to, msg, label)
            return
        except Exception as e:
            last_error = e
            logger.warning("%s sender failed for %s (%s); trying next sender", label, to, e)

    logger.error("All senders failed — email not sent to %s: %s", to, subject)
    if last_error is not None:
        raise last_error
    raise RuntimeError("No SMTP sender is configured")


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
    rows = [
        ("Name", html_lib.escape(name or "")),
        ("Email", html_lib.escape(email or "")),
        ("Phone", html_lib.escape(phone or "")),
        ("Subject", html_lib.escape(subject or "")),
    ]
    body = (
        _heading("New contact form submission")
        + _paragraph("A new enquiry was submitted through the TBR Solutions website.")
        + _details_table(rows)
        + _section_label("Message")
        + _message_block(html_lib.escape(message or ""))
    )
    return _email_shell(body, preheader="New contact form submission")


def build_contact_confirmation_html(name: str, subject: str, message: str) -> str:
    greeting = f"Hello {html_lib.escape(name)}," if name else "Hello,"
    body = (
        _heading("We received your message")
        + _paragraph(greeting)
        + _paragraph(
            "Thank you for contacting TBR Solutions. Your message has been received and a "
            "member of our team will respond within one business day."
        )
        + _section_label("Your message")
        + _details_table([("Subject", html_lib.escape(subject or ""))])
        + _message_block(html_lib.escape(message or ""))
        + _paragraph("If your matter is urgent, call us on +234 706 834 8923.")
        + _paragraph("Regards,<br>TBR Solutions", margin_bottom=0)
    )
    return _email_shell(body, preheader="We received your message")


def build_newsletter_welcome_html(name: str) -> str:
    greeting = f"Hello {html_lib.escape(name)}," if name else "Hello,"
    body = (
        _heading("Subscription confirmed")
        + _paragraph(greeting)
        + _paragraph(
            "Your email address has been added to the TBR Solutions mailing list. We send "
            "occasional updates on tax, regulatory and business compliance matters, usually "
            "one or two emails per month."
        )
        + _paragraph(
            'No further action is required. To unsubscribe, reply to this email with the '
            'word "unsubscribe".',
            margin_bottom=0,
        )
    )
    return _email_shell(
        body,
        preheader="TBR Solutions newsletter subscription confirmed",
        footer_note="You received this email because you subscribed at tbrsolutions.ng.",
    )
