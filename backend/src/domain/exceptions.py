class DomainError(Exception):
    pass


class InvalidTimeRangeError(DomainError):
    pass


class InvalidBookingStateError(DomainError):
    pass


class RoomUnavailableError(DomainError):
    pass


class PermissionDeniedError(DomainError):
    pass
