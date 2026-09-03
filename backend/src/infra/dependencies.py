#  ruff: noqa: PLR6301
from collections.abc import AsyncIterator

from dishka import (
    BaseScope,
    Component,
    Provider,
    Scope,
    make_async_container,
    provide,
)

from core.config import (
    AuthConfig,
    DBConfig,
    EmailConfig,
    RedisConfig,
    S3Config,
    WorkerConfig,
)
from infra.argon_hasher import ArgonHasher
from infra.auth.tokens import JWTTokenService
from infra.cache.service import RedisCacheService
from infra.db.provider import (
    DatabaseProvider,
    ROSessionFactory,
    RWSessionFactory,
)
from infra.db.queries.booking_history import BookingHistoryQueryRepository
from infra.db.queries.bookings import BookingsQueryRepository
from infra.db.queries.offices import OfficesQueryRepository
from infra.db.queries.rooms import RoomsQueryRepository
from infra.db.queries.user_sessions import UserSessionsQueryRepository
from infra.db.queries.users import UsersQueryRepository
from infra.db.repositories.booking import DBBookingsRepository
from infra.db.repositories.booking_history import DBBookingHistoryRepository
from infra.db.repositories.booking_participant import (
    DBBookingParticipantsRepository,
)
from infra.db.repositories.meeting_room import DBMeetingRoomsRepository
from infra.db.repositories.notification import DBNotificationRepository
from infra.db.repositories.notification_dispatch import (
    DBNotificationDispatchRepository,
)
from infra.db.repositories.office import DBOfficesRepository
from infra.db.repositories.user import DBUsersRepository
from infra.db.uow import SQLAlchemyUOW
from infra.integrations.notifications.email import (
    SMTPEmailNotificationSender,
)
from infra.integrations.s3storage.s3 import S3FileStorage
from infra.interfaces.cache import CacheInterface
from infra.interfaces.file_storage import FileStorageInterface
from infra.interfaces.jwt_tokens import JWTTokenServiceInterface
from usecases.commands.auth.login import LoginCommandHandler
from usecases.commands.auth.logout import LogoutCommandHandler
from usecases.commands.auth.refresh_tokens import RefreshTokensCommandHandler
from usecases.commands.auth.revoke_user_session import (
    RevokeUserSessionCommandHandler,
)
from usecases.commands.bookings.add_participant import (
    AddBookingParticipantCommandHandler,
)
from usecases.commands.bookings.cancel_booking import (
    CancelBookingCommandHandler,
)
from usecases.commands.bookings.change_room import (
    ChangeRoomBookingCommandHandler,
)
from usecases.commands.bookings.complete_expired_bookings import (
    CompleteExpiredBookingsCommandHandler,
)
from usecases.commands.bookings.create_booking import (
    CreateBookingCommandHandler,
)
from usecases.commands.bookings.remove_participant import (
    RemoveBookingParticipantCommandHandler,
)
from usecases.commands.bookings.reschedule_booking import (
    RescheduleBookingCommandHandler,
)
from usecases.commands.offices.activate_office import (
    ActivateOfficeCommandHandler,
)
from usecases.commands.offices.create_office import CreateOfficeCommandHandler
from usecases.commands.offices.deactivate_office import (
    DeactivateOfficeCommandHandler,
)
from usecases.commands.offices.image_ops import (
    DeleteOfficeImageCommandHandler,
    UploadOfficeImageCommandHandler,
)
from usecases.commands.offices.update_office import UpdateOfficeCommandHandler
from usecases.commands.rooms.activate_room import ActivateRoomCommandHandler
from usecases.commands.rooms.create_room import CreateRoomCommandHandler
from usecases.commands.rooms.deactivate_room import DeactivateRoomCommandHandler
from usecases.commands.rooms.image_ops import (
    DeleteRoomImageCommandHandler,
    UploadRoomImageCommandHandler,
)
from usecases.commands.rooms.update_room import UpdateRoomCommandHandler
from usecases.commands.users.activate_user import ActivateUserCommandHandler
from usecases.commands.users.change_role import ChangeUserRoleCommandHandler
from usecases.commands.users.create_user import CreateUserCommandHandler
from usecases.commands.users.deactivate_user import DeactivateUserCommandHandler
from usecases.commands.users.update_user import UpdateUserCommandHandler
from usecases.interfaces.commands import (
    OfficesCommandRepositoryInterface,
    RoomsCommandRepositoryInterface,
    UsersCommandRepositoryInterface,
)
from usecases.interfaces.db import (
    DBBookingHistoryRepositoryInterface,
    DBBookingParticipantsRepositoryInterface,
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
    DBOfficesRepositoryInterface,
    DBUsersRepositoryInterface,
    NotificationDispatchRepositoryInterface,
    NotificationRepositoryInterface,
)
from usecases.interfaces.hasher import HasherInterface
from usecases.interfaces.notifications import (
    NotificationSenderInterface,
    NotificationTemplateRendererInterface,
)
from usecases.interfaces.queries import (
    BookingHistoryQueryInterface,
    BookingsQueryInterface,
    ConsistentBookingsQueryInterface,
    ConsistentUserSessionsQueryInterface,
    ConsistentUsersQueryInterface,
    OfficesQueryInterface,
    RoomsQueryInterface,
    UserSessionsQueryInterface,
    UsersQueryInterface,
)
from usecases.interfaces.uow import UoWInterface
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)
from usecases.notifications.process_dispatch import (
    ProcessNotificationDispatchUseCase,
)
from usecases.notifications.select_reminders import (
    SelectBookingStartRemindersUseCase,
)
from usecases.notifications.template_renderer import (
    NotificationTemplateRenderer,
)
from usecases.queries.bookings.get_all_bookings import (
    GetAllBookingsQueryHandler,
)
from usecases.queries.bookings.get_available_rooms import (
    GetAvailableRoomsQueryHandler,
)
from usecases.queries.bookings.get_booking_details import (
    GetBookingDetailsQueryHandler,
)
from usecases.queries.bookings.get_booking_history import (
    GetBookingHistoryQueryHandler,
)
from usecases.queries.bookings.get_room_bookings import (
    GetRoomBookingsQueryHandler,
)
from usecases.queries.bookings.get_user_bookings import (
    GetUserBookingsQueryHandler,
)
from usecases.queries.offices.get_office_details import (
    GetOfficeDetailsQueryHandler,
)
from usecases.queries.offices.get_offices import GetOfficesQueryHandler
from usecases.queries.rooms.get_all_rooms import GetAllRoomsQueryHandler
from usecases.queries.rooms.get_office_rooms import GetOfficeRoomsQueryHandler
from usecases.queries.rooms.get_room_details import GetRoomDetailsQueryHandler
from usecases.queries.users.get_user_details import GetUserDetailsQueryHandler
from usecases.queries.users.get_user_sessions import GetUserSessionsQueryHandler
from usecases.queries.users.get_users import GetUsersQueryHandler
from usecases.queries.users.lookup_users import LookupUsersQueryHandler

db_config = DBConfig()
redis_config = RedisConfig()
auth_config = AuthConfig()
s3_config = S3Config()
email_config = EmailConfig()
worker_config = WorkerConfig()


class DependencyProvider(Provider):
    def __init__(
        self,
        redis_config: RedisConfig,
        auth_config: AuthConfig,
        s3_config: S3Config,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.redis_config = redis_config
        self.auth_config = auth_config
        self.s3_config = s3_config

    @provide(scope=Scope.APP)
    def auth_settings(self) -> AuthConfig:
        return self.auth_config

    @provide(scope=Scope.APP)
    def s3_settings(self) -> S3Config:
        return self.s3_config

    @provide(scope=Scope.APP)
    def file_storage(
        self,
        s3_settings: S3Config,
        cache: CacheInterface,
    ) -> FileStorageInterface:
        return S3FileStorage(config=s3_settings, cache=cache)

    @provide(scope=Scope.APP)
    async def redis_cache(self) -> AsyncIterator[CacheInterface]:
        cache = RedisCacheService(self.redis_config)
        try:
            yield cache
        finally:
            await cache.close()

    @provide(scope=Scope.APP)
    def hasher(self) -> HasherInterface:
        return ArgonHasher()

    @provide(scope=Scope.APP)
    def jwt_tokens(
        self,
        auth_settings: AuthConfig,
    ) -> JWTTokenServiceInterface:
        return JWTTokenService(config=auth_settings)

    @provide(scope=Scope.REQUEST)
    def sql_alchemy_uow(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> UoWInterface:
        return SQLAlchemyUOW(session_factory=session_factory, cache=cache)

    @provide(scope=Scope.REQUEST)
    def db_users_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> DBUsersRepositoryInterface:
        return DBUsersRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def db_offices_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> DBOfficesRepositoryInterface:
        return DBOfficesRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def db_rooms_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> DBMeetingRoomsRepositoryInterface:
        return DBMeetingRoomsRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def offices_command_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> OfficesCommandRepositoryInterface:
        return DBOfficesRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def rooms_command_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> RoomsCommandRepositoryInterface:
        return DBMeetingRoomsRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def users_command_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> UsersCommandRepositoryInterface:
        return DBUsersRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def offices_query_repository(
        self,
        session_factory: ROSessionFactory,
        cache: CacheInterface,
    ) -> OfficesQueryInterface:
        return OfficesQueryRepository(
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def rooms_query_repository(
        self,
        session_factory: ROSessionFactory,
        cache: CacheInterface,
    ) -> RoomsQueryInterface:
        return RoomsQueryRepository(
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def users_query_repository(
        self,
        session_factory: ROSessionFactory,
        cache: CacheInterface,
    ) -> UsersQueryInterface:
        return UsersQueryRepository(
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def consistent_users_query_repository(
        self,
        session_factory: RWSessionFactory,
        cache: CacheInterface,
    ) -> ConsistentUsersQueryInterface:
        return UsersQueryRepository(
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def user_sessions_query_repository(
        self,
        session_factory: ROSessionFactory,
    ) -> UserSessionsQueryInterface:
        return UserSessionsQueryRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def consistent_user_sessions_query_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> ConsistentUserSessionsQueryInterface:
        return UserSessionsQueryRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def bookings_query_repository(
        self,
        session_factory: ROSessionFactory,
    ) -> BookingsQueryInterface:
        return BookingsQueryRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def consistent_bookings_query_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> ConsistentBookingsQueryInterface:
        return BookingsQueryRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def booking_history_query_repository(
        self,
        session_factory: ROSessionFactory,
    ) -> BookingHistoryQueryInterface:
        return BookingHistoryQueryRepository(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def db_bookings_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> DBBookingsRepositoryInterface:
        return DBBookingsRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_booking_history_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> DBBookingHistoryRepositoryInterface:
        return DBBookingHistoryRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_booking_participants_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> DBBookingParticipantsRepositoryInterface:
        return DBBookingParticipantsRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_notifications_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> NotificationRepositoryInterface:
        return DBNotificationRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_notification_dispatch_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> NotificationDispatchRepositoryInterface:
        return DBNotificationDispatchRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def notification_template_renderer(
        self,
    ) -> NotificationTemplateRendererInterface:
        return NotificationTemplateRenderer()

    create_notification_dispatch_uc = provide(CreateNotificationDispatchUseCase)

    activate_office_handler = provide(ActivateOfficeCommandHandler)
    create_office_handler = provide(CreateOfficeCommandHandler)
    deactivate_office_handler = provide(DeactivateOfficeCommandHandler)
    get_office_handler = provide(GetOfficeDetailsQueryHandler)
    get_offices_handler = provide(GetOfficesQueryHandler)
    update_office_handler = provide(UpdateOfficeCommandHandler)
    upload_office_image_handler = provide(UploadOfficeImageCommandHandler)
    delete_office_image_handler = provide(DeleteOfficeImageCommandHandler)

    activate_room_handler = provide(ActivateRoomCommandHandler)
    create_room_handler = provide(CreateRoomCommandHandler)
    deactivate_room_handler = provide(DeactivateRoomCommandHandler)
    get_room_handler = provide(GetRoomDetailsQueryHandler)
    update_room_handler = provide(UpdateRoomCommandHandler)
    get_all_rooms_handler = provide(GetAllRoomsQueryHandler)
    get_office_rooms_handler = provide(GetOfficeRoomsQueryHandler)
    upload_room_image_handler = provide(UploadRoomImageCommandHandler)
    delete_room_image_handler = provide(DeleteRoomImageCommandHandler)

    activate_user_handler = provide(ActivateUserCommandHandler)
    create_user_handler = provide(CreateUserCommandHandler)
    deactivate_user_handler = provide(DeactivateUserCommandHandler)
    change_user_role_handler = provide(ChangeUserRoleCommandHandler)
    get_user_handler = provide(GetUserDetailsQueryHandler)
    update_user_handler = provide(UpdateUserCommandHandler)
    get_users_handler = provide(GetUsersQueryHandler)
    lookup_users_handler = provide(LookupUsersQueryHandler)
    login_handler = provide(LoginCommandHandler)
    refresh_tokens_handler = provide(RefreshTokensCommandHandler)
    logout_handler = provide(LogoutCommandHandler)
    get_user_sessions_handler = provide(GetUserSessionsQueryHandler)
    revoke_user_session_handler = provide(RevokeUserSessionCommandHandler)

    cancel_booking_handler = provide(CancelBookingCommandHandler)
    add_booking_participant_handler = provide(
        AddBookingParticipantCommandHandler,
    )
    create_booking_handler = provide(CreateBookingCommandHandler)
    get_all_bookings_handler = provide(GetAllBookingsQueryHandler)
    get_available_rooms_handler = provide(GetAvailableRoomsQueryHandler)
    get_booking_handler = provide(GetBookingDetailsQueryHandler)
    get_booking_history_handler = provide(GetBookingHistoryQueryHandler)
    get_user_bookings_handler = provide(GetUserBookingsQueryHandler)
    get_room_bookings_handler = provide(GetRoomBookingsQueryHandler)
    remove_booking_participant_handler = provide(
        RemoveBookingParticipantCommandHandler,
    )
    reschedule_booking_handler = provide(RescheduleBookingCommandHandler)
    change_room_booking_handler = provide(ChangeRoomBookingCommandHandler)


container = make_async_container(
    DatabaseProvider(db_config=db_config),
    DependencyProvider(
        redis_config=redis_config,
        auth_config=auth_config,
        s3_config=s3_config,
        scope=Scope.REQUEST,
    ),
)


class WorkerDependencyProvider(Provider):
    def __init__(
        self,
        email_config: EmailConfig,
        worker_config: WorkerConfig,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.email_config = email_config
        self.worker_config = worker_config

    @provide(scope=Scope.REQUEST)
    def sql_alchemy_uow(
        self,
        session_factory: RWSessionFactory,
    ) -> UoWInterface:
        return SQLAlchemyUOW(session_factory=session_factory, cache=None)

    @provide(scope=Scope.REQUEST)
    def db_notification_dispatch_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> NotificationDispatchRepositoryInterface:
        return DBNotificationDispatchRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.APP)
    def email_settings(self) -> EmailConfig:
        return self.email_config

    @provide(scope=Scope.APP)
    def worker_settings(self) -> WorkerConfig:
        return self.worker_config

    @provide(scope=Scope.REQUEST)
    def db_bookings_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> DBBookingsRepositoryInterface:
        return DBBookingsRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_users_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> DBUsersRepositoryInterface:
        return DBUsersRepository(
            session=None,
            session_factory=session_factory,
            cache=None,
        )

    @provide(scope=Scope.REQUEST)
    def db_rooms_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> DBMeetingRoomsRepositoryInterface:
        return DBMeetingRoomsRepository(
            session=None,
            session_factory=session_factory,
            cache=None,
        )

    @provide(scope=Scope.REQUEST)
    def db_notifications_repository(
        self,
        session_factory: RWSessionFactory,
    ) -> NotificationRepositoryInterface:
        return DBNotificationRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def notification_template_renderer(
        self,
    ) -> NotificationTemplateRendererInterface:
        return NotificationTemplateRenderer()

    create_notification_dispatch_uc = provide(CreateNotificationDispatchUseCase)

    @provide(scope=Scope.APP)
    def email_notification_sender(
        self,
        email_settings: EmailConfig,
    ) -> NotificationSenderInterface:
        return SMTPEmailNotificationSender(config=email_settings)

    @provide(scope=Scope.APP)
    def notification_senders(
        self,
        email_settings: EmailConfig,
        email_notification_sender: NotificationSenderInterface,
    ) -> list[NotificationSenderInterface]:
        if not email_settings.EMAIL_ENABLED:
            return []
        return [
            email_notification_sender,
        ]

    @provide(scope=Scope.REQUEST)
    def process_notification_dispatch_uc(
        self,
        dispatch_repo: NotificationDispatchRepositoryInterface,
        notification_senders: list[NotificationSenderInterface],
        worker_settings: WorkerConfig,
    ) -> ProcessNotificationDispatchUseCase:
        return ProcessNotificationDispatchUseCase(
            dispatch_repo=dispatch_repo,
            senders=notification_senders,
            max_attempts=worker_settings.DISPATCH_MAX_ATTEMPTS,
            batch_size=100,
            retry_base_seconds=worker_settings.DISPATCH_RETRY_BASE_SECONDS,
            retry_max_backoff_seconds=(
                worker_settings.DISPATCH_RETRY_MAX_BACKOFF_SECONDS
            ),
        )

    select_booking_start_reminders_uc = provide(
        SelectBookingStartRemindersUseCase,
    )
    complete_expired_bookings_handler = provide(
        CompleteExpiredBookingsCommandHandler,
    )


worker_container = make_async_container(
    DatabaseProvider(db_config=db_config),
    WorkerDependencyProvider(
        email_config=email_config,
        worker_config=worker_config,
        scope=Scope.REQUEST,
    ),
)
