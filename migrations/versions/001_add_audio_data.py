"""Add audio_data column to conversations table for database storage.

Revision ID: 001_add_audio_data
Revises: 
Create Date: 2026-02-19 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '001_add_audio_data'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add audio_data column to store audio bytes in database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # Fresh environments may not have ORM tables yet if migrations run before app init.
    if 'conversations' not in tables:
        return

    columns = {col['name'] for col in inspector.get_columns('conversations')}
    if 'audio_data' not in columns:
        op.add_column('conversations', sa.Column('audio_data', sa.LargeBinary(), nullable=True))


def downgrade():
    """Remove audio_data column."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if 'conversations' not in tables:
        return

    columns = {col['name'] for col in inspector.get_columns('conversations')}
    if 'audio_data' in columns:
        op.drop_column('conversations', 'audio_data')
