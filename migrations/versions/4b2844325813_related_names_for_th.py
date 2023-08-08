"""related names for thumbnails

Revision ID: 4b2844325813
Revises: 2c7e25599132
Create Date: 2013-07-08 21:25:41.892730

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4b2844325813'
down_revision = '2c7e25599132'


def upgrade():
    op.alter_column(
        'thumbnail',
        'name',
        existing_type=sa.VARCHAR(length=32),
        type_=sa.Unicode(length=64),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        'thumbnail',
        'name',
        existing_type=sa.Unicode(length=64),
        type_=sa.VARCHAR(length=32),
        existing_nullable=False,
    )
