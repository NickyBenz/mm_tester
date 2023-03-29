# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='mm_tester',
    version='0.1.0',
    description='Backtesting software for market making',
    long_description=readme,
    author='Pravin Bezwada',
    author_email='pravin.bezwada@gmail.com.com',
    url='https://github.com/satyapravin/mm_tester',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

