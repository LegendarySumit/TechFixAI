"""Compatibility alias for quotas migration IDs.

Use a short revision ID because PostgreSQL stores alembic_version.version_num
as varchar(32) in many existing setups.
"""

# revision identifiers, used by Alembic.
revision = '0001_quotas_cost_alias'
down_revision = '0001_quotas_cost'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op compatibility step."""
    return


def downgrade() -> None:
    """No-op compatibility step."""
    return
