"""add mimetype

Revision ID: 2c7e25599132
Revises: 347ba3ac054f
Create Date: 2013-07-08 15:52:59.918942

"""

# revision identifiers, used by Alembic.
revision = '2c7e25599132'
down_revision = '347ba3ac054f'

from alembic import op
import sqlalchemy as sa

import sys
sys.path.append('../../')
from mimetypes import guess_type
from sqlalchemy.sql import select, bindparam

from imgee.models import StoredFile


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stored_file', sa.Column('mimetype', sa.Unicode(length=32), nullable=False,
            server_default=sa.text("''")))
    op.alter_column('stored_file', 'mimetype', server_default=None)
    ### end Alembic commands ###

    connection = op.get_bind()
    sf = StoredFile.__table__
    result = connection.execute(select([sf.c.id, sf.c.title]))
    mimetypes = [dict(sfid=r[0], mimetype=guess_type(r[1])[0]) for r in result if '.' in r[1]]
    # fix for the stored file with id '3', whose title doesn't have extension
    mimetypes.append(dict(sfid=3, mimetype='image/png'))
    updt_stmt = sf.update().where(sf.c.id == bindparam('sfid')).values(mimetype=bindparam('mimetype'))
    connection.execute(updt_stmt, mimetypes)


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('stored_file', 'mimetype')
    ### end Alembic commands ###
