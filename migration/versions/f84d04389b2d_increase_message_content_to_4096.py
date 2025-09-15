"""increase message.content to 4096

Revision ID: f84d04389b2d
Revises: 3e9b3aeb5560
Create Date: 2025-09-16 02:03:38.997724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f84d04389b2d'
down_revision: Union[str, Sequence[str], None] = '3e9b3aeb5560'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("messages",	"content", type_=sa.String(length=4096), existing_type=sa.String(length=1000), existing_nullable=True)


def downgrade() -> None:
    op.alter_column("messages", "content", type_=sa.String(length=1000), existing_type=sa.String(length=4096),existing_nullable=True)
