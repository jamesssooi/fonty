"""setup.py: setuptools"""
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

setup(
    name='fonty',
    version='0.1.0',
    packages=['fonty'],
    install_requires=install_requires,
    entry_points='''
      [console_scripts]
      fonty=fonty.fonty:main
    ''',
    author='James Ooi',
    author_email='wengteikooi@gmail.com'
)
