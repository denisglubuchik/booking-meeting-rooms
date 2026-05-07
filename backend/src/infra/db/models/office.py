from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.office import Office
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.meeting_room import MeetingRoomModel


class OfficeModel(Base):
    __tablename__ = "offices"

    name: Mapped[str] = mapped_column(String(255), unique=True)
    city: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(String(255))
    image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    rooms: Mapped[list["MeetingRoomModel"]] = relationship(
        back_populates="office",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> Office:
        return Office(
            id=self.id,
            name=self.name,
            city=self.city,
            address=self.address,
            image_key=self.image_key,
            is_active=self.is_active,
        )

    @classmethod
    def from_domain(cls, office: Office) -> "OfficeModel":
        return cls(
            id=office.id,
            name=office.name,
            city=office.city,
            address=office.address,
            image_key=office.image_key,
            is_active=office.is_active,
        )
