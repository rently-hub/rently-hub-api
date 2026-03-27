"""Add platform_source to rental

Revision ID: 91f6229a677b
Revises: 1409328d54fc
Create Date: 2026-03-25 01:56:43.163156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91f6229a677b'
down_revision: Union[str, Sequence[str], None] = '1409328d54fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('rentals', sa.Column('platform_source', sa.String(length=50), server_default='Direto', nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('rentals', 'platform_source')
