# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sample',
    version='0.0.1',
    description='pfr: full-stack OG prep',
    long_description=readme,
    author='AMK',
    author_email='...',
    url='https://github.com/AnnaMag/pdf-flask-react',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
