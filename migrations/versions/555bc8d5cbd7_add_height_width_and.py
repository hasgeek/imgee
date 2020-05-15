# -*- coding: utf-8 -*-
"""add height, width and size to stored_file

Revision ID: 555bc8d5cbd7
Revises: 2d5db2a698f6
Create Date: 2013-06-06 14:43:26.622689

"""

# revision identifiers, used by Alembic.
revision = '555bc8d5cbd7'
down_revision = '2d5db2a698f6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'stored_file', sa.Column('width', sa.Integer(), server_default=sa.text('0'))
    )
    op.add_column(
        'stored_file', sa.Column('size', sa.BigInteger(), server_default=sa.text('0'))
    )
    op.add_column(
        'stored_file', sa.Column('height', sa.Integer(), server_default=sa.text('0'))
    )
    op.alter_column('stored_file', 'width', server_default=None)
    op.alter_column('stored_file', 'size', server_default=None)
    op.alter_column('stored_file', 'height', server_default=None)


def downgrade():
    op.drop_column('stored_file', 'height')
    op.drop_column('stored_file', 'size')
    op.drop_column('stored_file', 'width')
