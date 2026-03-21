"""Add user quotas, subscription tiers, and cost tracking.

Revision ID: 0001_quotas_cost
Revises: 
Create Date: 2026-03-21

This migration is backward-compatible:
- All new columns have defaults
- No existing data is deleted
- Migration can be rolled back safely
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '0001_quotas_cost'
down_revision = '001_add_audio_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add quota and cost tracking columns to users table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # In fresh DBs, app startup may create tables after migrations.
    if 'users' not in tables:
        return

    existing_columns = {col['name'] for col in inspector.get_columns('users')}
    
    # Create subscription_tier ENUM type
    # On PostgreSQL: CREATE TYPE subscription_tier AS ENUM (...)
    # On SQLite: no ENUM support, stored as VARCHAR
    subscription_tier_enum = sa.Enum(
        'free', 'pro', 'enterprise',
        name='subscription_tier',
        native_enum=True
    )
    
    try:
        subscription_tier_enum.create(op.get_bind(), checkfirst=True)
    except Exception:
        # SQLite doesn't support native ENUM; will be VARCHAR
        pass
    
    # Add columns to users table
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Subscription tier (free, pro, enterprise)
        if 'subscription_tier' not in existing_columns:
            batch_op.add_column(
                sa.Column(
                    'subscription_tier',
                    sa.String(20),  # VARCHAR for SQLite compatibility
                    nullable=False,
                    server_default='free',
                    comment='User subscription tier: free, pro, or enterprise'
                )
            )
        
        # Monthly upload usage (reset monthly)
        if 'uploads_this_month' not in existing_columns:
            batch_op.add_column(
                sa.Column(
                    'uploads_this_month',
                    sa.Integer(),
                    nullable=False,
                    server_default='0',
                    comment='Number of voice uploads this calendar month'
                )
            )
        
        # Date of last quota reset
        if 'quota_reset_date' not in existing_columns:
            batch_op.add_column(
                sa.Column(
                    'quota_reset_date',
                    sa.DateTime(),
                    nullable=True,
                    comment='Date when monthly quota was last reset (UTC)'
                )
            )
        
        # Monthly Groq API spend in cents
        if 'groq_spend_cents_month' not in existing_columns:
            batch_op.add_column(
                sa.Column(
                    'groq_spend_cents_month',
                    sa.Integer(),
                    nullable=False,
                    server_default='0',
                    comment='Cumulative Groq API spend this month in cents'
                )
            )
        
        # Monthly cost cap in cents (per user)
        if 'monthly_cost_limit_cents' not in existing_columns:
            batch_op.add_column(
                sa.Column(
                    'monthly_cost_limit_cents',
                    sa.Integer(),
                    nullable=True,
                    comment='Monthly spend limit in cents (NULL = no limit)'
                )
            )
        
        # Exceeded quota flag (for alerts/UI)
        if 'quota_exceeded' not in existing_columns:
            batch_op.add_column(
                sa.Column(
                    'quota_exceeded',
                    sa.Boolean(),
                    nullable=False,
                    server_default='0',
                    comment='True if user exceeded uploads or spend this month'
                )
            )


def downgrade() -> None:
    """Remove quota and cost tracking columns from users table."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if 'users' not in tables:
        return

    existing_columns = {col['name'] for col in inspector.get_columns('users')}
    
    with op.batch_alter_table('users', schema=None) as batch_op:
        if 'subscription_tier' in existing_columns:
            batch_op.drop_column('subscription_tier')
        if 'uploads_this_month' in existing_columns:
            batch_op.drop_column('uploads_this_month')
        if 'quota_reset_date' in existing_columns:
            batch_op.drop_column('quota_reset_date')
        if 'groq_spend_cents_month' in existing_columns:
            batch_op.drop_column('groq_spend_cents_month')
        if 'monthly_cost_limit_cents' in existing_columns:
            batch_op.drop_column('monthly_cost_limit_cents')
        if 'quota_exceeded' in existing_columns:
            batch_op.drop_column('quota_exceeded')
    
    # Drop ENUM type (PostgreSQL only)
    try:
        op.execute('DROP TYPE IF EXISTS subscription_tier')
    except Exception:
        pass
