#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from setuptools import setup, find_packages

setup(
    name="mlscores",
    version="0.1.0",
    description="Multilinguality score of Wikidata and Wikibase items",
    author="John Samuel",
    author_email="johnsamuelwrites@gmail.com",
    url="https://github.com/johnsamuelwrites/mlscores",
    packages=find_packages(),
    install_requires=[
        "sparqlwrapper>=2.0.0",
        "rich>=4.1",
        "tqdm>=4.65.0",
        "urllib3>=1.26.15",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.23.0",
            "pydantic>=2.0.0",
        ],
    },
    python_requires=">=3.8",
)
