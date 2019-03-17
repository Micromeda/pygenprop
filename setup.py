#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2018)

Description: Setup for installing pygenprop.
"""

from setuptools import setup

setup(name='pygenprop',
      version='0.5',
      description='A python library for programmatic usage of EBI InterPro Genome Properties.',
      url='https://github.com/Micromeda/pygenprop',
      author='Lee Bergstrand',
      author_email='lee.h.bergstrand@gmail.com',
      license='Apache License 2.0',
      packages=['pygenprop'],
      install_requires=[
          'Cython>=0.28.5',
          'pandas>=0.23.4',
      ],
      zip_safe=False)
