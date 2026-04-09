"""Compatibility alias for the quotas and cost tracking migration.

This no-op migration exists so older databases stamped with
0001_add_quotas_and_cost_tracking and deployments stamped with
0001_quotas_cost can both resolve the same migration chain.
"""

# revision identifiers, used by Alembic.
revision = '0001_add_quotas_and_cost_tracking'
down_revision = '0001_quotas_cost'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op compatibility step."""
    return


def downgrade() -> None:
    """No-op compatibility step."""
    return
