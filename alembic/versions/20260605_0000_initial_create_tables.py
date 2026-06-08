"""initial create tables

Revision ID: 20260605_0000
Revises: 
Create Date: 2026-06-05 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260605_0000"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    # Create notification_configs table
    op.create_table(
        "notification_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("objectType", sa.String(), nullable=False),
        sa.Column("action", sa.Enum("CREATE", "UPDATE", "DELETE", name="actionenum"), nullable=False),
        sa.Column("severity", sa.Enum("INFO", "WARNING", "ERROR", "CRITICAL", name="severityenum"), nullable=False),
        sa.Column("messageTemplate", sa.String(), nullable=False),
        sa.Column("recipients", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create audit table
    op.create_table(
        "audit",
        sa.Column("id", sa.String(length=11), nullable=False),
        sa.Column("auditType", sa.Enum("CREATE", "UPDATE", "DELETE", "READ", name="audittype"), nullable=False),
        sa.Column("auditScope", sa.Enum("METADATA", "TRACKER", "AGGREGATE", name="auditscope"), nullable=False),
        sa.Column("klass", sa.Text(), nullable=False),
        sa.Column("attributes", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("data", sa.LargeBinary(), nullable=True),
        sa.Column("createdBy", sa.String(), nullable=False),
        sa.Column("uid", sa.String(), nullable=True),
        sa.Column("code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create audit_object table
    op.create_table(
        "audit_object",
        sa.Column("id", sa.String(length=11), nullable=False),
        sa.Column("auditId", sa.String(length=11), nullable=False),
        sa.Column("objectId", sa.String(), nullable=False),
        sa.Column("objectData", sa.JSON(), nullable=False),
        sa.Column("auditScope", sa.Enum("METADATA", "TRACKER", "AGGREGATE", name="auditscope"), nullable=False),
        sa.Column("auditType", sa.Enum("CREATE", "UPDATE", "DELETE", "READ", name="audittype"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_object")
    op.drop_table("audit")
    op.drop_table("notification_configs")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE actionenum")
    op.execute("DROP TYPE severityenum")
    op.execute("DROP TYPE audittype")
    op.execute("DROP TYPE auditscope")
