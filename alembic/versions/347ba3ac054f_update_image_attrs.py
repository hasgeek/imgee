"""update image attrs

Revision ID: 347ba3ac054f
Revises: 555bc8d5cbd7
Create Date: 2013-06-06 22:44:36.482379

"""

# revision identifiers, used by Alembic.
revision = '347ba3ac054f'
down_revision = '555bc8d5cbd7'

from alembic import op
import sqlalchemy as sa


import os.path
import sys

sys.path.append('../../')
from imgee import app, init_for, db
from imgee.models import StoredFile
from imgee.storage import get_width_height, path_for

def upgrade():
    imgs = StoredFile.query.filter_by(size=None)

    for img in imgs:
        path = path_for(img.name) + os.path.splitext(img.title)[1]
        img.width, img.height = get_width_height(path)
        img.size = os.path.getsize(path)
        
        print 'updated attributes of %s\n' % img.title,
    db.session.commit()

def downgrade():
    pass
