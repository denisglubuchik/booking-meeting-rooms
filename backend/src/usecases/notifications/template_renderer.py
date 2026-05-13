from datetime import datetime
from zoneinfo import ZoneInfo

from domain.entities.notification import NotificationType
from usecases.interfaces.notifications import (
    NotificationTemplateRendererInterface,
)


class NotificationTemplateRenderer(NotificationTemplateRendererInterface):
    _MSK_TZ = ZoneInfo("Europe/Moscow")

    def _format_dt(self, value: str | None) -> str:
        if not value:
            return "-"
        try:
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=self._MSK_TZ)
            else:
                dt = dt.astimezone(self._MSK_TZ)
            return dt.strftime("%d.%m.%Y %H:%M")
        except ValueError:
            return value

    def _format_range(
        self,
        *,
        start_time: str | None,
        end_time: str | None,
    ) -> str:
        return f"{self._format_dt(start_time)} - {self._format_dt(end_time)}"

    def render_title(  # noqa: PLR6301
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
            time_range = self._format_range(
                start_time=payload.get("start_time"),
                end_time=payload.get("end_time"),
            )
            room_name = payload.get("room_name") or "-"
            return (
                "Вы добавлены как участник бронирования.\n"
                f"Тема: {booking_title}\n"
                f"Переговорная: {room_name}\n"
                f"Интервал: {time_range}"
            )
        if notification_type == NotificationType.BOOKING_START_REMINDER:
            booking_title = payload.get("booking_title") or "Без названия"
            time_range = self._format_range(
                start_time=payload.get("start_time"),
                end_time=payload.get("end_time"),
            )
            room_name = payload.get("room_name") or "-"
            return (
                "Скоро начнется бронирование.\n"
                f"Тема: {booking_title}\n"
                f"Переговорная: {room_name}\n"
                f"Интервал: {time_range}"
            )
        if notification_type == NotificationType.BOOKING_CANCELLED:
            booking_title = payload.get("booking_title") or "Без названия"
            time_range = self._format_range(
                start_time=payload.get("start_time"),
                end_time=payload.get("end_time"),
            )
            room_name = payload.get("room_name") or "-"
            return (
                "Бронирование было отменено.\n"
                f"Тема: {booking_title}\n"
                f"Переговорная: {room_name}\n"
                f"Планировалось: {time_range}"
            )
        if notification_type == NotificationType.BOOKING_RESCHEDULED:
            booking_title = payload.get("booking_title") or "Без названия"
            old_range = self._format_range(
                start_time=payload.get("old_start_time"),
                end_time=payload.get("old_end_time"),
            )
            new_range = self._format_range(
                start_time=payload.get("new_start_time"),
                end_time=payload.get("new_end_time"),
            )
            room_name = payload.get("room_name") or "-"
            return (
                "Время бронирования изменено.\n"
                f"Тема: {booking_title}\n"
                f"Переговорная: {room_name}\n"
                f"Было: {old_range}\n"
                f"Стало: {new_range}"
            )
        if notification_type == NotificationType.BOOKING_ROOM_CHANGED:
            booking_title = payload.get("booking_title") or "Без названия"
            time_range = self._format_range(
                start_time=payload.get("start_time"),
                end_time=payload.get("end_time"),
            )
            old_room_name = payload.get("old_room_name") or "-"
            new_room_name = payload.get("new_room_name") or "-"
            return (
                "Для бронирования выбрана другая переговорная.\n"
                f"Тема: {booking_title}\n"
                f"Интервал: {time_range}\n"
                f"Было: {old_room_name}\n"
                f"Стало: {new_room_name}"
            )
        return "У вас новое уведомление."
