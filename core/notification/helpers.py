import smtplib
from email.message import EmailMessage
from typing import Dict, Any
from core.notification.models import NotificationConfig
from core.config import settings


def _render_message(template: str, context: dict) -> str:
    """Substitui {placeholders} no message_template da regra."""
    for key, value in context.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def send_notification_email(config: NotificationConfig, context: Dict[str, Any]):
    recipients = config.recipients if isinstance(config.recipients, dict) else {}

    to_emails = recipients.get("to", [])
    cc_emails = recipients.get("cc", [])
    bcc_emails = recipients.get("bcc", [])

    msg = EmailMessage()
    msg["Subject"] = f"Audit Alert - {context.get('action', 'UNKNOWN')}"
    msg["From"] = settings.EMAIL_HOST_USER
    msg["To"] = ", ".join(to_emails)

    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)

    body = _render_message(config.messageTemplate, context)
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD.get_secret_value())
            all_recipients = to_emails + cc_emails + bcc_emails
            server.send_message(msg, to_addrs=all_recipients)
        print("Email enviado com sucesso")
    except Exception as e:
        print("Erro ao enviar email:")
        print(str(e))
        raise
