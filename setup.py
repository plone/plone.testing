# -*- coding: utf-8 -*-
import os
import os.path
import sys
from setuptools import setup, find_packages

version = '4.3.1'

install_requires = [
    'setuptools',
    'zope.testing',
]


if sys.version_info < (2, 7):
    install_requires.append('unittest2')

tests_require = [
    'zope.component',
    'zope.interface',
    'zope.publisher',
    'zope.security',
    'zope.event',
    'zope.configuration',
    'zope.testbrowser',
    'zope.testrunner',
    'zope.app.publisher',  # XXX: Can probably go away in Zope 2.13
    'ZODB3',
    'Zope2',
]

setup(
    name='plone.testing',
    version=version,
    description="Testing infrastructure for Zope and Plone projects.",
    long_description=(u'\n\n'.join([
        open(os.path.join("src", "plone", "testing", "README.rst")).read(),
        open("CHANGES.rst").read(),
        "Detailed documentation\n" +
        "======================",
        open(os.path.join("src", "plone", "testing", "layer.rst")).read(),
        open(os.path.join("src", "plone", "testing", "zca.rst")).read(),
        open(os.path.join("src", "plone", "testing", "security.rst")).read(),
        open(os.path.join("src", "plone", "testing", "publisher.rst")).read(),
        open(os.path.join("src", "plone", "testing", "zodb.rst")).read(),
        open(os.path.join("src", "plone", "testing", "z2.rst")).read()
    ])),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='plone zope testing',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://github.com/plone/plone.testing',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'zodb': ['ZODB3'],
        'zca': [
            'zope.component',
            'zope.event',
            'zope.configuration',
        ],
        'security': [
            'zope.security',
        ],
        'publisher': [
            'zope.configuration',
            'zope.security',
            'zope.app.publisher',  # XXX: Can probably go away in Zope 2.13
        ],
        'z2': [
            'Zope2',
            'zope.site',
            'zope.testbrowser',
            'zope.publisher',
        ],
    },
)
