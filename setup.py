"""Setup for EOC Journal XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='xblock-eoc-journal',
    version='0.10.1',
    description='End of Course Journal XBlock',
    packages=[
        'eoc_journal',
    ],
    install_requires=[
        'XBlock',
        'xblock-utils',
        'edx-rest-api-client>=5.2.1,<5.3.0',
        'reportlab==3.5.55',
        'future',
        'six'
    ],
    extras_require={
        ":python_version<'3'": [
            "xblock-problem-builder<4"
        ],
        ":python_version>='3'": [
            "xblock-problem-builder>=4.1.5"
        ]
    },
    entry_points={
        'xblock.v1': [
            'eoc-journal = eoc_journal:EOCJournalXBlock',
        ]
    },
    package_data=package_data("eoc_journal", ["public", "templates"]),
)
