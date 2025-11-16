from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.timestamp_mixin import TimestampMixin
from app.models.uuid_mixin import UUIDMixin

if TYPE_CHECKING:
    from app.models.company_model import CompanyModel
    from app.models.user_model import UserModel


class InviteType(str, enum.Enum):
    INVITE = "invite"
    REQUEST = "request"


class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    CANCELED = "canceled"


class CompanyInvitesModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "company_invites"
    company_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    invited_by_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    invited_user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    type: Mapped[InviteType] = mapped_column(
        Enum(
            InviteType,
            name="invitation_type",
            native_enum=False,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )
    status: Mapped[InviteStatus] = mapped_column(
        Enum(
            InviteStatus,
            name="invitation_status",
            native_enum=False,
            values_callable=lambda e: [i.value for i in e],
        ),
        nullable=False,
    )
    company: Mapped["CompanyModel"] = relationship("CompanyModel")
    invited_by: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[invited_by_id]
    )
    invited_user: Mapped["UserModel"] = relationship(
        "UserModel", foreign_keys=[invited_user_id]
    )
