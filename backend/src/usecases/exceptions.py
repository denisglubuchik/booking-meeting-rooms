class ApplicationError(Exception):
    pass


class NotFoundError(ApplicationError):
    pass


class BadRequest(ApplicationError):
    pass
