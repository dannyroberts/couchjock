from setuptools import setup

setup(
    name='couchjock',
    version='0.0.1',
    author='Danny Roberts',
    author_email='droberts@dimagi.com',
    description='A python interface for the couchdb',
    long_description='couchjock is a thin wrapper around couchdbkit '
                     'that substitutes jsonobject for couchdbkit.schema',
    url='https://github.com/dannyroberts/couchjock',
    packages=['couchjock'],
    install_requires=[
        'jsonobject',
        'couchdbkit==0.5.7',
    ],
    tests_require=['unittest2'],
    test_suite='test',
)
