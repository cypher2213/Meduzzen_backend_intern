"""Fix enums in company_invites

Revision ID: 684c8dbd51fe
Revises: 392336bdc249
Create Date: 2025-11-17 01:42:47.755472

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "684c8dbd51fe"
down_revision: Union[str, Sequence[str], None] = "392336bdc249"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "company_invites",
        "type",
        type_=sa.String(),
        existing_type=sa.Enum("invite", "request", name="invitation_type"),
        nullable=False,
    )
    op.alter_column(
        "company_invites",
        "status",
        type_=sa.String(),
        existing_type=sa.Enum(
            "pending", "accepted", "declined", "canceled", name="invitation_status"
        ),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "company_invites",
        "type",
        type_=sa.Enum("invite", "request", name="invitation_type"),
        nullable=False,
    )
    op.alter_column(
        "company_invites",
        "status",
        type_=sa.Enum(
            "pending", "accepted", "declined", "canceled", name="invitation_status"
        ),
        nullable=False,
    )

    op.execute("DROP TYPE IF EXISTS invitation_type")
    op.execute("DROP TYPE IF EXISTS invitation_status")
