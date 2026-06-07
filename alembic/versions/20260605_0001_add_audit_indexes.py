"""add audit query indexes

Revision ID: 20260605_0001
Revises:
Create Date: 2026-06-05 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "20260605_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_audit_auditType", "audit", ["auditType"], unique=False)
    op.create_index("ix_audit_auditScope", "audit", ["auditScope"], unique=False)
    op.create_index("ix_audit_klass", "audit", ["klass"], unique=False)
    op.create_index("ix_audit_createdBy", "audit", ["createdBy"], unique=False)
    op.create_index("ix_audit_uid", "audit", ["uid"], unique=False)
    op.create_index("ix_audit_code", "audit", ["code"], unique=False)
    op.create_index("ix_audit_object_auditId", "audit_object", ["auditId"], unique=False)
    op.create_index("ix_audit_object_objectId", "audit_object", ["objectId"], unique=False)
    op.create_index("ix_audit_object_auditScope", "audit_object", ["auditScope"], unique=False)
    op.create_index("ix_audit_object_auditType", "audit_object", ["auditType"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_object_auditType", table_name="audit_object")
    op.drop_index("ix_audit_object_auditScope", table_name="audit_object")
    op.drop_index("ix_audit_object_objectId", table_name="audit_object")
    op.drop_index("ix_audit_object_auditId", table_name="audit_object")
    op.drop_index("ix_audit_code", table_name="audit")
    op.drop_index("ix_audit_uid", table_name="audit")
    op.drop_index("ix_audit_createdBy", table_name="audit")
    op.drop_index("ix_audit_klass", table_name="audit")
    op.drop_index("ix_audit_auditScope", table_name="audit")
    op.drop_index("ix_audit_auditType", table_name="audit")
