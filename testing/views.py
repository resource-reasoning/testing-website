from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import (
        HTTPNotFound,
        HTTPFound,
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Place,
    )


@view_config(route_name='view_wiki')
def view_wiki(request):
    return HTTPFound(location = request.route_url('view_places'))

@view_config(route_name='view_places', renderer='templates/test.pt')
def view_jobs(request):
    place = DBSession.query(Place).all()
    return dict(place=place)
