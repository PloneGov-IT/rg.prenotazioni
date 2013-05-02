A **booking product for Plone** that allows you to reserve slots of time across the week.

.. contents::

============
Introduction
============

This product introduces two new contents to your Plone site:

- `Booking Folder`_
- `Booking`_

Booking Folder
==============

Is a folderish content type that will store your reservations (the content type `Booking`_).

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazionifolderedit.png/image_preview
   :alt: The edit form of PrenotazioniFolder

The edit form of Booking Folder

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazionifolderview.png/image_preview
   :alt: The view of Booking Folder

The default view of Booking Folder

Booking
=======

Clicking on one of the plus signs that are shown in each available calendar slot,
you can insert a Booking into your Booking Folder.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazioneadd.png/image_preview
   :alt: Add Booking

Features
========

After adding a Booking, non managers users see that the slot is busy, managers 
see in the slot who made the request, alink to the Booking detail and a link to 
move the Booking.

Managers can confirm a Booking using workflow transitions. 
The workflow transition triggers an email to be sent to the booker.

============
ContentRules
============

There are an additional contentrule that can be used to notify booking owner when his booking has been rescheduled.
There is a trigger event for contentrules called "Booking moved" that will be triggered when a
booking is rescheduled by an admin.

There is also a new action that allows to configure a mail that will be sent to the booking owner.

============
Installation
============
 
Add **rg.prenotazioni** to the egg section of your instance:

.. code-block:: ini

  [instance]
  eggs=
      ...
      rg.prenotazioni

Notes
=====

**rg.prenotazioni** has been fully tested only with Plone 3.1.7.
It has been partially tested with Plone 3.3.6.

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
