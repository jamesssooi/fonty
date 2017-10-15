"""setup.py: setuptools"""
import re
from setuptools import setup


install_requires = [
    'ansiwrap>=0.8.3',
    'appdirs>=1.4.3',
    'click>=6.7',
    'colorama>=0.3.9',
    'fonttools>=3.13.1',
    'python-dateutil>=2.6.0',
    'requests>=2.17.3',
    'Send2Trash>=1.3.0',
    'termcolor>=1.1.0',
    'textwrap3>=0.9.1',
    'timeago>=1.0.7',
    'Whoosh>=2.7.4',
    'wrapt>=1.10.10'
]


def parse_version():
    '''Parse version from version.py'''
    VERSION_FILE = "fonty/version.py"
    VERSION_PATTERN = r"^__version__\s*=\s*['\"]([^'\"]*)['\"]"

    with open(VERSION_FILE) as f:
        contents = f.read()

    match = re.search(VERSION_PATTERN, contents, re.M)
    if not match:
        raise RuntimeError('Unable to find version string in {}'.format(VERSION_FILE))

    return match.group(1)


setup(
    name='fonty',
    version=parse_version(),
    packages=['fonty'],
    install_requires=install_requires,
    entry_points='''
      [console_scripts]
      fonty=fonty.fonty:main
    ''',
    author='James Ooi',
    author_email='wengteikooi@gmail.com'
)