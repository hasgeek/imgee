"""Timestamp with timezone.

Revision ID: 71acbde6c980
Revises: e1436ac65c6c
Create Date: 2024-05-27 11:53:33.653891

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '71acbde6c980'
down_revision = 'e1436ac65c6c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('label', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'updated_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table('profile', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'updated_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table('stored_file', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'updated_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table('thumbnail', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'updated_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'created_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'updated_at',
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.TIMESTAMP(timezone=True),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column(
            'updated_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'created_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table('thumbnail', schema=None) as batch_op:
        batch_op.alter_column(
            'updated_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'created_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table('stored_file', schema=None) as batch_op:
        batch_op.alter_column(
            'updated_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'created_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table('profile', schema=None) as batch_op:
        batch_op.alter_column(
            'updated_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'created_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table('label', schema=None) as batch_op:
        batch_op.alter_column(
            'updated_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'created_at',
            existing_type=sa.TIMESTAMP(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=False,
        )
