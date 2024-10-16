# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""invenio data model for Learning object metadata"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "elasticsearch_dsl>=7.2.1",
    "invenio-app>=1.3.0,<2.0.0",
    "pytest-invenio>=1.4.0,<2.0.0",
]

# Should follow inveniosoftware/invenio versions
invenio_db_version = ">=1.0.9,<2.0.0"
invenio_search_version = ">=1.4.2,<2.0.0"

extras_require = {
    "docs": [
        "Sphinx>=3",
    ],
    # Elasticsearch version
    "elasticsearch7": [
        "invenio-search[elasticsearch7]{}".format(invenio_search_version),
    ],
    # Database
    "postgresql": [
        "invenio-db[postgresql,versioning]{}".format(invenio_db_version),
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for name, reqs in extras_require.items():
    if name[0] == ":" or name in ("elasticsearch7", "postgresql"):
        continue
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=1.3",
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "invenio-jsonschemas>=1.1.3",
    "invenio-previewer>=1.3.4",
    "invenio-records-rest>=1.8.0",
    "invenio_rdm_records>=0.32.3,<0.33",
    # these indirect dependencies are given for faster dependency tree resolution:
    "celery>=5.0.5",
    "cffi>=1.14.6",
    "cryptography>=3.4.7",
    "dnspython>=2.1.0",
    "email-validator>=1.1.3",
    "faker>=8.12.1",
    "flask>=1.1.4,<2.0.0",
    "flask-login>=0.4.1",
    "flask-menu>=0.7.2",
    "flask-principal>=0.4.0",
    "fs>=0.5.4",
    "future>=0.18.2",
    "idna>=3.2",
    "idutils>=1.1.7",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_records_lom", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio_records_lom",
    version=version,
    description=__doc__,
    long_description=readme,
    keywords="invenio_records_lom Invenio lom Learning object metadata records",
    license="MIT",
    author="Graz University of Technology",
    author_email="mb_wali@hotmail.com",
    url="https://github.com/tu-graz-library/invenio-records-lom/",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "flask.commands": [
            "lom = invenio_records_lom.cli:lom",
        ],
        "invenio_base.apps": [
            "invenio_records_lom = invenio_records_lom:InvenioRecordsLOM",
        ],
        "invenio_base.api_apps": [
            "invenio_records_lom = invenio_records_lom:InvenioRecordsLOM",
        ],
        "invenio_base.blueprints": [
            "invenio_records_lom_ui = invenio_records_lom.ui:create_blueprint",
            "invenio_records_lom_resource_registerer = invenio_records_lom.views:blueprint",
        ],
        "invenio_base.api_blueprints": [
            "invenio_records_lom_records = invenio_records_lom.views:create_records_bp",
        ],
        "invenio_jsonschemas.schemas": [
            "invenio_records_lom = invenio_records_lom.jsonschemas",
        ],
        "invenio_search.mappings": [
            "lomrecords = invenio_records_lom.records.mappings",
        ],
        "invenio_config.module": [
            "invenio_records_lom = invenio_records_lom.config",
        ],
        "invenio_pidstore.fetchers": [
            "lomid = invenio_records_lom.fetchers:lom_pid_fetcher",
        ],
        "invenio_pidstore.minters": [
            "lomid = invenio_records_lom.minters:lom_pid_minter",
        ],
        "invenio_db.models": [
            "invenio_records_lom = invenio_records_lom.records.models",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
