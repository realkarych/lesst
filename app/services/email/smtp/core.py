from __future__ import annotations

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

import aiosmtplib

from app.dtos.email import UserEmailDTO
from app.services.email.base.entities import EmailServers, OutgoingEmail


class SMTPClient:

    def __init__(self, server: EmailServers, email_data: UserEmailDTO):
        self._server = server
        self._email_data = email_data

    async def __aenter__(self) -> SMTPClient:
        smtp_client = aiosmtplib.SMTP(
            hostname=self._server.value.smtp.server,
            port=self._server.value.smtp.port,
            use_tls=True
        )
        self._client = smtp_client
        await smtp_client.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._client.quit()
        self._client.close()

    async def send(self, email: OutgoingEmail) -> None:
        msg = MIMEMultipart()

        msg["From"] = self._email_data.mail_address
        msg["To"] = email.send_to
        msg["Subject"] = email.subject

        msg.attach(MIMEText(email.text, "plain"))
        msg = self._submit_attachments_to_msg(msg=msg, email=email)

        await self._client.sendmail(
            sender=msg["From"],
            recipients=msg["To"],
            message=msg.as_string()
        )

    @staticmethod
    def _submit_attachments_to_msg(msg: MIMEMultipart, email: OutgoingEmail) -> MIMEMultipart:
        for attachment in email.attachments_paths or []:
            with open(attachment, "rb") as attachment_bytes:
                part = MIMEApplication(
                    attachment_bytes.read(),
                    Name=basename(attachment)
                )
            part["Content-Disposition"] = "attachment; filename=\"%s\"" % basename(attachment)
            msg.attach(part)
        return msg
