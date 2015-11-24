"""Statistics table

Revision ID: 323affea5e1f
Revises: 32b00f238557
Create Date: 2015-08-04 11:32:59.803926

"""

# revision identifiers, used by Alembic.
revision = '323affea5e1f'
down_revision = '32b00f238557'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('test_job_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('passes', sa.Integer(), nullable=True),
    sa.Column('fails', sa.Integer(), nullable=True),
    sa.Column('aborts', sa.Integer(), nullable=True),
    sa.Column('unknowns', sa.Integer(), nullable=True),
    sa.Column('timeouts', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], [u'jsil.test_jobs.id'], name='test_job_stats_job_id_fkey'),
    sa.PrimaryKeyConstraint('id'),
    schema='jsil'
    )
    # Execute raw query to populate the stats table with existing data!
    op.execute('''insert into jsil.test_job_stats (job_id, passes, fails, aborts, unknowns, timeouts)
                        select 
                          job_id, 
                          sum(case result::text when 'PASS' then 1 else 0 end) as total_pass,
                          sum(case result::text when 'FAIL' then 1 else 0 end) as total_fail,
                          sum(case result::text when 'ABORT' then 1 else 0 end) as total_abort,
                          sum(case result::text when 'UNKNOWN' then 1 else 0 end) as total_unknown,
                          sum(case result::text when 'TIMEOUT' then 1 else 0 end) as total_timeout
                        from jsil.test_runs group by job_id order by job_id asc;''')


def downgrade():
    op.drop_table('test_job_stats', schema='jsil')