from setuptools import find_packages
from setuptools import setup

import os
import os.path


version = "9.0.2"

install_requires = [
    "setuptools",
    "zope.testing >= 3.8",
]

tests_require = [
    "WebTest",
    "Zope",
    "zope.testbrowser",
    "zope.testrunner",
]

zope_requires = (
    [
        "WebTest",
        "Zope",
        "zope.testbrowser",
    ],
)


setup(
    name="plone.testing",
    version=version,
    description="Testing infrastructure for Zope and Plone projects.",
    long_description=(
        "\n\n".join(
            [
                open(os.path.join("src", "plone", "testing", "README.rst")).read(),
                open("CHANGES.rst").read(),
                "Detailed documentation\n" + "======================",
                open(os.path.join("src", "plone", "testing", "layer.rst")).read(),
                open(os.path.join("src", "plone", "testing", "zca.rst")).read(),
                open(os.path.join("src", "plone", "testing", "security.rst")).read(),
                open(os.path.join("src", "plone", "testing", "publisher.rst")).read(),
                open(os.path.join("src", "plone", "testing", "zodb.rst")).read(),
                open(os.path.join("src", "plone", "testing", "zope.rst")).read(),
                open(os.path.join("src", "plone", "testing", "zserver.rst")).read(),
            ]
        )
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Testing",
    ],
    keywords="plone zope testing",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://github.com/plone/plone.testing",
    license="BSD",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        "test": tests_require,
        "zodb": ["ZODB"],
        "zca": [
            "zope.component",
            "zope.configuration",
            "zope.event",
        ],
        "security": [
            "zope.security",
        ],
        "publisher": [
            "zope.browsermenu",
            "zope.browserpage",
            "zope.browserresource",
            "zope.configuration",
            "zope.publisher",
            "zope.security",
        ],
        "z2": [],  # BBB
        "zope": zope_requires,
        "zserver": [
            "ZServer",
        ],
    },
)
