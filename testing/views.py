from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import (
        HTTPNotFound,
        HTTPFound,
    )

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

@view_config(route_name='view_jobs', renderer='templates/test.pt')
def view_jobs(request):
    jobs = DBSession.query(Job).order_by(Job.create_time.desc()).all()
    return dict(jobs=jobs)
