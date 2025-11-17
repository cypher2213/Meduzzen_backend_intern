"""updated role field

Revision ID: a58ab01da6b4
Revises: d797a49ab296
Create Date: 2025-11-17 20:13:50.205995

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a58ab01da6b4"
down_revision: Union[str, Sequence[str], None] = "d797a49ab296"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    role_enum = postgresql.ENUM("member", "owner", "admin", name="role_enum")
    role_enum.create(op.get_bind(), checkfirst=True)

    op.execute(
        "ALTER TABLE company_user_roles "
        "ALTER COLUMN role TYPE role_enum "
        "USING role::role_enum"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "ALTER TABLE company_user_roles "
        "ALTER COLUMN role TYPE VARCHAR "
        "USING role::text"
    )

    role_enum = postgresql.ENUM("member", "owner", "admin", name="role_enum")
    role_enum.drop(op.get_bind(), checkfirst=True)
