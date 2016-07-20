"""populate condor_proc column

Revision ID: 574e747f1d4
Revises: 21843d55caa
Create Date: 2016-06-24 10:16:55.064015

"""

# revision identifiers, used by Alembic.
revision = '574e747f1d4'
down_revision = '21843d55caa'
branch_labels = None
depends_on = None

from alembic import op
from sqlalchemy import Integer, SmallInteger, func, Table, Column, select, MetaData

def upgrade():
    batches = Table('test_batches', MetaData(schema='jsil'),
        Column('id', Integer),
        Column('job_id', Integer),
        Column('condor_proc', SmallInteger),
    )

    indexed_batches = select([
        batches.c.id,
        (func.row_number()\
              .over(partition_by=batches.c.job_id, order_by=batches.c.id)\
              - op.inline_literal(1)).label('idx')
    ]).alias('indexed_batches')

    op.execute(
        batches.update()\
            .where(batches.c.condor_proc == op.inline_literal(-1))\
            .where(batches.c.id == indexed_batches.c.id)\
            .values(condor_proc = indexed_batches.c.idx)
    )

def downgrade():
    pass
