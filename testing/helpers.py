# Helper functions for rendering engines
def test262_link(path):
    (_, partitioned, subpath) = path.rpartition('test262/')
    if partitioned:
        base_url = "https://github.com/tc39/test262/tree/es5-tests/"
    else:
        (_, _, subpath) = path.rpartition('test262-es6/')
        base_url = "https://github.com/tc39/test262/tree/master/"
    return base_url + subpath
