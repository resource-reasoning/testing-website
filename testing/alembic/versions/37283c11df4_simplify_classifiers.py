"""simplify test_classifiers table

Revision ID: 37283c11df4
Revises: 323affea5e1f
Create Date: 2016-06-20 19:19:19.230008

"""

# revision identifiers, used by Alembic.
revision = '37283c11df4'
down_revision = '323affea5e1f'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('test_classifiers', sa.Column('column', sa.Text(), nullable=True), schema='jsil')
    op.add_column('test_classifiers', sa.Column('description', sa.Text(), nullable=True), schema='jsil')
    op.add_column('test_classifiers', sa.Column('pattern', sa.Text(), nullable=True), schema='jsil')
    op.drop_constraint('test_classifiers_group_id_fkey', 'test_classifiers', schema='jsil', type_='foreignkey')
    op.drop_column('test_classifiers', 'class_value', schema='jsil')
    op.drop_column('test_classifiers', 'class_field', schema='jsil')
    op.drop_column('test_classifiers', 'class_operator', schema='jsil')
    op.drop_column('test_classifiers', 'group_id', schema='jsil')
    op.drop_constraint('test_group_memberships_test_id_fkey', 'test_group_memberships', schema='jsil', type_='foreignkey')


def downgrade():
    op.add_column('test_classifiers', sa.Column('group_id', sa.INTEGER(), autoincrement=False, nullable=True), schema='jsil')
    op.add_column('test_classifiers', sa.Column('class_operator', sa.VARCHAR(), autoincrement=False, nullable=False), schema='jsil')
    op.add_column('test_classifiers', sa.Column('class_field', sa.VARCHAR(), autoincrement=False, nullable=False), schema='jsil')
    op.add_column('test_classifiers', sa.Column('class_value', sa.VARCHAR(), autoincrement=False, nullable=False), schema='jsil')
    op.create_foreign_key('test_classifiers_group_id_fkey', 'test_classifiers', 'test_groups', ['group_id'], ['id'], source_schema='jsil', referent_schema='jsil')
    op.drop_column('test_classifiers', 'pattern', schema='jsil')
    op.drop_column('test_classifiers', 'description', schema='jsil')
    op.drop_column('test_classifiers', 'column', schema='jsil')
