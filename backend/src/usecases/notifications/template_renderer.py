from domain.entities.notification import NotificationType
from usecases.interfaces.notifications import (
    NotificationTemplateRendererInterface,
)


class NotificationTemplateRenderer(NotificationTemplateRendererInterface):
    def render_title(
        self,
        *,
        notification_type: NotificationType,
        payload: dict,
        locale: str = "ru",
    ) -> str:
        _ = payload, locale
        if notification_type == NotificationType.BOOKING_PARTICIPANT_ADDED:
            return "Вас добавили в бронирование"
        if notification_type == NotificationType.BOOKING_CANCELLED:
            return "Бронирование отменено"
        if notification_type == NotificationType.BOOKING_RESCHEDULED:
            return "Бронирование перенесено"
        if notification_type == NotificationType.BOOKING_ROOM_CHANGED:
            return "Изменена переговорная в бронировании"
        if notification_type == NotificationType.BOOKING_START_REMINDER:
            return "Напоминание о бронировании"
        return "Уведомление"

    def render_body(
        self,
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
        if notification_type == NotificationType.BOOKING_CANCELLED:
            booking_title = payload.get("booking_title") or "Без названия"
            start_time = payload.get("start_time") or "-"
            return (
                "Бронирование было отменено.\n"
                f"Тема: {booking_title}\n"
                f"Планировалось на: {start_time}"
            )
        if notification_type == NotificationType.BOOKING_RESCHEDULED:
            booking_title = payload.get("booking_title") or "Без названия"
            old_start_time = payload.get("old_start_time") or "-"
            old_end_time = payload.get("old_end_time") or "-"
            new_start_time = payload.get("new_start_time") or "-"
            new_end_time = payload.get("new_end_time") or "-"
            return (
                "Время бронирования изменено.\n"
                f"Тема: {booking_title}\n"
                f"Было: {old_start_time} - {old_end_time}\n"
                f"Стало: {new_start_time} - {new_end_time}"
            )
        if notification_type == NotificationType.BOOKING_ROOM_CHANGED:
            booking_title = payload.get("booking_title") or "Без названия"
            start_time = payload.get("start_time") or "-"
            old_room_id = payload.get("old_room_id") or "-"
            new_room_id = payload.get("new_room_id") or "-"
            return (
                "Для бронирования выбрана другая переговорная.\n"
                f"Тема: {booking_title}\n"
                f"Начало: {start_time}\n"
                f"Было room_id: {old_room_id}\n"
                f"Стало room_id: {new_room_id}"
            )
        return "У вас новое уведомление."
