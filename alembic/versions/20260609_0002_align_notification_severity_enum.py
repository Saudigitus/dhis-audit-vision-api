"""align notification severity enum

Revision ID: 20260609_0002
Revises: 20260605_0001
Create Date: 2026-06-09 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260609_0002"
down_revision: Union[str, Sequence[str], None] = "20260605_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE severityenum RENAME TO severityenum_old")
    op.execute("CREATE TYPE severityenum AS ENUM ('LOW', 'MEDIUM', 'HIGH')")
    op.execute(
        """
        ALTER TABLE notification_configs
        ALTER COLUMN severity TYPE severityenum
        USING (
            CASE severity::text
                WHEN 'INFO' THEN 'LOW'
                WHEN 'WARNING' THEN 'MEDIUM'
                WHEN 'ERROR' THEN 'HIGH'
                WHEN 'CRITICAL' THEN 'HIGH'
                ELSE severity::text
            END
        )::severityenum
        """
    )
    op.execute("DROP TYPE severityenum_old")


def downgrade() -> None:
    op.execute("ALTER TYPE severityenum RENAME TO severityenum_old")
    op.execute("CREATE TYPE severityenum AS ENUM ('INFO', 'WARNING', 'ERROR', 'CRITICAL')")
    op.execute(
        """
        ALTER TABLE notification_configs
        ALTER COLUMN severity TYPE severityenum
        USING (
            CASE severity::text
                WHEN 'LOW' THEN 'INFO'
                WHEN 'MEDIUM' THEN 'WARNING'
                WHEN 'HIGH' THEN 'ERROR'
                ELSE severity::text
            END
        )::severityenum
        """
    )
    op.execute("DROP TYPE severityenum_old")
