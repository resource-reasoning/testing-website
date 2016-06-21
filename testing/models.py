from sqlalchemy import (Boolean, Column, Enum, DateTime, ForeignKey, Integer,
                        Interval, SmallInteger, String, Text)
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import backref, column_property, deferred, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base(metadata=MetaData(schema='jsil'))

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
    testcase = relationship('TestCase', backref=backref('runs'))

    batch_id = Column(Integer, ForeignKey('test_batches.id', name='test_runs_batch_id_new_fkey'))
    batch = relationship('Batch', backref=backref('runs'))

    job_id = Column(Integer, ForeignKey('test_jobs.id', name='test_runs_job_id_fkey'))

    result = Column(Enum('PASS', 'FAIL', 'ABORT', 'UNKNOWN', 'TIMEOUT', name='jscert.result_text'))
    exit_code = Column(SmallInteger)
    stdout = deferred(Column(Text))
    stderr = deferred(Column(Text))
    duration = Column(Interval)

class TestCase(Base):
    __tablename__ = 'test_cases'

    id = Column(String, primary_key=True)
    negative = Column(Boolean, nullable=False)
    nostrict = Column(Boolean, nullable=False)
    onlystrict = Column(Boolean, nullable=False)
    es5test = Column(Boolean, nullable=False, server_default='false')

class TestGroup(Base):
    __tablename__ = 'test_groups'

    id = Column(Integer, primary_key=True)
    description = Column(Text)

class TestClassifier(Base):
    __tablename__ = 'test_classifiers'

    id = Column(Integer, primary_key=True)
    description = Column(Text)
    pattern = Column(Text)
    column = Column(Text)

class TestGroupMembership(Base):
    __tablename__ = 'test_group_memberships'

    group_id = Column(Integer, ForeignKey('test_groups.id', name='test_group_memberships_group_id_fkey'), primary_key=True)
    group = relationship('TestGroup', backref=backref('testgroupmemberships', cascade='all, delete-orphan'))

    test_id = Column(String, ForeignKey('test_cases.id', name='test_group_memberships_test_id_fkey'), primary_key=True)
    testcase = relationship('TestCase')

class TestRunClassification(Base):
    __tablename__ = 'test_run_classifications'

    classifier_id = Column(Integer, ForeignKey('test_classifiers.id', name='test_run_classifications_classifier_id_fkey'), primary_key=True)
    classifier = relationship('TestClassifier', backref=backref('testrunclassifiers', cascade='all, delete-orphan'))

    run_id = Column(Integer, ForeignKey('test_runs.id', name='test_run_memberships_run_id_fkey'), primary_key=True)
    run = relationship('Run', backref=backref('testrunclassifiers'))

class Stats(Base):
    __tablename__ = 'test_job_stats'

    id = Column(Integer, primary_key=True)

    job_id   = Column(Integer, ForeignKey('test_jobs.id', name='test_job_stats_job_id_fkey'))

    passes   = Column(Integer)
    fails    = Column(Integer)
    aborts   = Column(Integer)
    unknowns = Column(Integer)
    timeouts = Column(Integer)
