from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='overwatch-stats',
    version='0.1.0',
    description='A library to query a player\'s overwatch stats from Battle.net',
    long_description=long_description,
    url='https://github.com/hyeon0145/overwatch-stats',
    author='Jonghwan Hyeon',
    author_email='hyeon0145@gmail.com',
    license='WTFPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment :: First Person Shooters',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='overwatch stats',
    packages=find_packages(),
    install_requires=['requests', 'beautifulsoup4'],
)