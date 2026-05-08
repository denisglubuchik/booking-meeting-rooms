export const ru = {
  common: {
    unknownError: "Неизвестная ошибка",
  },
  api: {
    fallback: {
      invalidFields: "Проверьте корректность заполненных полей.",
      unauthorized: "Сессия истекла или неверные учетные данные.",
      forbidden: "Недостаточно прав для выполнения действия.",
      notFound: "Ресурс не найден.",
      serverError: "Внутренняя ошибка сервера.",
      requestFailed: "Запрос завершился с ошибкой ({status}).",
    },
    errors: {
      not_found: "Ресурс не найден.",
      forbidden: "Недостаточно прав для выполнения действия.",
      bad_request: "Некорректный запрос.",
      invalid_credentials: "Неверный email или пароль.",
      booking_time_in_past: "Нельзя создать бронирование в прошлом.",
      booking_horizon_exceeded: "Слишком дальняя дата бронирования.",
      room_unavailable: "Переговорная уже занята в выбранное время.",
      invalid_time_range: "Некорректный временной интервал.",
      invalid_booking_state: "Операция недоступна для текущего статуса бронирования.",
      permission_denied: "Недостаточно прав для выполнения действия.",
      application_error: "Ошибка приложения.",
      domain_error: "Ошибка бизнес-логики.",
      "auth.missing_bearer_token": "Требуется авторизация.",
      "auth.invalid_access_token": "Сессия истекла. Войдите снова.",
      "auth.user_deactivated": "Пользователь деактивирован.",
      "auth.admin_access_required": "Требуются права администратора.",
      "validation.request_invalid": "Проверьте корректность заполненных полей.",
    },
  },
} as const;
