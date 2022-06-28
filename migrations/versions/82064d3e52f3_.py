"""empty message

Revision ID: 82064d3e52f3
Revises: 9e9bed5ab7c5
Create Date: 2022-06-28 14:23:48.551903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82064d3e52f3'
down_revision = '9e9bed5ab7c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('room',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('roomName', sa.String(length=64), nullable=False),
    sa.Column('person_num', sa.Integer(), nullable=False),
    sa.Column('remote', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.add_column('meeting', sa.Column('roomId', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'meeting', 'room', ['roomId'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'meeting', type_='foreignkey')
    op.drop_column('meeting', 'roomId')
    op.drop_table('room')
    # ### end Alembic commands ###