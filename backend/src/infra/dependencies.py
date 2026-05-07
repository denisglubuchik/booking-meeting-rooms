#  ruff: noqa: PLR6301

from dishka import (
    BaseScope,
    Component,
    Provider,
    Scope,
    make_async_container,
    provide,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import AuthConfig, DBConfig, RedisConfig, S3Config
from infra.auth.access_token import JWTAccessTokenIssuer, JWTAccessTokenVerifier
from infra.cache.service import RedisCacheService
from infra.db.repositories.booking import DBBookingsRepository
from infra.db.repositories.booking_history import DBBookingHistoryRepository
from infra.db.repositories.booking_participant import (
    DBBookingParticipantsRepository,
)
from infra.db.repositories.meeting_room import DBMeetingRoomsRepository
from infra.db.repositories.office import DBOfficesRepository
from infra.db.repositories.user import DBUsersRepository
from infra.db.uow import SQLAlchemyUOW
from infra.integrations.s3storage.s3 import S3FileStorage
from infra.interfaces.access_token import (
    AccessTokenIssuerInterface,
    AccessTokenVerifierInterface,
)
from infra.interfaces.cache import CacheInterface
from infra.interfaces.file_storage import FileStorageInterface
from infra.password_hasher import PasswordHasher
from usecases.bookings.add_participant import AddBookingParticipantUseCase
from usecases.bookings.cancel_booking import CancelBookingUseCase
from usecases.bookings.change_room import ChangeRoomBookingUseCase
from usecases.bookings.create_booking import CreateBookingUseCase
from usecases.bookings.get_all_bookings import GetAllBookingsUseCase
from usecases.bookings.get_available_rooms import GetAvailableRoomsUseCase
from usecases.bookings.get_booking_details import GetBookingDetailsUseCase
from usecases.bookings.get_my_bookings import GetMyBookingsUseCase
from usecases.bookings.get_room_bookings import GetRoomBookingsUseCase
from usecases.bookings.remove_participant import RemoveBookingParticipantUseCase
from usecases.bookings.reschedule_booking import RescheduleBookingUseCase
from usecases.interfaces.db import (
    DBBookingHistoryRepositoryInterface,
    DBBookingParticipantsRepositoryInterface,
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
    DBOfficesRepositoryInterface,
    DBUsersRepositoryInterface,
)
from usecases.interfaces.password_hasher import PasswordHasherInterface
from usecases.interfaces.uow import UoWInterface
from usecases.meeting_rooms.activate_room import ActivateRoomUseCase
from usecases.meeting_rooms.create_room import CreateRoomUseCase
from usecases.meeting_rooms.deactivate_room import DeactivateRoomUseCase
from usecases.meeting_rooms.get_all_rooms import GetAllRoomsUseCase
from usecases.meeting_rooms.get_office_rooms import GetOfficeRoomsUseCase
from usecases.meeting_rooms.get_room_details import GetRoomDetailsUseCase
from usecases.meeting_rooms.image_ops import (
    DeleteRoomImageUseCase,
    UploadRoomImageUseCase,
)
from usecases.meeting_rooms.update_room import UpdateRoomUseCase
from usecases.offices.activate_office import ActivateOfficeUseCase
from usecases.offices.create_office import CreateOfficeUseCase
from usecases.offices.deactivate_office import DeactivateOfficeUseCase
from usecases.offices.get_office_details import GetOfficeDetailsUseCase
from usecases.offices.get_offices import GetOfficesUseCase
from usecases.offices.image_ops import (
    DeleteOfficeImageUseCase,
    UploadOfficeImageUseCase,
)
from usecases.offices.update_office import UpdateOfficeUseCase
from usecases.user.activate_user import ActivateUserUseCase
from usecases.user.change_role import ChangeUserRoleUseCase
from usecases.user.create_user import CreateUserUseCase
from usecases.user.deactivate_user import DeactivateUserUseCase
from usecases.user.get_user_details import GetUserDetailsUseCase
from usecases.user.get_users import GetUsersUseCase
from usecases.user.login_user import LoginUserUseCase
from usecases.user.lookup_users import LookupUsersUseCase
from usecases.user.update_user import UpdateUserUseCase

db_config = DBConfig()
redis_config = RedisConfig()
auth_config = AuthConfig()
s3_config = S3Config()


class DependencyProvider(Provider):
    def __init__(
        self,
        db_config: DBConfig,
        redis_config: RedisConfig,
        auth_config: AuthConfig,
        s3_config: S3Config,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.db_config = db_config
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
    def redis_cache(self) -> CacheInterface:
        return RedisCacheService(self.redis_config)

    @provide(scope=Scope.APP)
    def hasher(self) -> PasswordHasherInterface:
        return PasswordHasher()

    @provide(scope=Scope.APP)
    def access_token_issuer(
        self,
        auth_settings: AuthConfig,
    ) -> AccessTokenIssuerInterface:
        return JWTAccessTokenIssuer(config=auth_settings)

    @provide(scope=Scope.APP)
    def access_token_verifier(
        self,
        auth_settings: AuthConfig,
    ) -> AccessTokenVerifierInterface:
        return JWTAccessTokenVerifier(config=auth_settings)

    @provide(scope=Scope.APP)
    def db_engine(self) -> AsyncEngine:
        return create_async_engine(
            self.db_config.DATABASE_URL,
            echo=False,
            pool_size=7,
            max_overflow=20,
            pool_pre_ping=True,
        )

    @provide(scope=Scope.APP)
    def session_factory(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )

    @provide(scope=Scope.REQUEST)
    def sql_alchemy_uow(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheInterface,
    ) -> UoWInterface:
        return SQLAlchemyUOW(session_factory=session_factory, cache=cache)

    @provide(scope=Scope.REQUEST)
    def db_users_repository(
        self,
        session_factory: async_sessionmaker[AsyncSession],
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
        session_factory: async_sessionmaker[AsyncSession],
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
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheInterface,
    ) -> DBMeetingRoomsRepositoryInterface:
        return DBMeetingRoomsRepository(
            session=None,
            session_factory=session_factory,
            cache=cache,
        )

    @provide(scope=Scope.REQUEST)
    def db_bookings_repository(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> DBBookingsRepositoryInterface:
        return DBBookingsRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_booking_history_repository(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> DBBookingHistoryRepositoryInterface:
        return DBBookingHistoryRepository(
            session=None,
            session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_booking_participants_repository(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> DBBookingParticipantsRepositoryInterface:
        return DBBookingParticipantsRepository(
            session=None,
            session_factory=session_factory,
        )

    activate_office_uc = provide(ActivateOfficeUseCase)
    create_office_uc = provide(CreateOfficeUseCase)
    deactivate_office_uc = provide(DeactivateOfficeUseCase)
    get_office_uc = provide(GetOfficeDetailsUseCase)
    get_offices_uc = provide(GetOfficesUseCase)
    update_office_uc = provide(UpdateOfficeUseCase)
    upload_office_image_uc = provide(UploadOfficeImageUseCase)
    delete_office_image_uc = provide(DeleteOfficeImageUseCase)

    activate_room_uc = provide(ActivateRoomUseCase)
    create_room_uc = provide(CreateRoomUseCase)
    deactivate_room_uc = provide(DeactivateRoomUseCase)
    get_room_uc = provide(GetRoomDetailsUseCase)
    update_room_uc = provide(UpdateRoomUseCase)
    get_all_rooms_uc = provide(GetAllRoomsUseCase)
    get_office_rooms_uc = provide(GetOfficeRoomsUseCase)
    upload_room_image_uc = provide(UploadRoomImageUseCase)
    delete_room_image_uc = provide(DeleteRoomImageUseCase)

    activate_user_uc = provide(ActivateUserUseCase)
    create_user_uc = provide(CreateUserUseCase)
    login_user_uc = provide(LoginUserUseCase)
    deactivate_user_uc = provide(DeactivateUserUseCase)
    change_user_role_uc = provide(ChangeUserRoleUseCase)
    get_user_uc = provide(GetUserDetailsUseCase)
    update_user_uc = provide(UpdateUserUseCase)
    get_users_uc = provide(GetUsersUseCase)
    lookup_users_uc = provide(LookupUsersUseCase)

    cancel_booking_uc = provide(CancelBookingUseCase)
    add_booking_participant_uc = provide(AddBookingParticipantUseCase)
    create_booking_uc = provide(CreateBookingUseCase)
    get_all_bookings_uc = provide(GetAllBookingsUseCase)
    get_available_rooms_uc = provide(GetAvailableRoomsUseCase)
    get_booking_uc = provide(GetBookingDetailsUseCase)
    get_my_bookings_uc = provide(GetMyBookingsUseCase)
    get_room_bookings_uc = provide(GetRoomBookingsUseCase)
    remove_booking_participant_uc = provide(RemoveBookingParticipantUseCase)
    reschedule_booking_uc = provide(RescheduleBookingUseCase)
    change_room_booking_uc = provide(ChangeRoomBookingUseCase)


container = make_async_container(
    DependencyProvider(
        db_config=db_config,
        redis_config=redis_config,
        auth_config=auth_config,
        s3_config=s3_config,
        scope=Scope.REQUEST,
    ),
)
