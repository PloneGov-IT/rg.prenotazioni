# -*- coding: utf-8 -*-
"""
This module contains the tool of rg.prenotazioni
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.0.2'

long_description = (
    read('README.txt')
    + '\n\n' +
    read('docs', 'HISTORY.txt')
    + '\n' +
    '========\n'
    'Download\n'
    '========\n'
    )

tests_require = ['zope.testing']

setup(name='rg.prenotazioni',
      version=version,
      description="Prenotazioni product for Unione Reno Galliera",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='http://plone.org/products/rg.prenotazioni',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rg', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'Products.DataGridField<1.7',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='rg.prenotazioni.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
#      setup_requires=["PasteScript"],
#      paster_plugins = ["ZopeSkel"],
      )
