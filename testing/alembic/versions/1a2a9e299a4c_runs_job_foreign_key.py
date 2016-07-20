"""runs job foreign key

Revision ID: 1a2a9e299a4c
Revises: 5a583b3c6089
Create Date: 2015-07-15 15:51:24.750456

"""

# revision identifiers, used by Alembic.
revision = '1a2a9e299a4c'
down_revision = '5a583b3c6089'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    
    ### Upgrade to version that contains job_id in Runs directly. ###

    op.add_column('test_runs', sa.Column('job_id', sa.Integer(), nullable=True), schema='jsil')
    op.create_foreign_key('test_runs_job_id_fkey', 'test_runs', 'test_jobs', ['job_id'], ['id'], source_schema='jsil', referent_schema='jsil')
    # Run an update to import values of job_id into new foregin key column.
    op.execute('update jsil.test_runs set job_id = jsil.test_batches.job_id from jsil.test_batches where jsil.test_batches.id = batch_id;')
    ### end Alembic commands ###


def downgrade():
    op.drop_constraint('test_runs_job_id_fkey', 'test_runs', schema='jsil', type_='foreignkey')
    op.drop_column('test_runs', 'job_id')
    ### end Alembic commands ###
