"""setup.py: setuptools"""
import re
from setuptools import setup, find_packages


install_requires = [
    'ansiwrap>=0.8.3',
    'appdirs>=1.4.3',
    'brotlipy>=0.7.0',
    'click>=6.7',
    'colorama>=0.3.9',
    'distro>=1.2.0; platform_system=="Linux"',
    'fonttools>=3.13.1',
    'pypiwin32>=220; platform_system=="Windows"',
    'python-dateutil>=2.6.0',
    'requests>=2.17.3',
    'Send2Trash>=1.3.0; platform_system=="Darwin"',
    'termcolor>=1.1.0',
    'textwrap3>=0.9.1',
    'timeago>=1.0.7',
    'winshell>=0.6.0; platform_system=="Windows"',
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


def get_long_description():
    '''Reads the README.rst file contents.'''
    with open('README.rst', encoding='utf8') as f:
        return f.read()


setup(
    name='fonty',
    version=parse_version(),
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points='''
      [console_scripts]
      fonty=fonty.fonty:main
    ''',
    author='James Ooi',
    author_email='wengteikooi@gmail.com',
    url='https://github.com/jamesssooi/fonty',
    description='fonty is a command line tool for installing, managing and converting fonts.',
    long_description=get_long_description(),
    license='Apache License 2.0',
    keywords='font fonts typeface cli tool install uninstall convert manage',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ]
)
