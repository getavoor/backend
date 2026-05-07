"""Transform to time management app

Revision ID: e1f2a3b4c5d6
Revises: badebd87bdc0
Create Date: 2025-11-27 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f2a3b4c5d6'
down_revision = 'badebd87bdc0'
branch_labels = None
depends_on = None


def upgrade():
    # Drop restaurant table
    op.drop_table('restaurant')

    # Modify user table - remove taste_biography, add time management fields
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('taste_biography')
        batch_op.add_column(sa.Column('plancoins', sa.Integer(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('current_streak', sa.Integer(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('longest_streak', sa.Integer(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('last_task_completion_date', sa.Date(), nullable=True))

    # Create task table
    op.create_table('task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.String(length=5000), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create plancoin_transaction table
    op.create_table('plancoin_transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop new tables
    op.drop_table('plancoin_transaction')
    op.drop_table('task')

    # Restore user table fields
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_task_completion_date')
        batch_op.drop_column('longest_streak')
        batch_op.drop_column('current_streak')
        batch_op.drop_column('plancoins')
        batch_op.add_column(sa.Column('taste_biography', sa.String(length=5000), nullable=True))

    # Recreate restaurant table
    op.create_table('restaurant',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=1000), nullable=False),
        sa.Column('address', sa.String(length=1000), nullable=False),
        sa.Column('maps_id', sa.String(length=1000), nullable=False),
        sa.Column('taste_biography', sa.String(length=5000), nullable=False),
        sa.Column('is_test', sa.Boolean(), nullable=True),
        sa.Column('photo_url', sa.String(length=1000), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('review_amount', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
