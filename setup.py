# -*- coding: utf-8 -*-
import os
import os.path
import sys
from setuptools import setup, find_packages

version = '6.1.dev0'

install_requires = [
    'setuptools',
    'six',
    'zope.testing',
]

tests_require = [
    'ZODB3',
    'zope.browsermenu',
    'zope.browserpage',
    'zope.browserresource',
    'zope.component',
    'zope.configuration',
    'zope.event',
    'zope.interface',
    'zope.publisher',
    'zope.security',
    'zope.testbrowser',
    'zope.testrunner',
    'Zope',
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
        open(os.path.join("src", "plone", "testing", "zope.rst")).read(),
        open(os.path.join("src", "plone", "testing", "zserver.rst")).read(),
    ])),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone",
        "Framework :: Zope :: 4",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Testing",
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
            'zope.browsermenu',
            'zope.browserpage',
            'zope.browserresource',
            'zope.publisher',
        ],
        'z2': [
            'Zope',
            'ZServer',
            'zope.component',
            'zope.testbrowser',
            'zope.publisher',
        ],
    },
)
