"""fix_try_role

Revision ID: 39b6699a0773
Revises: 3be00efbf980
Create Date: 2025-11-17 20:50:37.627322

"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "39b6699a0773"
down_revision: Union[str, Sequence[str], None] = "a58ab01da6b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE company_user_roles
        ALTER COLUMN role TYPE role_enum
        USING LOWER(role::text)::role_enum;
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "ALTER TABLE company_user_roles ALTER COLUMN role TYPE VARCHAR USING role::text;"
    )
