from setuptools import setup, find_packages
import os

version = '0.8'

setup(name='pmr2.virtuoso',
      version=version,
      description="Virtuoso support for PMR2",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Tommy Yu',
      author_email='tommy.yu@auckland.ac.nz',
      url='https://github.com/PMR2/pmr2.virtuoso',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pmr2'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'pmr2.app',
          'pmr2.rdf',
          'rdflib-jsonld==0.4.0',
          'virtuoso==0.12.6pmr2',
          'sqlalchemy>=0.6.0',
          'requests>=1.0.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
