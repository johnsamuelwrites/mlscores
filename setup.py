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
    install_requires=["sparqlwrapper", "rich"],  # External dependencies
)
