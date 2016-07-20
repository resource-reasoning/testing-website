# Helper functions for rendering engines
def test262_link(path, rev=None):
    (_, partitioned, subpath) = path.rpartition('test262/')
    if not partitioned:
        (_, _, subpath) = path.rpartition('test262-es6/')

    rev = rev or ('es5-tests' if ('suite' in subpath) else 'master')

    return "https://github.com/tc39/test262/tree/%s/%s" % (rev, subpath)
