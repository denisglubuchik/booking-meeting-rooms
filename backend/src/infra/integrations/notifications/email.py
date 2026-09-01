import asyncio
import smtplib
import ssl
from email.message import EmailMessage

from opentelemetry import trace
from opentelemetry.trace import SpanKind

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
        if self.config.SMTP_USE_TLS:
            security = "tls"
        elif self.config.SMTP_USE_STARTTLS:
            security = "starttls"
        else:
            security = "plain"

        tracer = trace.get_tracer("infra.integrations.notifications.email")
        with tracer.start_as_current_span(
            "smtp.send",
            kind=SpanKind.CLIENT,
            attributes={
                "server.address": self.config.SMTP_HOST,
                "server.port": self.config.SMTP_PORT,
                "network.transport": "tcp",
                "smtp.security": security,
            },
        ):
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
