"""Test Run to Group relation

Revision ID: 41279dd36a58
Revises: 1a2a9e299a4c
Create Date: 2015-07-30 13:59:16.303757

"""

# revision identifiers, used by Alembic.
revision = '41279dd36a58'
down_revision = '1a2a9e299a4c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('test_run_memberships',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], [u'cr1013.test_groups.id'], name='test_run_memberships_group_id_fkey'),
    sa.ForeignKeyConstraint(['run_id'], [u'cr1013.test_runs.id'], name='test_run_memberships_run_id_fkey'),
    sa.PrimaryKeyConstraint('group_id', 'run_id'),
    schema='cr1013'
    )


def downgrade():
    op.drop_table('test_run_memberships', schema='cr1013')