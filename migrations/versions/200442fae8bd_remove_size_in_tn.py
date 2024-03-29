"""remove size column from thumnail table

Revision ID: 200442fae8bd
Revises: 2122dff4c223
Create Date: 2013-10-18 18:55:13.526165

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '200442fae8bd'
down_revision = '2122dff4c223'


def upgrade():
    op.drop_column('thumbnail', 'size')


def downgrade():
    op.add_column(
        'thumbnail', sa.Column('size', sa.VARCHAR(length=100), nullable=False)
    )
