"""Add audio_data column to conversations table for database storage.

Revision ID: 001_add_audio_data
Revises: 
Create Date: 2026-02-19 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_audio_data'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add audio_data column to store audio bytes in database."""
    op.add_column('conversations', sa.Column('audio_data', sa.LargeBinary(), nullable=True))


def downgrade():
    """Remove audio_data column."""
    op.drop_column('conversations', 'audio_data')
