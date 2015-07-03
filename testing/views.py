from pyramid.response import Response
from pyramid.view import view_config

from datatables import ColumnDT,DataTables

from pyramid.httpexceptions import (
        HTTPNotFound,
        HTTPFound,
    )

from sqlalchemy import func

from .models import (
    DBSession,
    Job,
    Batch,
    Run,
    TestCase,
    )

import logging
log = logging.getLogger(__name__)


@view_config(route_name='view_home')
def view_home(request):
    return HTTPFound(location = request.route_url('view_jobs'))


@view_config(route_name='view_jobs', renderer='templates/home.pt')
def view_jobs(request):
    jobs = DBSession.query(Job).order_by(Job.create_time.desc()).all()
    return dict(jobs=jobs)


@view_config(route_name='view_job', renderer='templates/job.pt')
def view_batch(request):
    batches = DBSession.query(Batch.id).filter(Batch.job_id == request.matchdict['job_id']).subquery()
    runs = DBSession.query(Run).filter(Run.batch_id.in_(batches)).all()
    return dict(runs=runs, root_url=request.route_url('view_home'))

@view_config(route_name='request_job_table', request_method='GET', renderer='json')
def request_job_table(request):
    # Server side processing for DataTables plugin
    columns=[]
    #columns.append(ColumnDT('id'))
    columns.append(ColumnDT('test_id'))
    #columns.append(ColumnDT('testcase'))
    #columns.append(ColumnDT('batch_id'))
    #columns.append(ColumnDT('batch'))
    columns.append(ColumnDT('result'))
    columns.append(ColumnDT('test_id'))
    #columns.append(ColumnDT('exit_code'))
    #columns.append(ColumnDT('stdout'))
    #columns.append(ColumnDT('stderr'))
    #columns.append(ColumnDT('duration'))

    batches = DBSession.query(Batch.id).filter(Batch.job_id == request.matchdict['job_id']).subquery()
    query = DBSession.query(Run).filter(Run.batch_id.in_(batches))

    log.info('Completed query')

    runs = DataTables(request, Run, query, columns)

    return runs.output_result()

@view_config(route_name='view_test_run', renderer='templates/testrun.pt')
def view_test_run(request):
    run = DBSession.query(Run).filter(Run.id == request.matchdict['test_id']).first()
    return dict(run=run, redirect=request.route_url('view_test', test_id=run.test_id))


@view_config(route_name='view_test', renderer='templates/testcase.pt')
def view_test(request):
    runs = DBSession.query(Run).filter(
        Run.test_id == request.matchdict['test_id']).order_by(Run.id.desc()).all()
    runs_stats = DBSession.query(Run.result, func.count(Run.result)).filter(
        Run.test_id == 'tests/' + request.matchdict['test_id']).group_by(Run.result).all()
    return dict(runs=runs, runs_stats=runs_stats, root_url=request.route_url('view_home'))