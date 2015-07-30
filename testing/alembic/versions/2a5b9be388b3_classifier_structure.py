"""Classifier structure

Revision ID: 2a5b9be388b3
Revises: 41279dd36a58
Create Date: 2015-07-30 16:23:19.794321

"""

# revision identifiers, used by Alembic.
revision = '2a5b9be388b3'
down_revision = '41279dd36a58'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('classifiers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('field', sa.String(), nullable=False),
    sa.Column('operator', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='cr1013'
    )
    op.create_table('group_classifier_membership',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('classifier_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['classifier_id'], [u'cr1013.classifiers.id'], name='group_classifier_memberships_classifier_id_fkey'),
    sa.ForeignKeyConstraint(['group_id'], [u'cr1013.test_groups.id'], name='group_classifier_memberships_group_id_fkey'),
    sa.PrimaryKeyConstraint('group_id', 'classifier_id'),
    schema='cr1013'
    )


def downgrade():
    op.drop_table('group_classifier_membership', schema='cr1013')
    op.drop_table('classifiers', schema='cr1013')