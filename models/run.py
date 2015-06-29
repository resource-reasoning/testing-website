from sqlalchemy import (Column, Enum, ForeignKey, Integer, Interval,
                        SmallInteger, String, Text)
from sqlalchemy.orm import backref, relationship


class Run(Base):
    __tablename__ = 'test_runs'

    id = Column(Integer, primary_key=True)

    test_id = Column(String, ForeignKey('test_cases.id'))
    testcase = relationship('TestCase')

    batch_id = Column(Integer, ForeignKey('test_batches.id'))
    job = relationship('Batch', backref=backref('runs'))

    result = Column(Enum('PASS', 'FAIL', 'ABORT', 'UNKNOWN', 'TIMEOUT'))
    exit_code = Column(SmallInteger)
    stdout = Column(Text)
    stderr = Column(Text)
    duration = Column(Interval)
