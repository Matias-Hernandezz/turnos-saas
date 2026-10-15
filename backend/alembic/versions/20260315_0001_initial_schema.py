"""initial schema

Revision ID: 20260315_0001
Revises:
Create Date: 2026-03-15
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "20260315_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    import models  # noqa: F401
    from sqlmodel import SQLModel

    bind = op.get_bind()
    SQLModel.metadata.create_all(bind)

    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
        op.execute(
            """
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'appointment_no_professional_overlap'
              ) THEN
                ALTER TABLE appointment
                ADD CONSTRAINT appointment_no_professional_overlap
                EXCLUDE USING gist (
                  tenant_id WITH =,
                  professional_id WITH =,
                  tstzrange(starts_at, ends_at, '[)') WITH &&
                )
                WHERE (status IN ('held', 'confirmed', 'pending_payment'));
              END IF;
            END $$;
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TABLE appointment DROP CONSTRAINT IF EXISTS appointment_no_professional_overlap"
        )
    import models  # noqa: F401
    from sqlmodel import SQLModel

    SQLModel.metadata.drop_all(bind)
