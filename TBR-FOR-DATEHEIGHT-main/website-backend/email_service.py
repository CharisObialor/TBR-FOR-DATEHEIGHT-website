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


_EMAIL_BG = "#f1f5f9"
_EMAIL_FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,Helvetica,sans-serif"


def email_logo_url():
    return os.getenv("EMAIL_LOGO_URL", "") or EMAIL_LOGO_DATA_URI


def _logo_header():
    url = email_logo_url()
    if not url:
        return ""
    return (
        f'<div style="text-align:center;padding:10px 0 22px;">'
        f'<img src="{url}" alt="TBR Solutions" width="190" '
        f'style="max-width:190px;width:190px;height:auto;border:0;display:inline-block;" />'
        f'</div>'
    )


def _hero(kicker, title, subtitle, image_url):
    kicker_html = ""
    if kicker:
        kicker_html = (
            f'<p style="margin:0 0 10px;font-size:11px;font-weight:700;'
            f'letter-spacing:3px;text-transform:uppercase;color:#93c5fd;">{kicker}</p>'
        )
    return (
        '<div style="border-radius:20px;overflow:hidden;border:1px solid #e2e8f0;">'
        f'<img src="{image_url}" alt="TBR Solutions" width="600" height="220" '
        'style="width:600px;max-width:100%;height:220px;object-fit:cover;display:block;border:0;"/>'
        '<div style="background:#0f172a;padding:30px 30px 28px;color:#ffffff;">'
        + kicker_html
        + f'<h1 style="margin:0 0 10px;font-size:26px;line-height:1.25;font-weight:800;'
          f'letter-spacing:-0.02em;">{title}</h1>'
        + f'<p style="margin:0;font-size:14px;line-height:1.6;color:#cbd5e1;">{subtitle}</p>'
        + '</div>'
        + '</div>'
    )


_UNSPLASH_QUERY = "?auto=format&fit=crop&w=1200&q=80"
_HERO_IMAGES = {
    "contact": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d" + _UNSPLASH_QUERY,
    "confirmation": "https://images.unsplash.com/photo-1556761175-b413da4baf72" + _UNSPLASH_QUERY,
    "newsletter": "https://images.unsplash.com/photo-1506784983877-45594efa4cbe" + _UNSPLASH_QUERY,
}


def _card(content):
    return (
        '<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:16px;'
        'box-shadow:0 12px 34px rgba(15,23,42,0.07);padding:30px 28px;">'
        + content
        + '</div>'
    )


def _badge(text, bg="#dbeafe", color="#1d4ed8"):
    return (
        f'<span style="display:inline-block;padding:6px 14px;border-radius:999px;'
        f'font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;'
        f'background:{bg};color:{color};">{text}</span>'
    )


def _label_row(label, value):
    return (
        '<div style="padding:14px 0;border-bottom:1px solid #f1f5f9;">'
        f'<p style="margin:0 0 5px;font-size:11px;font-weight:700;letter-spacing:1.5px;'
        f'text-transform:uppercase;color:#94a3b8;">{label}</p>'
        f'<p style="margin:0;font-size:15px;font-weight:600;color:#0f172a;">{value}</p>'
        '</div>'
    )


def _callout(heading, body, bg="#f8fafc", border="#2563eb"):
    heading_html = ""
    if heading:
        heading_html = (
            f'<p style="margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:1.5px;'
            f'text-transform:uppercase;color:#64748b;">{heading}</p>'
        )
    return (
        f'<div style="background:{bg};border:1px solid #e2e8f0;border-left:4px solid {border};'
        'border-radius:10px;padding:18px 20px;">'
        + heading_html
        + f'<p style="margin:0;font-size:14px;line-height:1.7;color:#334155;white-space:pre-wrap;">{body}</p>'
        + '</div>'
    )


def _check_item(text, square_bg="#dbeafe"):
    return (
        '<div style="padding:9px 0;">'
        f'<span style="display:inline-block;width:20px;height:20px;border-radius:6px;'
        f'background:{square_bg};vertical-align:middle;margin-right:12px;"></span>'
        f'<span style="font-size:14px;line-height:1.6;color:#334155;vertical-align:middle;">{text}</span>'
        '</div>'
    )


def _button(href, label, bg="#2563eb"):
    return (
        '<div style="text-align:center;padding-top:22px;">'
        f'<a href="{href}" style="display:inline-block;padding:14px 30px;border-radius:10px;'
        f'background:{bg};color:#ffffff;font-size:14px;font-weight:700;text-decoration:none;">{label}</a>'
        '</div>'
    )


def _email_shell(body_html, preheader=""):
    preheader_html = ""
    if preheader:
        preheader_html = (
            f'<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">{preheader}</div>'
        )
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"/></head>'
        f'<body style="margin:0;padding:0;background-color:{_EMAIL_BG};font-family:{_EMAIL_FONT};">'
        + preheader_html
        + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
        f'style="background-color:{_EMAIL_BG};"><tr><td align="center" style="padding:32px 16px 20px;">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" '
        'style="width:600px;max-width:100%;margin:0 auto;">'
        '<tr><td style="padding-bottom:8px;">' + _logo_header() + '</td></tr>'
        + '<tr><td>' + body_html + '</td></tr>'
        '<tr><td style="padding:26px 8px 8px;text-align:center;">'
        '<p style="margin:0 0 6px;font-size:12px;font-weight:600;color:#64748b;">TBR Solutions</p>'
        '<p style="margin:0 0 2px;font-size:12px;color:#94a3b8;">'
        'Plot 5A, Block A10, Admiralty Way, Lekki, Lagos, Nigeria</p>'
        '<p style="margin:0;font-size:12px;color:#94a3b8;">'
        '<a href="https://tbrsolutions.ng" style="color:#3b82f6;text-decoration:none;">tbrsolutions.ng</a>'
        ' &nbsp;|&nbsp; support@tbrsolutions.ng</p>'
        '</td></tr>'
        '</table></td></tr></table></body></html>'
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

    for label, cfg in senders:
        if not all([cfg["host"], cfg["user"], cfg["password"], cfg["from_email"]]):
            logger.warning("%s sender missing SMTP settings — skipping", label)
            continue
        msg = _make_message(to, subject, html_body, cfg["from_name"], cfg["from_email"], cfg["from_email"])
        try:
            await _smtp_send(cfg["host"], cfg["port"], cfg["user"], cfg["password"], cfg["from_email"], to, msg, label)
            return
        except Exception as e:
            logger.warning("%s sender failed for %s (%s); trying next sender", label, to, e)

    logger.error("All senders failed — email not sent to %s: %s", to, subject)


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
    rows = (
        _label_row("Name", name)
        + _label_row("Email", email)
        + (_label_row("Phone", phone) if phone else "")
        + _label_row("Subject", subject)
    )
    body = (
        _hero("Client Contact", "New Message Received",
              "A visitor has just submitted the contact form on the TBR Solutions website.",
              _HERO_IMAGES["contact"])
        + '<div style="padding:14px 0 0;">'
        + _card(
            _badge("Contact Form")
            + '<p style="margin:8px 0 16px;font-size:13px;color:#64748b;">'
              'The enquiry details are below for your review.</p>'
            + rows
            + _callout("Message", message)
        )
        + '</div>'
    )
    return _email_shell(body, preheader="New contact form submission on the TBR Solutions website")


def build_contact_confirmation_html(name: str, subject: str) -> str:
    body = (
        _hero("TBR Solutions", "We've Received Your Message",
              "Thank you for reaching out, our compliance team is on it.",
              _HERO_IMAGES["confirmation"])
        + '<div style="padding:14px 0 0;">'
        + _card(
            f'<p style="margin:0 0 8px;font-size:16px;font-weight:700;color:#0f172a;">Hi {name},</p>'
            '<p style="margin:0 0 16px;font-size:14px;line-height:1.7;color:#475569;">'
            'Thank you for contacting TBR Solutions. We have received your message and will '
            'respond to you shortly.</p>'
            + _callout("Subject", subject, bg="#eff6ff", border="#2563eb")
            + '<div style="padding:16px 2px 4px;">'
            + _check_item("Your enquiry has been logged with our compliance team.")
            + _check_item("We will respond to you within one business day.")
            + _check_item("For anything urgent, call us on +234 7068348923.")
            + '</div>'
            + _button("https://tbrsolutions.ng", "Visit our website")
        )
        + '</div>'
    )
    return _email_shell(body, preheader="We've received your message, TBR Solutions")


def build_newsletter_welcome_html(name: str) -> str:
    greeting = f"Hi {name}," if name else "Hello,"
    body = (
        _hero("TBR Solutions Newsletter", "Welcome aboard",
              "Practical tax, business and revenue assurance insights, straight to your inbox.",
              _HERO_IMAGES["newsletter"])
        + '<div style="padding:14px 0 0;">'
        + _card(
            f'<p style="margin:0 0 8px;font-size:16px;font-weight:700;color:#0f172a;">{greeting}</p>'
            '<p style="margin:0 0 16px;font-size:14px;line-height:1.7;color:#475569;">'
            'You are now subscribed to the TBR Solutions newsletter.</p>'
            + '<p style="margin:0 0 6px;font-size:11px;font-weight:700;letter-spacing:1.5px;'
              'text-transform:uppercase;color:#94a3b8;">What to expect</p>'
            + '<div style="padding:8px 2px 2px;">'
            + _check_item("Expert tax and regulatory insights")
            + _check_item("Revenue assurance best practices")
            + _check_item("Business compliance updates")
            + '</div>'
            + _callout("Stay informed",
                       "Expect 1-2 emails per month. We never share your details with third parties.")
            + _button("https://tbrsolutions.ng/services", "Explore our services")
        )
        + '</div>'
    )
    return _email_shell(body, preheader="Welcome to the TBR Solutions newsletter")
