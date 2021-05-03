"""update image attrs

Revision ID: 347ba3ac054f
Revises: 555bc8d5cbd7
Create Date: 2013-06-06 22:44:36.482379

"""

# revision identifiers, used by Alembic.
revision = '347ba3ac054f'
down_revision = '555bc8d5cbd7'


from glob import glob
import os.path
import sys

from alembic import op
from sqlalchemy.orm import load_only
from sqlalchemy.orm.session import sessionmaker

from imgee.models import StoredFile
from imgee.storage import get_width_height, path_for

sys.path.append('../../')


def upgrade():
    connection = op.get_bind()
    Session = sessionmaker(bind=connection.engine)  # NOQA
    session = Session(bind=connection)
    imgs = (
        session.query(StoredFile)
        .filter_by(size=None)
        .options(load_only("id", "name", "title"))
    )

    for img in imgs:
        path = path_for(img.name) + '.*'
        gpath = glob(path)
        if gpath:
            img.width, img.height = get_width_height(gpath[0])
            img.size = os.path.getsize(gpath[0])

            print('updated attributes of %s\n' % img.title, end=' ')  # NOQA
        else:
            print('local file not found for %s\n' % img.title, end=' ')  # NOQA
    session.commit()


def downgrade():
    pass
