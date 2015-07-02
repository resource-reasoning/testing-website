# testing-website
Python web interface to jscert test results database

### Installing
You can get through installation on your own via [this page](http://docs.pylonsproject.org/projects/pyramid//en/latest/narr/install.html), or follow this, which is a condensed, need only version of that page.

To set up the app in a development environment, you will need the python `setuptools` library. With that, make sure you also have `virtualenv`, which can be installed through setuptools by running `easy_install virtualenv`.

With that, you can now create a virtual environment:
```
> export VENV=~/some/path/where/you/want/this/to/be
> virtualenv $VENV
```
You'll now install Pyramid in the virtual environment.
```
> $VENV/bin/easy_install "pyramid==1.5.7"
```
Clone the repo into `$VENV`, then create a duplicate of `development.ini`, which I'll call here `development_actual.ini`. Fill in your db credentials on the sqlalchemy.url line.

You can then run the commands in the README.txt, replacing `development.ini` with `development_actual.ini.