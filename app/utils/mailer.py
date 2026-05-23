import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

def send_email(
    subject: str,
    body: str,
    to_emails: List[str],
    from_email: Optional[str] = None,
    html: bool = False
):
    settings = get_settings()
    
    # Priority 1: Resend API
    if settings.RESEND_API_KEY:
        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "from": from_email or settings.RESEND_FROM,
                "to": to_emails,
                "subject": subject,
                "html" if html else "text": body
            }
            
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
            logger.info(f"Email sent successfully via Resend to {to_emails}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email via Resend: {str(e)}")
            # Fall back to SMTP if configured
            if not (settings.SMTP_USER and settings.SMTP_PASSWORD):
                return False

    # Priority 2: SMTP
    # Skip if credentials are not configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("No email provider configured (Resend or SMTP). Skipping email send.")
        return False

    msg = MIMEMultipart()
    msg['From'] = from_email or settings.SMTP_FROM or settings.SMTP_USER
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html' if html else 'plain'))

    try:
        if settings.SMTP_SSL:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            if settings.SMTP_TLS:
                server.starttls()
        
        with server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info(f"Email sent successfully via SMTP to {to_emails}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via SMTP: {str(e)}")
        return False
