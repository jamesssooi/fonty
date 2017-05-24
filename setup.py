"""setup.py: setuptools"""
from setuptools import setup

setup(
    name='fonty',
    version='0.1.0',
    packages=['fonty'],
    entry_points='''
      [console_scripts]
      fonty=fonty.fonty:main
    ''',
    author='James Ooi',
    author_email='wengteikooi@gmail.com'
)
