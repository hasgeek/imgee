"""StoredFile.no_previews

Revision ID: 5a1014061968
Revises: 1036f2d710dc
Create Date: 2013-12-30 22:40:09.773656

"""

# revision identifiers, used by Alembic.
revision = '5a1014061968'
down_revision = '1036f2d710dc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        'stored_file',
        sa.Column('no_previews', sa.Boolean(), nullable=False, server_default='False'),
    )
    op.alter_column('stored_file', 'no_previews', server_default=None)


def downgrade():
    op.drop_column('stored_file', 'no_previews')
