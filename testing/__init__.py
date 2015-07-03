from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('view_home', '/')
    config.add_route('view_jobs', '/jobs')
    config.add_route('view_job' , '/job/{job_id}')
    config.add_route('request_job_table', '/job/table/{job_id}')
    config.add_route('view_test_run', '/test/{test_id}')
    config.add_route('view_test', '/tests/{test_id:.*}')
    config.scan()
    return config.make_wsgi_app()
