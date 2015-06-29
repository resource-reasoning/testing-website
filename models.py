from sqlalchemy import (Boolean, Column, Enum, DateTime, ForeignKey, Integer,
                        Interval, SmallInteger, String, Text)
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Job(Base):
    __tablename__ = 'test_jobs'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    note = Column(String)
    impl_name = Column(String)
    impl_version = Column(String)
    create_time = Column(DateTime)
    repo_version = Column(String)
    username = Column(String)
    condor_cluster = Column(SmallInteger)
    condor_scheduler = Column(String)


class Batch(Base):
    __tablename__ = 'test_batches'

    id = Column(Integer, primary_key=True)

    job_id = Column(Integer, ForeignKey('test_jobs.id'))
    job = relationship("Job", backref=backref('batches'))

    system = Column(String)
    osnodename = Column(String)
    osrelease = Column(String)
    osversion = Column(String)
    hardware = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    condor_proc = Column(SmallInteger)


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


class TestCase(Base):
    __tablename__ = 'test_cases'

    id = Column(String, primary_key=True)
    negative = Column(Boolean)
