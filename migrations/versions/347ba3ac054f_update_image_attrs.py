"""update image attrs

Revision ID: 347ba3ac054f
Revises: 555bc8d5cbd7
Create Date: 2013-06-06 22:44:36.482379

"""

# revision identifiers, used by Alembic.
revision = '347ba3ac054f'
down_revision = '555bc8d5cbd7'


import os.path
import sys
from glob import glob

sys.path.append('../../')
from imgee import db
from imgee.models import StoredFile
from imgee.storage import get_width_height, path_for


def upgrade():
    imgs = StoredFile.query.filter_by(size=None)

    for img in imgs:
        path = path_for(img.name) + '.*'
        gpath = glob(path)
        if gpath:
            img.width, img.height = get_width_height(gpath[0])
            img.size = os.path.getsize(gpath[0])

            print 'updated attributes of %s\n' % img.title,
        else:
            print 'local file not found for %s\n' % img.title,
    db.session.commit()


def downgrade():
    pass
