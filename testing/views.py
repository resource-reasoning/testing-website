from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import (
        HTTPNotFound,
        HTTPFound,
    )

from sqlalchemy import func
from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Job,
    Batch,
    Run,
    TestCase,
    )


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
    runs_result = DBSession.query(Run.result, func.count(Run.result)).filter(Run.batch_id.in_(batches)).group_by(Run.result).all()
    return dict(runs=runs, runs_result=runs_result)

@view_config(route_name='view_test_run', renderer='templates/testrun.pt')
def view_test_run(request):
    run = DBSession.query(Run).filter(Run.id == request.matchdict['test_id']).first()
    return dict(run=run, redirect=request.route_url('view_test', test_id=run.test_id))

@view_config(route_name='view_test', renderer='templates/testcase.pt')
def view_test(request):
	runs = DBSession.query(Run.result, func.count(Run.result)).filter(
		Run.test_id == 'tests/' + request.matchdict['test_id']).group_by(Run.result).all()
	return dict(runs=runs)