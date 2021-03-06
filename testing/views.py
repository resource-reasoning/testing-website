from pyramid.response import Response
from pyramid.view import view_config

from datatables import DataTable

from pyramid.httpexceptions import (
        HTTPNotFound,
        HTTPFound,
    )

from sqlalchemy import func, text, cast, Text, or_, column, String
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.sql import expression
from zope.sqlalchemy import mark_changed

from . import DBSession
from .models import (
    Job,
    Batch,
    Run,
    TestCase,
    TestClassifier,
    TestGroup,
    TestGroupMembership,
    TestRunClassification,
    Stats
    )
from .model_helpers import *

import functools
import operator

import logging
log = logging.getLogger(__name__)


#### Home page and redirection ###
@view_config(route_name='view_home')
def view_home(request):
    return HTTPFound(location = request.route_url('view_jobs'))



### Jobs view: All jobs + statistical recap ###

@view_config(route_name='view_jobs', renderer='templates/home.pt')
def view_jobs(request):
    jobs = DBSession.query(Job).order_by(Job.create_time.desc()).all()

    stats = DBSession.query(Stats).order_by(Stats.job_id.desc()).limit(50)
    labels = []
    passes = []
    fails = []
    aborts = []
    timeouts = []
    unknowns = []
    for job in stats[::-1]:
        labels.append(job.job_id)
        passes.append(job.passes)
        fails.append(job.fails)
        aborts.append(job.aborts)
        timeouts.append(job.timeouts)
        unknowns.append(job.unknowns)
    series =dict(passes=passes, fails=fails, aborts=aborts, timeouts=timeouts, unknowns=unknowns)
    return dict(jobs=jobs, labels=labels, series=series)



### Single Job view and server side processing route ###

@view_config(route_name='view_job', renderer='templates/job.pt')
def view_batch(request):
    job_id = request.matchdict['job_id']
    job = DBSession.query(Job).filter(Job.id == job_id).one()

    runs_stats = DBSession.query(Run.result, func.count(Run.result)) \
                    .filter(Run.job_id == job_id) \
                    .group_by(Run.result).all()
    groups = DBSession.query(TestGroup).all()
    classifiers = DBSession.query(TestClassifier).all()
    return dict(runs_stats=runs_stats, root_url=request.route_url('view_home'),
                groups=groups, classifiers=classifiers, job=job)

@view_config(route_name='request_job_table', request_method='GET', renderer='json')
def request_job_table(request):
    # Server side processing for DataTables plugin

    job = request.matchdict['job_id']
    query = DBSession.query(Run.id, Run.test_id, Run.stdout, Run.stderr, Run.result).filter(Run.job_id == job)

    resultFilter = request.params.getall('resultFilter[]')
    if resultFilter:
        query = query.filter(Run.result.in_(resultFilter))

    groupFilter = request.params.getall('select-group[]')
    if groupFilter:
        group_subquery = DBSession.query(TestGroupMembership.test_id) \
            .filter(TestGroupMembership.group_id.in_(groupFilter))
        query = query.filter(Run.test_id.in_(group_subquery))

    groupExcludeFilter = request.params.getall('exclude-group[]')
    if groupExcludeFilter:
        groupExc_subquery = DBSession.query(TestGroupMembership.test_id) \
            .filter(TestGroupMembership.group_id.in_(groupExcludeFilter))
        query = query.filter(~Run.test_id.in_(groupExc_subquery))

    classifierFilter = request.params.getall('select-classifier[]')
    if classifierFilter:
        subquery = DBSession.query(Run.id).join(TestRunClassification) \
            .filter(Run.job_id == job) \
            .filter(TestRunClassification.classifier_id.in_(classifierFilter))
        query = query.filter(Run.id.in_(subquery))

    classifierFilter = request.params.getall('exclude-classifier[]')
    if classifierFilter:
        subquery = DBSession.query(Run.id).join(TestRunClassification) \
            .filter(Run.job_id == job) \
            .filter(TestRunClassification.classifier_id.in_(classifierFilter))
        query = query.filter(~Run.id.in_(subquery))

    table = DataTable(request.GET, Run, query, ["test_id", "stdout", "stderr", "result"])
    table.add_data(link=lambda o: request.route_url("view_test_run", test_id=o.id))
    # Search for similarity in Results or Regex in test_id
    table.searchable(lambda queryset, userinput: queryset.filter(or_(cast(Run.result, Text).\
                like('%' + userinput.upper() + '%'), Run.test_id.op('~')(userinput))))

    return table.json()



### Test run view ###

@view_config(route_name='view_test_run', renderer='templates/testrun.pt')
def view_test_run(request):
    run = DBSession.query(Run).options(joinedload(Run.batch), joinedload(Run.job)).\
                filter(Run.id == request.matchdict['test_id']).first()
    groups = DBSession.query(TestGroup).join(TestGroupMembership, TestGroupMembership.group_id == TestGroup.id).\
                filter(TestGroupMembership.test_id == run.test_id).all()

    classifs = DBSession.query(TestClassifier.id, TestClassifier.description) \
        .join(TestRunClassification, TestRunClassification.classifier_id == TestClassifier.id) \
        .filter(TestRunClassification.run_id == run.id).all()

    return dict(run=run, groups=groups, classifiers=classifs,
                redirect=request.route_url('view_test', test_id=run.test_id))



### Test case view ###

@view_config(route_name='view_test', renderer='templates/testcase.pt')
def view_test(request):
    test_id = request.matchdict['test_id']
    testcase = DBSession.query(TestCase).filter(TestCase.id == test_id) \
                    .options(joinedload(TestCase.runs)) \
                    .one()

    runs_stats = DBSession.query(Run.result, func.count(Run.result)).filter(
        Run.test_id == test_id).group_by(Run.result).all()

    groups = DBSession.query(TestGroup).join(TestGroupMembership, TestGroupMembership.group_id == TestGroup.id).\
                filter(TestGroupMembership.test_id == test_id).all()
    return dict(testcase=testcase, runs_stats=runs_stats, groups=groups, root_url=request.route_url('view_home'))



### Comparison view ###

aliased_run = aliased(Run)

@view_config(route_name='view_compare', renderer='templates/compare.pt')
def view_compare(request):
    return dict()

@view_config(route_name='compare_table', request_method='GET', renderer='json')
def compare_table(request):
    # Server Side processing for Datatables.

    res = DBSession.query(Run.test_id, Run.id.label('run_id'), aliased_run.id.label('alt_id'), Run.result, aliased_run.result.label("alt_result")).\
                            join(aliased_run, Run.test_id == aliased_run.test_id).\
                            filter(Run.job_id == request.matchdict['job_id_source']).\
                            filter(aliased_run.job_id == request.matchdict['job_id_dest']).\
                            filter(aliased_run.result != Run.result)

    table = DataTable(request.GET, Run, res, [("test_id"), ("run_id"), ("alt_id"), ("result"), ("alt_result")])
    table.add_data(link      =lambda o: request.route_url("view_test", test_id=o.test_id))
    table.add_data(sourcelink=lambda o: request.route_url("view_test_run", test_id=o.run_id))
    table.add_data(destlink  =lambda o: request.route_url("view_test_run", test_id=o.alt_id))
    table.searchable(lambda queryset, userinput: queryset.\
            filter(Run.test_id.op('~')(userinput)))
    return table.json()

@view_config(route_name='compare_save', request_method='GET', renderer='csv')
def compare_save(request):
    # Query saving based on Pyramid wiki example: http://pyramid-cookbook.readthedocs.org/en/latest/templates/customrenderers.html

    res = DBSession.query(Run.test_id, Run.id.label('run_id'), aliased_run.id.label('alt_id'), Run.result, aliased_run.result.label("alt_result")).\
                            join(aliased_run, Run.test_id == aliased_run.test_id).\
                            filter(Run.job_id == request.matchdict['job_id_source']).\
                            filter(aliased_run.job_id == request.matchdict['job_id_dest']).\
                            filter(aliased_run.result != Run.result)

    # Recreate user search:
    search = request.params['search']
    if (search != ''):
        res = res.filter(Run.test_id.op('~')(search))
    res = res.all()

    header= ['test_id','src_run_id', 'dst_run_id', 'src_result', 'dst_result']
    rows = [[item.test_id, item.run_id, item.alt_id, item.result, item.alt_result] for item in res]

    # override attributes of response
    filename = 'compare' + request.matchdict['job_id_source'] + '_' + request.matchdict['job_id_dest'] + '.csv'
    request.response.content_disposition = 'attachment;filename=' + filename

    return {'header': header, 'rows': rows}



### GROUPS: many group view, single group view, addition, creation, deletion routes ###

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

### Classifiers ###
@view_config(route_name='list_classifiers', renderer='templates/list_classifiers.pt')
def list_classifiers(request):
    classifiers = DBSession.query(TestClassifier).all()
    return dict(classifiers=classifiers)

@view_config(route_name='create_classifier', renderer='templates/create_classifier.pt')
def create_classifier(request):
    if 'form.submitted' in request.params:
        desc = request.params['description']
        col = request.params['field']
        pat = request.params['pattern']
        print(col)
        print(pat)
        classifier = TestClassifier(description=desc, column=col, pattern=pat)
        DBSession.add(classifier)
        DBSession.flush()
        classifier_id = classifier.id
        return HTTPFound(location=request.route_url('view_classifier', classifier_id=classifier_id))
    return dict(columns=Run.__table__.columns.keys(), classifier=None)

@view_config(route_name='view_classifier', renderer='templates/view_classifier.pt')
def view_classifier(request):
    classifier = DBSession.query(TestClassifier) \
                          .filter_by(id=request.matchdict['classifier_id']) \
                          .one()

    return dict(columns=Run.__table__.c.keys(), classifier=classifier, view=True)

@view_config(route_name='test_classifier', request_method='GET', renderer='json')
def test_classifier(request):
    classifier = DBSession.query(TestClassifier) \
                          .filter_by(id=request.matchdict['classifier_id']) \
                          .first()

    col = getattr(Run, str(classifier.column))

    matched_runs = DBSession.query(Run.id, Run.test_id, col) \
                       .filter(col.op('~')(classifier.pattern))

    if request.params['job_id']:
        matched_runs = matched_runs.filter(Run.job_id == request.params['job_id'])

    table = DataTable(request.GET, Run, matched_runs, ["id", "test_id", classifier.column])
    table.add_data(link=lambda o: request.route_url("view_test_run", test_id=o.id))
    table.searchable(lambda queryset, userinput: queryset.filter(Run.test_id.op('~')(userinput)))
    return table.json()

@view_config(route_name='apply_classifier', request_method='POST')
def apply_classifier(request):
    job = request.params['job']
    cid = request.matchdict['classifier_id']

    session = DBSession()

    if request.params['submit'] == 'apply':

        classifiers = session.query(TestClassifier)
        if cid != "all":
            classifiers = classifiers.filter_by(id=cid)
        classifiers = classifiers.all()

        for classifier in classifiers:
            col = getattr(Run, str(classifier.column))

            matched_runs = session.query(str(classifier.id), Run.id) \
                            .filter(Run.job_id == job) \
                            .filter(col.op('~')(classifier.pattern))

            query = expression.insert(TestRunClassification).from_select(
                [TestRunClassification.classifier_id, TestRunClassification.run_id],
                matched_runs)

            session.execute(query)

    elif request.params['submit'] == 'delete':
        subquery = session.query(TestRunClassification.run_id) \
                       .join(Run).filter(Run.job_id == job)

        query = session.query(TestRunClassification) \
            .filter(TestRunClassification.run_id.in_(subquery))

        if cid != "all":
            query = query.filter(TestRunClassification.classifier_id == cid)

        query.delete(synchronize_session=False)

    mark_changed(session)

    if cid == 'all':
        return HTTPFound(location=request.route_url('list_classifiers'))
    else:
        return HTTPFound(location=request.route_url('view_classifier', classifier_id=cid))

@view_config(route_name='rollup_test', renderer='templates/sum.pt')
def rollup_test(request):
    id = request.params['job']

    one = func.split_part(Run.test_id, '/', 4).alias('one')
    two = func.split_part(Run.test_id, '/', 5).alias('two')

    passed = (Run.result == 'PASS').alias('PASS')
    failed = (Run.result == 'FAIL').alias('FAIL')
    abort = (Run.result == 'ABORT').alias('ABORT')
    timeout = (Run.result == 'TIMEOUT').alias('TIMEOUT')

    rollup_cols = [one, two]
    q = DBSession.query(passed, failed, abort, timeout, *rollup_cols) \
                 .where(Run.job_id == id)

    q = rollup(DBSession, q, *rollup_cols)
    columns = [c['name'] for c in q.column_descriptions]
    return dict(cols=columns, rows=q.all())

@view_config(route_name='summarise_job_filter', renderer='templates/sum.pt')
def summarise_job_filter(request):
    ignored_runs = DBSession.query(TestGroupMembership.test_id) \
        .filter(TestGroupMembership.group_id.between(6,8)) #16))
    test_runs = DBSession.query(Run.id, Run.test_id, Run.result) \
        .filter(Run.job_id == 74) \
        .filter(Run.test_id.notin_(ignored_runs)) \
        .cte()

    rollup_cols = [TestCase.part1, TestCase.part2] # , TestCase.part3, TestCase.part4,
                 #TestCase.part5, TestCase.part6]

    # Pivot table for group membership
    groups = DBSession.query(TestGroup.id, TestGroup.description) \
        .filter(TestGroup.id.between(9,21)).all()

    test_case_id = TestCase.id.label('test_case_id')
    query = DBSession.query(test_case_id, *rollup_cols) \
            .join(test_runs, test_runs.c.test_id == test_case_id) \
            .outerjoin(TestGroupMembership)

    pivot_exps = [TestGroupMembership.group_id == g.id for g in groups]
    pivot_labels = tuple("G: "+g.description for g in groups)
    query = pivot(query, pivot_exps, pivot_labels)

    sum_g_column = functools.reduce(operator.add, pivot_exps).label("Sum G")
    query = query.add_columns(sum_g_column)

    # Stick it into a subquery -- if we just use multiple outer left joins,
    # we get a cross product join between groups and classifications
    # (since the grouping is applied late), work out ways to improve on this
    subquery = query.subquery()

    # Pivot table for test classifications
    classifiers = DBSession.query(TestClassifier.id, TestClassifier.description).all()
    query = DBSession.query(subquery) \
        .join(test_runs, test_runs.c.test_id == subquery.c.test_case_id) \
        .outerjoin(TestRunClassification, test_runs.c.id == TestRunClassification.run_id)

    pivot_exps = [TestRunClassification.classifier_id == c.id for c in classifiers]
    pivot_labels = tuple("C: " + c.description for c in classifiers)
    query = pivot(query, pivot_exps, pivot_labels)

    sum_c_column = functools.reduce(operator.add, pivot_exps).label("Sum C")
    query = query.add_columns(sum_c_column)

    subquery = query.subquery()

    # Drop off TestCase.id for grouping
    query = DBSession.query(subquery) \
        .join(test_runs, test_runs.c.test_id == subquery.c.test_case_id)

    sum_g_column = subquery.corresponding_column(sum_g_column)
    sum_c_column = subquery.corresponding_column(sum_c_column)

    pass_col = test_runs.c.result == 'PASS'
    fail_col = ~pass_col
    filtered_exp = (sum_g_column + sum_c_column) > 0
    pass_filtered_col = pass_col & filtered_exp
    fail_filtered_col = fail_col & ~filtered_exp

    # Generic count columns
    query = pivot(query,
                  [pass_col, fail_col, filtered_exp, pass_filtered_col, fail_filtered_col],
                  ["Pass", "Fail", "filtered", "Pass & Filtered", "Fail & ~Filtered"])

    # Fetch out the new rollup column aliases for the rollup operation
    rollup_cols = tuple(subquery.corresponding_column(c) for c in rollup_cols)
    query = rollup(DBSession, query, rollup_cols, f=func.sum,
                   mask_cols=(test_case_id,))

    columns = (c['name'] for c in query.column_descriptions)

    return dict(cols=columns, rows=query.all())
