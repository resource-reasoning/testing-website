"""add missing test_cases boolean columns

Revision ID: 21843d55caa
Revises: 37283c11df4
Create Date: 2016-06-21 18:35:07.080337

"""

# revision identifiers, used by Alembic.
revision = '21843d55caa'
down_revision = '37283c11df4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('test_cases', sa.Column('nostrict', sa.Boolean(), nullable=False), schema='jsil')
    op.add_column('test_cases', sa.Column('onlystrict', sa.Boolean(), nullable=False), schema='jsil')
    op.add_column('test_cases', sa.Column('es5test', sa.Boolean(), nullable=False, server_default='false'), schema='jsil')
    op.create_foreign_key('test_group_memberships_test_id_fkey', 'test_group_memberships', 'test_cases', ['test_id'], ['id'], source_schema='jsil', referent_schema='jsil')

def downgrade():
    op.drop_constraint('test_group_memberships_test_id_fkey', 'test_group_memberships', schema='jsil', type_='foreignkey')
    op.drop_column('test_cases', 'es5test', schema='jsil')
    op.drop_column('test_cases', 'onlystrict', schema='jsil')
    op.drop_column('test_cases', 'nostrict', schema='jsil')
