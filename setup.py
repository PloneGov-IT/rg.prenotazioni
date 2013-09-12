# -*- coding: utf-8 -*-
"""
This module contains the tool of rg.prenotazioni
"""
import os
from setuptools import setup, find_packages

version = '2.1'

tests_require = ['zope.testing']

setup(name='rg.prenotazioni',
      version=version,
      description="Booking product for Plone",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Plone',
        'Framework :: Plone :: 3.3',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone plonegov booking',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/rg.prenotazioni',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rg', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'Products.DataGridField',
                        'collective.contentrules.mailfromfield>=0.2.0',
                        'quintagroup.formlib.captcha',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='rg.prenotazioni.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
