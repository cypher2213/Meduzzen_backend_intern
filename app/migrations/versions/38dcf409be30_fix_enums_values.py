"""Fix enums values

Revision ID: 38dcf409be30
Revises: 684c8dbd51fe
Create Date: 2025-11-17 01:51:01.467427

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "38dcf409be30"
down_revision: Union[str, Sequence[str], None] = "684c8dbd51fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "company_invites",
        "type",
        type_=sa.String(),
        existing_type=postgresql.ENUM("INVITE", "REQUEST", name="invitation_type"),
        nullable=False,
    )
    op.alter_column(
        "company_invites",
        "status",
        type_=sa.String(),
        existing_type=postgresql.ENUM(
            "PENDING", "ACCEPTED", "DECLINED", "CANCELED", name="invitation_status"
        ),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "company_invites",
        "type",
        type_=postgresql.ENUM("INVITE", "REQUEST", name="invitation_type"),
        nullable=False,
    )
    op.alter_column(
        "company_invites",
        "status",
        type_=postgresql.ENUM(
            "PENDING", "ACCEPTED", "DECLINED", "CANCELED", name="invitation_status"
        ),
        nullable=False,
    )
    op.execute("DROP TYPE IF EXISTS invitation_type")
    op.execute("DROP TYPE IF EXISTS invitation_status")
