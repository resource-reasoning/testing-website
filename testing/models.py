from sqlalchemy import (Boolean, Column, Enum, DateTime, ForeignKey, Integer,
                        Interval, SmallInteger, String, Text)
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import backref, relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base(metadata=MetaData(schema='cr1013'))

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

    job_id = Column(Integer, ForeignKey('test_jobs.id', name='test_batches_job_id_fkey'))
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

    test_id = Column(String, ForeignKey('test_cases.id', name='test_runs_test_id_fkey'))
    testcase = relationship('TestCase')

    batch_id = Column(Integer, ForeignKey('test_batches.id', name='test_runs_batch_id_fkey'))
    batch = relationship('Batch', backref=backref('runs'))

    result = Column(Enum('PASS', 'FAIL', 'ABORT', 'UNKNOWN', 'TIMEOUT', name='jscert.result_text'))
    exit_code = Column(SmallInteger)
    stdout = Column(Text)
    stderr = Column(Text)
    duration = Column(Interval)

class TestCase(Base):
    __tablename__ = 'test_cases'

    id = Column(String, primary_key=True)
    negative = Column(Boolean)

class FailGroup(Base):
    __tablename__ = 'fail_groups'

    id = Column(Integer, primary_key=True)
    description = Column(Text)
    reason = Column(Text)

class TestGroup(Base):
    __tablename__ = 'test_groups'

    id = Column(Integer, primary_key=True)
    description = Column(Text)

class FailGroupMembership(Base):
    __tablename__ = 'fail_group_memberships'

    group_id = Column(Integer, ForeignKey('fail_groups.id', name='fail_group_memberships_group_id_fkey'), primary_key=True)
    test_id = Column(String, ForeignKey('test_cases.id', name='fail_group_memberships_test_id_fkey'), primary_key=True)

class TestGroupMembership(Base):
    __tablename__ = 'test_group_memberships'

    group_id = Column(Integer, ForeignKey('test_groups.id', name='test_group_memberships_group_id_fkey'), primary_key=True)
    test_id = Column(String, ForeignKey('test_cases.id', name='test_group_memberships_test_id_fkey'), primary_key=True)
