Introduction
============

Tests for rg.prenotazioni
-------------------------

All the tests pass ;)

    >>> pass


Periods
=======

We have three periods every day:
* mornig
* afternoon
* stormynight

The last one is visible only by booking operators (editors on the folder).

Test urlify
===========

    >>> from rg.prenotazioni.utilities.urls import urlify
    >>> urlify('http://www.redturtle.it/')
    'http://www.redturtle.it/'
    >>> urlify('http://www.redturtle.it/', 'test')
    'http://www.redturtle.it/test'
    >>> urlify('http://www.redturtle.it/', 'test/')
    'http://www.redturtle.it/test/'
    >>> urlify('http://www.redturtle.it/', ['test'])
    'http://www.redturtle.it/test'
    >>> urlify('http://www.redturtle.it/', ['/test', ''])
    'http://www.redturtle.it/test/'
    >>> urlify(paths='test')
    'test'
    >>> urlify(paths='test/')
    'test/'
    >>> urlify('http://www.redturtle.it/', params={'q': 'redturtle'})
    'http://www.redturtle.it/?q=redturtle'

