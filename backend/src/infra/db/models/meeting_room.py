from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.meeting_room import MeetingRoom
from infra.db.models.base import Base

if TYPE_CHECKING:
    from infra.db.models.booking import BookingModel
    from infra.db.models.office import OfficeModel


class MeetingRoomModel(Base):
    __tablename__ = "meeting_rooms"

    office_id: Mapped[UUID] = mapped_column(
        ForeignKey("offices.id", ondelete="CASCADE"),
        index=True,
    )
    floor: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    capacity: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    equipment: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    office: Mapped["OfficeModel"] = relationship(back_populates="rooms")
    bookings: Mapped[list["BookingModel"]] = relationship(
        back_populates="room",
        cascade="all, delete-orphan",
    )

    def to_domain(self) -> MeetingRoom:
        return MeetingRoom(
            id=self.id,
            office_id=self.office_id,
            floor=self.floor,
            name=self.name,
            capacity=self.capacity,
            description=self.description,
            equipment=self.equipment,
            is_active=self.is_active,
        )

    @classmethod
    def from_domain(cls, meeting_room: MeetingRoom) -> "MeetingRoomModel":
        return cls(
            id=meeting_room.id,
            office_id=meeting_room.office_id,
            floor=meeting_room.floor,
            name=meeting_room.name,
            capacity=meeting_room.capacity,
            description=meeting_room.description,
            equipment=meeting_room.equipment,
            is_active=meeting_room.is_active,
        )
