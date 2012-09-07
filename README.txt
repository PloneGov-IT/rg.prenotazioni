.. contents::

============
Introduction
============

**rg.prenotazioni** is a booking product that allows you to reserve slots of time across the week.

It introduces two archetypes to your Plone site:

- `PrenotazioniFolder`_
- `Prenotazione`_

PrenotazioniFolder
==================

Is a folderish content type that will store your reservations (the content type `Prenotazione`_).

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazionifolderedit.png/image_preview
   :alt: The edit form of PrenotazioniFolder

The edit form of PrenotazioniFolder

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazionifolderview.png/image_preview
   :alt: The view of PrenotazioniFolder

The default view of PrenotazioniFolder

Prenotazione
==================
Clicking on one of the plus signs that are shown in each available calendar slot, you can insert a Prenotazione into your PrenotazioniFolder.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazioneadd.png/image_preview
   :alt: Add PrenotazioniFolder

Features
========

After adding a Prenotazione, non managers users see that the slot is busy, managers 
see in the slot who made the request, alink to the Prenotazione detail and a link to 
move the Prenotazione.

Managers can confirm a Prenotazione using workflow transitions. 
The workflow transition triggers an email to be sent to the booker.

============
Installation
============
 
Add **rg.prenotazioni** to the egg section of your instance::
  
  [instance]
  eggs=
      ...
      rg.prenotazioni
      ...

  zcml=
      ...
      rg.prenotazioni
      ...

=====
Notes
=====
**rg.prenotazioni** has been fully tested only with Plone 3.1.7.
It has been partially tested with Plone 3.3.6. At the moment it **will not work with Plone 4**

**rg.prenotazioni** depends on
`Products.DataGridField <http://plone.org/products/datagridfield>`_, 
which is automatically included in your buildout, so you do not have to take care about it.

Credits
=======

Developed with the support of `Unione Reno Galliera`__ 

  .. image:: https://blog.redturtle.it/pypi-images/rg.prenotazioni/logo-urg.jpg/image_mini
     :alt: Logo Unione Reno Galliera

__ http://www.renogalliera.it/

Unione Reno Galliera supports the `PloneGov initiative`__.

__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/

TODO
====
- Locatlization;
- Porting to recent versions of Plone;