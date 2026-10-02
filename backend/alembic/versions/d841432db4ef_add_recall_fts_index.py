"""add recall FTS index

Revision ID: d841432db4ef
Revises: 82ed0c080c0c
Create Date: 2026-10-01 19:06:15.562675

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd841432db4ef'
down_revision: Union[str, Sequence[str], None] = '82ed0c080c0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
