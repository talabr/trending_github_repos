from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = ''

setup(
    name='Trending Repos',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'main = trending_repos.trending_repos.main:main'
        ]
    },
    install_requires=requirements,
    zip_safe=False
)
