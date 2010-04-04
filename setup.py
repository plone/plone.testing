from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='plone.testing',
      version=version,
      description="Testing infrastructure for Zope and Plone packages",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone zope testing',
      author='Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.testing',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.testing',
          'unittest2',
      ],
      extras_require = {
        'tests': [
                'zope.component',
                'zope.event',
                'zope.publisher',
                'zope.configuration',
                'zope.testbrowser',
            ],
        'zodb': [
                'ZODB3',
            ],
        'zca': [
                'zope.component',
                'zope.event',
                'zope.configuration',
            ],
        'ztk': [
                'zope.component',
                'zope.interface',
                'zope.container',
                'zope.i18n',
                'zope.password',
                'zope.publisher',
                'zope.traversing',
                'zope.security',
                'zope.schema',
                'zope.app.publisher', # XXX: Can probably go away in Zope 2.13
            ],
        'z2': [
                'Zope2',
            ]
      },
      entry_points="""
      """,
      )
