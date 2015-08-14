from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sys
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
    config.add_renderer('csv', 'testing.renderers.CSVRenderer')

    config.add_route('view_home', '/')
    config.add_route('view_jobs', '/jobs')
    config.add_route('view_job' , '/job/{job_id}')
    config.add_route('request_job_table', '/job/table/{job_id}')
    
    config.add_route('view_compare', '/compare/{job_id_dest}/{job_id_source}')
    config.add_route('compare_table', '/compare/table/{job_id_dest}/{job_id_source}')
    config.add_route('compare_save', '/compare/save/{job_id_dest}/{job_id_source}')
    
    config.add_route('view_test_run', '/test/{test_id}')
    config.add_route('view_test', '/tests/{test_id:.*}')
    
    config.add_route('view_groups','/groups/')
    config.add_route('create_group', '/group/create')
    config.add_route('view_group_add', '/group/add/{group_id}')
    config.add_route('group_add_test', '/group/addtest/{group_id}')
    config.add_route('group_remove_test', '/group/removetest/{group_id}')
    config.add_route('request_group_tests', '/group/add/table/{group_id}')
    config.add_route('view_group', '/group/{group_id}')
    config.scan()
    return config.make_wsgi_app()
