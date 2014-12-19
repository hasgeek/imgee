"""StoredFile.orig_extn

Revision ID: 1036f2d710dc
Revises: 200442fae8bd
Create Date: 2013-12-27 23:34:51.646494

"""

# revision identifiers, used by Alembic.
revision = '1036f2d710dc'
down_revision = '200442fae8bd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('stored_file', sa.Column('orig_extn', sa.Unicode(length=15), nullable=True))


def downgrade():
    op.drop_column('stored_file', 'orig_extn')
