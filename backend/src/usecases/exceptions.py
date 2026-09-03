class ApplicationError(Exception):
    default_code = "application_error"
    default_status_code = 400

    def __init__(
        self,
        message: str = "",
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code or self.default_code
        self.status_code = status_code or self.default_status_code


class NotFoundError(ApplicationError):
    default_code = "not_found"
    default_status_code = 404


class BadRequest(ApplicationError):
    default_code = "bad_request"
    default_status_code = 400


class ForbiddenError(ApplicationError):
    default_code = "forbidden"
    default_status_code = 403


class UnauthorizedError(ApplicationError):
    default_code = "invalid_credentials"
    default_status_code = 401


class UserEmailAlreadyExistsError(ApplicationError):
    default_code = "user_email_already_exists"
    default_status_code = 409


class ConflictError(ApplicationError):
    default_code = "conflict"
    default_status_code = 409


class NotificationEnqueueError(ApplicationError):
    default_code = "notification_enqueue_failed"
    default_status_code = 500
