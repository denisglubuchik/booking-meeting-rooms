import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from core.config import EmailConfig
from domain.entities.notification import (
    NotificationChannel,
    NotificationDispatch,
)
from usecases.interfaces.notifications import NotificationSenderInterface


class SMTPEmailNotificationSender(NotificationSenderInterface):
    channel = NotificationChannel.EMAIL

    def __init__(self, config: EmailConfig) -> None:
        if config.SMTP_USE_TLS and config.SMTP_USE_STARTTLS:
            raise ValueError(
                "SMTP_USE_TLS and SMTP_USE_STARTTLS cannot both be true",
            )
        self.config = config

    async def send(self, dispatch: NotificationDispatch) -> None:
        await asyncio.to_thread(self._send_sync, dispatch)

    def _send_sync(self, dispatch: NotificationDispatch) -> None:
        message = EmailMessage()
        message["From"] = self.config.EMAIL_FROM
        message["To"] = dispatch.recipient
        message["Subject"] = dispatch.subject or "Уведомление"
        message.set_content(dispatch.body)

        context = ssl.create_default_context()
        timeout = self.config.SMTP_TIMEOUT_SECONDS
        if self.config.SMTP_USE_TLS:
            with smtplib.SMTP_SSL(
                self.config.SMTP_HOST,
                self.config.SMTP_PORT,
                timeout=timeout,
                context=context,
            ) as client:
                self._auth(client)
                client.send_message(message)
            return

        with smtplib.SMTP(
            self.config.SMTP_HOST,
            self.config.SMTP_PORT,
            timeout=timeout,
        ) as client:
            if self.config.SMTP_USE_STARTTLS:
                client.starttls(context=context)
            self._auth(client)
            client.send_message(message)

    def _auth(self, client: smtplib.SMTP) -> None:
        username = self.config.SMTP_USERNAME
        if not username:
            return
        password = self.config.SMTP_PASSWORD or ""
        client.login(username, password)
