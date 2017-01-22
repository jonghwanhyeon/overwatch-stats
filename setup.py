from setuptools import setup, find_packages

setup(
    name='overwatch-stats',
    version='0.2.0',
    description='A library to query a player\'s overwatch stats from Battle.net',
    url='https://github.com/hyeon0145/overwatch-stats',
    author='Jonghwan Hyeon',
    author_email='hyeon0145@gmail.com',
    license='WTFPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Games/Entertainment :: First Person Shooters',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='overwatch stats',
    packages=find_packages(),
    install_requires=['requests', 'lxml', 'inflect'],
)