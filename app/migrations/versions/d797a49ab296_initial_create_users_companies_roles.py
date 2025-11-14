"""Initial create users, companies, roles

Revision ID: d797a49ab296
Revises: 08f63ea6d980
Create Date: 2025-11-14 01:47:30.034798

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d797a49ab296"
down_revision: Union[str, Sequence[str], None] = "08f63ea6d980"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("email", sa.String(), nullable=False, unique=True, index=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "companies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "company_user_roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column(
            "company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id")
        ),
        sa.Column("role", sa.String(), nullable=False, default="member"),
    )


def downgrade() -> None:
    op.drop_table("company_user_roles")
    op.drop_table("companies")
    op.drop_table("users")

    # ### end Alembic commands ###
