"""Add streak freeze fields and create streak/reward tables

Revision ID: f1a2b3c4d5e6
Revises: e1f2a3b4c5d6
Create Date: 2026-05-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e1f2a3b4c5d6'
branch_labels = None
depends_on = None


def upgrade():
    # Add freeze_count and last_freeze_date to user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('freeze_count', sa.Integer(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('last_freeze_date', sa.Date(), nullable=True))

    # Create streak_update table
    op.create_table('streak_update',
        sa.Column('update_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('update_id')
    )

    # Create plancoin_reward table
    op.create_table('plancoin_reward',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=1000), nullable=False),
        sa.Column('cost', sa.Integer(), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop tables
    op.drop_table('plancoin_reward')
    op.drop_table('streak_update')

    # Remove columns from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_freeze_date')
        batch_op.drop_column('freeze_count')
