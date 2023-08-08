"""add mimetype

Revision ID: 2c7e25599132
Revises: 347ba3ac054f
Create Date: 2013-07-08 15:52:59.918942

"""

from mimetypes import guess_type

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import bindparam, select

from imgee.models import StoredFile

# revision identifiers, used by Alembic.
revision = '2c7e25599132'
down_revision = '347ba3ac054f'


def upgrade():
    op.add_column(
        'stored_file',
        sa.Column(
            'mimetype',
            sa.Unicode(length=32),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )
    op.alter_column('stored_file', 'mimetype', server_default=None)

    connection = op.get_bind()
    sf = StoredFile.__table__
    result = connection.execute(select([sf.c.id, sf.c.title]))
    mimetypes = [{'sfid': r[0], 'mimetype': guess_type(r[1])[0]} for r in result]
    if len(mimetypes) > 0:
        updt_stmt = (
            sf.update()
            .where(sf.c.id == bindparam('sfid'))
            .values(mimetype=bindparam('mimetype'))
        )
        connection.execute(updt_stmt, mimetypes)


def downgrade():
    op.drop_column('stored_file', 'mimetype')
