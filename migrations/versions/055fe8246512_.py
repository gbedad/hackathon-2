"""empty message

Revision ID: 055fe8246512
Revises: 6f0fc8af2def
Create Date: 2022-06-30 17:08:03.724234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '055fe8246512'
down_revision = '6f0fc8af2def'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('participants_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('meeting', sa.String(length=64), nullable=True),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['meeting'], ['meeting.title'], ),
    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('participants_user')
    # ### end Alembic commands ###
