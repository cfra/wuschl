from distutils.core import setup
import sys

if sys.version_info.major >= 3:
    sys.stderr.write("Wuschl is currently only for python2, sorry. :(\n")
    sys.exit(1)

setup(
    name="wuschl",
    version="0.2.0",
    license='MIT',
    author='Christian Franke',
    author_email='nobody@nowhere.ws',
    description='Tool to generate testcases with afl',
    scripts=["wuschl"],
    requires=['jinja2'],
    data_files=[('share/wuschl/templates',[
        'templates/main.c.j2',
        'templates/test.h.j2'
    ])],
    url="https://github.com/cfra/wuschl/"
)
