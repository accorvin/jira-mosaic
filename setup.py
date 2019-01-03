#! /usr/bin/env python3

from setuptools import find_packages, setup

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

setup(name='mosaic',
      version='1.0',
      description='Mosaic tool for JIRA reporting',
      author='Alex Corvin',
      author_email='acorvin@redhat.com',
      packages=find_packages(),
      install_requires=requirements,
      entry_points={
          'console_scripts': ['mosaic=mosaic.mosaic:main']
      })
