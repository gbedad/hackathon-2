"""empty message

Revision ID: 3b5622b61017
Revises: 82064d3e52f3
Create Date: 2022-06-28 15:16:31.840881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b5622b61017'
down_revision = '82064d3e52f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('room', 'remote',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.create_unique_constraint(None, 'room', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'room', type_='unique')
    op.alter_column('room', 'remote',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###
