"""add tests_version field to test_jobs

Revision ID: f88925aa21
Revises: 574e747f1d4
Create Date: 2016-06-28 17:41:23.846209

"""

# revision identifiers, used by Alembic.
revision = 'f88925aa21'
down_revision = '574e747f1d4'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('test_jobs', sa.Column('tests_version', sa.String()), schema='jsil')

def downgrade():
    op.drop_column('test_jobs', 'tests_version', schema='jsil')
