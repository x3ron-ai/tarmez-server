"""add sender_receiver index to message

Revision ID: 7e6e755ed457
Revises: 1775d0defdc4
Create Date: 2025-09-09 16:40:24.996058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e6e755ed457'
down_revision: Union[str, Sequence[str], None] = '1775d0defdc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	op.create_index(
		"idx_messages_sender_receiver",
		"messages",
		["sender_id", "receiver_id"]
	)


def downgrade() -> None:
	"""Downgrade schema."""
	op.drop_index(
		"idx_messages_sender_receiver",
		table_name="messages"
	)
