#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: Setup for installing pygenprop.
"""

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setup(name='pygenprop',
      version='0.8',
      description='A python library for programmatic usage of EBI InterPro Genome Properties.',
      url='https://github.com/Micromeda/pygenprop',
      author='Lee Bergstrand',
      author_email='lee.h.bergstrand@gmail.com',
      license='Apache License 2.0',
      packages=['pygenprop'],
      install_requires=[
          'numpy>=1.13.3'
          'Cython>=0.29.13',
          'pandas>=0.25.0,<1.0.0',
          'sqlalchemy>=1.3.12',
          'scikit-bio>=0.5.5'
      ],
      scripts=['bin/pygenprop'],
      zip_safe=True,
      long_description=long_description,
      long_description_content_type='text/markdown')
