"""empty message

Revision ID: a3727bcae99f
Revises: 87850bd9e4c5
Create Date: 2020-04-11 21:42:00.193848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3727bcae99f'
down_revision = '87850bd9e4c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('follow',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('originating_user', sa.Integer(), nullable=True),
    sa.Column('target_user', sa.Integer(), nullable=True),
    sa.Column('label', sa.String(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['originating_user'], ['user.id'], ),
    sa.ForeignKeyConstraint(['target_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_follow_originating_user'), 'follow', ['originating_user'], unique=False)
    op.create_index(op.f('ix_follow_target_user'), 'follow', ['target_user'], unique=False)
    op.add_column('user', sa.Column('created_date', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'created_date')
    op.drop_index(op.f('ix_follow_target_user'), table_name='follow')
    op.drop_index(op.f('ix_follow_originating_user'), table_name='follow')
    op.drop_table('follow')
    # ### end Alembic commands ###