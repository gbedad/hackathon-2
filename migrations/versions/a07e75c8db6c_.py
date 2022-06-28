"""empty message

Revision ID: a07e75c8db6c
Revises: 
Create Date: 2022-06-28 11:17:15.174414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a07e75c8db6c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=False),
    sa.Column('fullname', sa.String(length=64), nullable=False),
    sa.Column('password', sa.String(length=64), nullable=False),
    sa.Column('role', sa.String(length=64), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###