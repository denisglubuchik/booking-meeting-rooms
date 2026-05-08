from domain.entities.notification import NotificationType
from usecases.interfaces.notifications import (
    NotificationTemplateRendererInterface,
)


class NotificationTemplateRenderer(NotificationTemplateRendererInterface):
    @staticmethod
    def render_title(
        *,
        notification_type: NotificationType,
        payload: dict,
        locale: str = "ru",
    ) -> str:
        _ = payload, locale
        if notification_type == NotificationType.BOOKING_PARTICIPANT_ADDED:
            return "Вас добавили в бронирование"
        if notification_type == NotificationType.BOOKING_START_REMINDER:
            return "Напоминание о бронировании"
        return "Уведомление"

    @staticmethod
    def render_body(
        *,
        notification_type: NotificationType,
        payload: dict,
        locale: str = "ru",
    ) -> str:
        _ = locale
        if notification_type == NotificationType.BOOKING_PARTICIPANT_ADDED:
            booking_title = payload.get("booking_title") or "Без названия"
            start_time = payload.get("start_time") or "-"
            return (
                "Вы добавлены как участник бронирования.\n"
                f"Тема: {booking_title}\n"
                f"Начало: {start_time}"
            )
        if notification_type == NotificationType.BOOKING_START_REMINDER:
            booking_title = payload.get("booking_title") or "Без названия"
            start_time = payload.get("start_time") or "-"
            return (
                "Скоро начнется бронирование.\n"
                f"Тема: {booking_title}\n"
                f"Начало: {start_time}"
            )
        return "У вас новое уведомление."
