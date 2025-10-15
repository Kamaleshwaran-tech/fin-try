from __future__ import annotations

import os
from typing import Iterable, List, Optional
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib

from ..core.config import get_settings


def _build_message(subject: str, body: str, attachments: Optional[Iterable[str]] = None) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg.attach(MIMEText(body))

    if attachments:
        for path in attachments:
            if not path:
                continue
            norm = os.path.abspath(path)
            if not os.path.isfile(norm):
                continue
            with open(norm, 'rb') as f:
                file_part = MIMEApplication(f.read(), name=os.path.basename(norm))
                file_part['Content-Disposition'] = f'attachment; filename="{os.path.basename(norm)}"'
                msg.attach(file_part)
    return msg


def send_report(to_emails: List[str], subject: str, body: str, attachments: Optional[List[str]] = None) -> None:
    settings = get_settings()
    if not settings.email_user or not settings.email_pass:
        raise ValueError("EMAIL_USER and EMAIL_PASS must be configured")

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(settings.email_user, settings.email_pass)

    msg = _build_message(subject, body, attachments)
    smtp.sendmail(from_addr=settings.email_user, to_addrs=to_emails, msg=msg.as_string())
    smtp.quit()
