"""Switch to UserBase2

Revision ID: e1436ac65c6c
Revises: 5a1014061968
Create Date: 2021-11-12 12:40:21.234716

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e1436ac65c6c'
down_revision = '5a1014061968'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'user',
        sa.Column('status', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )
    op.alter_column('user', 'status', server_default=None)


def downgrade():
    op.drop_column('user', 'status')
