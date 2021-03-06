"""empty message

Revision ID: 05624d3088ad
Revises: 
Create Date: 2020-05-10 20:57:20.241519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05624d3088ad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('uuid', sa.String(length=36), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_group_uuid'), 'group', ['uuid'], unique=True)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('uuid', sa.String(length=36), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_index(op.f('ix_user_uuid'), 'user', ['uuid'], unique=True)
    op.create_table('follow',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('originating_id', sa.Integer(), nullable=True),
    sa.Column('target_id', sa.Integer(), nullable=True),
    sa.Column('label', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['originating_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['target_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_follow_originating_id'), 'follow', ['originating_id'], unique=False)
    op.create_index(op.f('ix_follow_target_id'), 'follow', ['target_id'], unique=False)
    op.create_table('group_membership',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('label', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_group_membership_group_id'), 'group_membership', ['group_id'], unique=False)
    op.create_index(op.f('ix_group_membership_member_id'), 'group_membership', ['member_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_group_membership_member_id'), table_name='group_membership')
    op.drop_index(op.f('ix_group_membership_group_id'), table_name='group_membership')
    op.drop_table('group_membership')
    op.drop_index(op.f('ix_follow_target_id'), table_name='follow')
    op.drop_index(op.f('ix_follow_originating_id'), table_name='follow')
    op.drop_table('follow')
    op.drop_index(op.f('ix_user_uuid'), table_name='user')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_group_uuid'), table_name='group')
    op.drop_table('group')
    # ### end Alembic commands ###
