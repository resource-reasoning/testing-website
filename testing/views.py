from pyramid.response import Response
from pyramid.view import view_config

from datatables import DataTable

from pyramid.httpexceptions import (
        HTTPNotFound,
        HTTPFound,
    )

from sqlalchemy import func, text, cast, Text, or_, column
from sqlalchemy.orm import aliased

from .models import (
    DBSession,
    Job,
    Batch,
    Run,
    TestCase,
    TestGroup,
    TestGroupMembership
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
    runs_stats = DBSession.query(Run.result, func.count(Run.result)).filter(
        Run.job_id == request.matchdict['job_id']).group_by(Run.result).all()
    return dict(runs_stats=runs_stats, root_url=request.route_url('view_home'))

@view_config(route_name='request_job_table', request_method='GET', renderer='json')
def request_job_table(request):
    # Server side processing for DataTables plugin

    query = DBSession.query(Run.id, Run.test_id, Run.result).filter(Run.job_id == request.matchdict['job_id'])

    table = DataTable(request.GET, Run, query, ["test_id", "result"])
    table.add_data(link=lambda o: request.route_url("view_test_run", test_id=o.id))
    # Search for similarity in Results or Regex in test_id
    table.searchable(lambda queryset, userinput: queryset.filter(or_(cast(Run.result, Text).\
                like('%' + userinput.upper() + '%'), Run.test_id.op('~')(userinput))))

    return table.json()

@view_config(route_name='request_job_table_nogroup', request_method='GET', renderer='json')
def request_job_table_nogroup(request):
    # Server side processing for DataTables plugin

    # Double query required to figure out which tests do NOT have a group yet.
    query = DBSession.query(Run.test_id).join(TestGroupMembership, TestGroupMembership.test_id == Run.test_id).\
                filter(Run.job_id == request.matchdict['job_id'])
    actual = DBSession.query(Run.id, Run.test_id, Run.result).filter(~Run.test_id.in_(query)).filter(Run.job_id == request.matchdict['job_id'])

    table = DataTable(request.GET, Run, actual, ["test_id", "result"])
    table.add_data(link=lambda o: request.route_url("view_test_run", test_id=o.id))
    table.searchable(lambda queryset, userinput: queryset.filter(or_(cast(Run.result, Text).\
                like('%' + userinput.upper() + '%'), Run.test_id.op('~')(userinput))))
    return table.json()




@view_config(route_name='view_test_run', renderer='templates/testrun.pt')
def view_test_run(request):
    run = DBSession.query(Run).filter(Run.id == request.matchdict['test_id']).first()
    groups = DBSession.query(TestGroup).join(TestGroupMembership, TestGroupMembership.group_id == TestGroup.id).\
                filter(TestGroupMembership.test_id == run.test_id).all()
    return dict(run=run, groups=groups, redirect=request.route_url('view_test', test_id=run.test_id))



@view_config(route_name='view_test', renderer='templates/testcase.pt')
def view_test(request):
    runs = DBSession.query(Run).filter(
        Run.test_id == request.matchdict['test_id']).order_by(Run.id.desc()).all()
    runs_stats = DBSession.query(Run.result, func.count(Run.result)).filter(
        Run.test_id == request.matchdict['test_id']).group_by(Run.result).all()
    groups = DBSession.query(TestGroup).join(TestGroupMembership, TestGroupMembership.group_id == TestGroup.id).\
                filter(TestGroupMembership.test_id == request.matchdict['test_id']).all()
    return dict(runs=runs, runs_stats=runs_stats, groups=groups, root_url=request.route_url('view_home'))



@view_config(route_name='view_compare', renderer='templates/compare.pt')
def view_compare(request):

    res = DBSession.execute(text('''select test1.test_id, test1.id, test2.id, test1.result, test2.result 
    from 
      cr1013.test_runs test1 inner join cr1013.test_runs test2
    on 
      test1.job_id = :source 
    and 
      test2.job_id = :dest
    and 
      test1.test_id = test2.test_id
    and
      test1.result <> test2.result;'''), {'source':request.matchdict['job_id_source'], 
                                          'dest':  request.matchdict['job_id_dest']}  );
    return dict(res=res)

@view_config(route_name='view_groups', renderer='templates/groups.pt')
def view_groups(request):
    groups = DBSession.query(TestGroup).all()
    return dict(groups=groups)

@view_config(route_name='view_group', renderer='templates/group.pt')
def view_group(request):
    if request.method == 'DELETE':
        DBSession.delete(DBSession.query(TestGroup).get(request.matchdict['group_id']))
        return HTTPFound(location=request.route_url('view_groups'))
    group = DBSession.query(TestGroup).filter(TestGroup.id == request.matchdict['group_id']).first()
    cases = DBSession.query(TestGroupMembership).\
                filter(TestGroupMembership.group_id == request.matchdict['group_id']).all()
    return dict(group=group, cases=cases)

@view_config(route_name='create_group', renderer='templates/create_group.pt')
def create_group(request):
    if 'form.submitted' in request.params:
        desc = request.params['group_desc']
        group = TestGroup(description=desc)
        DBSession.add(group)
        DBSession.flush()
        group_id = group.id
        return HTTPFound(location=request.route_url('view_group', group_id=group_id))
    return dict()

@view_config(route_name='view_group_add', renderer='templates/add_group.pt')
def view_group_add(request):
    return dict()

@view_config(route_name='request_group_tests', request_method='GET', renderer='json')
def request_group_tests(request):
     # Server side processing for DataTables plugin

    in_cases  = DBSession.query(TestGroupMembership.test_id).\
                filter(TestGroupMembership.group_id == request.matchdict['group_id'])
    not_cases = DBSession.query(TestCase).filter(~TestCase.id.in_(in_cases))
    
    table = DataTable(request.GET, TestCase, not_cases, ["id"])
    table.add_data(link=lambda o: request.route_url("view_test", test_id=o.id))
    table.searchable(lambda queryset, userinput: queryset.filter(TestCase.id.op('~')(userinput)))
    return table.json()

@view_config(route_name='group_add_test', request_method='POST', renderer='json')
def group_add_test(request):
    tests = request.params.getall('tests')
    group_id = request.matchdict['group_id']
    for x in tests:   
        membership = TestGroupMembership(test_id=x, group_id=group_id)
        DBSession.add(membership)
    DBSession.flush()
    return dict(success=True)

@view_config(route_name='group_remove_test', request_method='POST', renderer='json')
def group_remove_test(request):
    tests = request.params.getall('tests')
    group_id = request.matchdict['group_id']
    allTests = DBSession.query(TestGroupMembership).filter(TestGroupMembership.group_id == group_id)
    for x in tests:   
        allTests.filter(TestGroupMembership.test_id == x).delete()
    DBSession.flush()
    return dict(success=True)
