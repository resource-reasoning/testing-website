# Helper functions for rendering engines
def test262_link(path):
    base_url = "https://github.com/tc39/test262/tree/es5-tests/"
    (_, _, subpath) = path.rpartition('test262/')
    return base_url + subpath

