#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

with open('README.rst') as readme_file:
    readme = readme_file.read()

long_description = ''

setup(
    name='trending_repos',
    version='1.0.0',
    description='Retrieve n top trending python repositories from Github with basic information',
    long_description=readme,
    author='Tal Abramovitch',
    url='https://github.com/talabr/trending_github_repos.git',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'trending_repos=trending_github_repos.trending_repos.cli:main'
        ]
    },
    install_requires=requirements,
    zip_safe=False
)


