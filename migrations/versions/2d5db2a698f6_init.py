"""init

Revision ID: 2d5db2a698f6
Revises: None
Create Date: 2013-05-06 12:09:54.133915

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2d5db2a698f6'
down_revision = None


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('username', sa.Unicode(length=80), nullable=True),
        sa.Column('lastuser_token_scope', sa.Unicode(length=250), nullable=True),
        sa.Column('userinfo', sa.UnicodeText(), nullable=True),
        sa.Column('lastuser_token_type', sa.Unicode(length=250), nullable=True),
        sa.Column('userid', sa.String(length=22), nullable=False),
        sa.Column('lastuser_token', sa.String(length=22), nullable=True),
        sa.Column('fullname', sa.Unicode(length=80), nullable=False),
        sa.Column('email', sa.Unicode(length=80), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('lastuser_token'),
        sa.UniqueConstraint('userid'),
        sa.UniqueConstraint('username'),
    )
    op.create_table(
        'profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('userid', sa.Unicode(length=22), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('userid'),
    )
    op.create_table(
        'stored_file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profile.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'label',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profile.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'thumbnail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('size', sa.Unicode(length=100), nullable=False),
        sa.Column('stored_file_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['stored_file_id'], ['stored_file.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'image_labels',
        sa.Column('label_id', sa.Integer(), nullable=True),
        sa.Column('stored_file_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['label_id'], ['label.id']),
        sa.ForeignKeyConstraint(['stored_file_id'], ['stored_file.id']),
        sa.PrimaryKeyConstraint(),
    )


def downgrade():
    op.drop_table('image_labels')
    op.drop_table('thumbnail')
    op.drop_table('label')
    op.drop_table('stored_file')
    op.drop_table('profile')
    op.drop_table('user')
