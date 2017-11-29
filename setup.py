from setuptools import setup, find_packages

setup(
    name='overwatch-stats',
    version='1.0.1',
    description='A library to query a player\'s overwatch stats from Battle.net',
    url='https://github.com/jonghwanhyeon/overwatch-stats',
    author='Jonghwan Hyeon',
    author_email='hyeon0145@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Games/Entertainment :: First Person Shooters',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='overwatch stats',
    packages=find_packages(),
    install_requires=['requests', 'lxml', 'inflect'],
)
