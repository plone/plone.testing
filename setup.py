from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "9.0.7"

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

testing_folder = Path("src", "plone", "testing")

setup(
    name="plone.testing",
    version=version,
    description="Testing infrastructure for Zope and Plone projects.",
    long_description=(
        f"{(testing_folder / 'README.rst').read_text()}\n"
        f"{Path('CHANGES.rst').read_text()}\n"
        "Detailed documentation\n======================"
        f"{(testing_folder / 'layer.rst').read_text()}\n"
        f"{(testing_folder / 'zca.rst').read_text()}\n"
        f"{(testing_folder / 'security.rst').read_text()}\n"
        f"{(testing_folder / 'publisher.rst').read_text()}\n"
        f"{(testing_folder / 'zodb.rst').read_text()}\n"
        f"{(testing_folder / 'zope.rst').read_text()}\n"
        f"{(testing_folder / 'zserver.rst').read_text()}\n"
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
