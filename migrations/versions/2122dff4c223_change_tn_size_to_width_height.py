"""change thumbnail size to width and height

Revision ID: 2122dff4c223
Revises: 4b2844325813
Create Date: 2013-10-18 18:15:47.189909

"""


from alembic import op
from sqlalchemy.sql import bindparam, column, select
import sqlalchemy as sa

from imgee.models import Thumbnail

# revision identifiers, used by Alembic.
revision = '2122dff4c223'
down_revision = '4b2844325813'


def upgrade():
    op.add_column('thumbnail', sa.Column('width', sa.Integer(), nullable=True))
    op.add_column('thumbnail', sa.Column('height', sa.Integer(), nullable=True))

    connection = op.get_bind()
    tn = Thumbnail.__table__
    result = connection.execute(select([column('id'), column('size')], from_obj=tn))
    w_h = [
        {'tnid': r.id, 'w': int(r.size.split('x')[0]), 'h': int(r.size.split('x')[1])}
        for r in result
    ]
    if len(w_h) > 0:
        updt_stmt = (
            tn.update()
            .where(tn.c.id == bindparam('tnid'))
            .values(width=bindparam('w'), height=bindparam('h'))
        )
        connection.execute(updt_stmt, w_h)


def downgrade():
    op.drop_column('thumbnail', 'height')
    op.drop_column('thumbnail', 'width')
