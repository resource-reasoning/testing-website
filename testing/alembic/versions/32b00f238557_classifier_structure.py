"""Classifier structure

Revision ID: 32b00f238557
Revises: 1a2a9e299a4c
Create Date: 2015-07-31 11:32:12.708799

"""

# revision identifiers, used by Alembic.
revision = '32b00f238557'
down_revision = '1a2a9e299a4c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('test_classifiers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('class_field', sa.String(), nullable=False),
    sa.Column('class_operator', sa.String(), nullable=False),
    sa.Column('class_value', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], [u'cr1013.test_groups.id'], name='test_classifiers_group_id_fkey'),
    sa.PrimaryKeyConstraint('id'),
    schema='cr1013'
    )
    op.create_table('test_run_classifications',
    sa.Column('classifier_id', sa.Integer(), nullable=False),
    sa.Column('run_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['classifier_id'], [u'cr1013.test_classifiers.id'], name='test_run_classifications_classifier_id_fkey'),
    sa.ForeignKeyConstraint(['run_id'], [u'cr1013.test_runs.id'], name='test_run_memberships_run_id_fkey'),
    sa.PrimaryKeyConstraint('classifier_id', 'run_id'),
    schema='cr1013'
    )


def downgrade():
    op.drop_table('test_run_classifications', schema='cr1013')
    op.drop_table('test_classifiers', schema='cr1013')
