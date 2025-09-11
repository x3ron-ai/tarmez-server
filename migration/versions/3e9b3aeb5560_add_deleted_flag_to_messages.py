"""add deleted flag to messages

Revision ID: 3e9b3aeb5560
Revises: 7e6e755ed457
Create Date: 2025-09-11 03:19:40.459859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e9b3aeb5560'
down_revision: Union[str, Sequence[str], None] = '7e6e755ed457'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("messages", sa.Column("deleted", sa.Boolean(), nullable=False, server_default="0"))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("messages", "deleted")
    pass
