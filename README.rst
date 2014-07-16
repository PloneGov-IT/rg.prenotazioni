A **booking product for Plone** which allows to reserve time slots throughout the week.

.. contents::

Installation
============

Add **rg.prenotazioni** to the egg section of your instance:

::

  [instance]
  eggs=
      ...
      rg.prenotazioni

Introduction
============

This product introduces two new `content types`_ to your Plone site:

.. _content types: http://developer.plone.org/content/types.html

- `Booking`
- `Booking Folder`

Booking content
---------------

**Booking** is a `content type` used to store information about reservation.

The product interface provides a way to add new booking elements,
by clicking on one of the plus signs available in the slots calendar
as shown below:

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-new-booking.png/image_preview
  :alt: The view of Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-new-booking.png

Each booking element once created is storerd into its own **Booking Folder**.


Booking Folder content
----------------------

**Booking Folder** is a folderish content type which store your **Booking** objects.


Using rg.prenotazioni
=====================


Creating a new Booking Folder
-----------------------------

If the product is correctly installed the **Booking Folder** entry is available on the `add new` action menu.
Click on it to add a new booking folder content.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-folder-content-entry.png/image_preview
  :alt: The view of Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-folder-content-entry.png

Saving the form a new booking folder will be created.

Here below the edit page:

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/booking-folder-form.png/image_preview
  :alt: The edit form for a Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/booking-folder-form.png


Since version **2.1** new functionalities has been added to the folder
configuration:

- more then one gate can be handled
- booking vacations supports also bookings with no gate assigned

Since version **3.0** the agenda has:
- a new user interface
- allows custom duration for booking types

Creating a new booking content
------------------------------

Anonymous and authenticated users are allowed to add new booking content
by clicking on the plus signs on the default booking folder view.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/default-view.png/image_preview
  :alt: Link to create new entry
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/default-view.png

After its creation the slot will be displayed as "busy" for anonymous user
and the slot won't be available anymore.

Back-end users can see and manage the reservation according
to the assigned Plone roles.

Here below a screenshot of the edit page:

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-bomking-form.png/image_preview
  :alt: The view of Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-bomking-form.png

Since version **2.1**:
- captcha has been added for anonymous users.
- booking content can be added only from the view folder links.
- booking can't be added in the past anymore.

Backend view
------------

The backend view is quite different from the anonimous user view.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-bomking-form.png/image_preview
  :alt: The view of Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-bomking-form.png

Workflow
--------

The product comes with its own workflow "prenotazioni_workflow".

Since versione **2.1** a new states has been added.
Here below a list of all the states available:

**Private**: booking object initial state:

* `submit` (Automatic transition to pending)

**Pending**

Transaction available:

* `publish` (to published)
* `refuse` (to refused)

**Published**

Transaction available:

* `refuse` (to refused)

**Refused**

Transaction available:

* `restore` (to pending)

Managers can confirm a Booking using workflow transitions.
The workflow transition triggers an email to be sent to the booker (see below).


Content Rules (mail notifications)
----------------------------------

There are additional content rules that can be used to notify booking owner when his booking has been accepted
or re-scheduled.

Rules **are not automatically** as of version **3.x**. They are imported by a separate generic setup profile.

There's also a rule that can warn the Booking Folder responsible when new booking are created, but you need to
manually enable it on folders.


Vacations
---------

You can specify days when the Booking Folder will not accept
bookings.
Those days are called "Vacation days".
Vacation days can be specified compiling the "Vacation days"
field in the Booking Folder edit form.
Values are allowed in the format DD/MM/YYYY.
Instead of the year you can put an asterisk, in this case every here
the day DD of month MM will be considered a vacation day.

It is also possible to specify a vacation period
for a single gate using the vacation booking form.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/vacation-booking-view.png/image_preview
  :alt: The view of Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/vacation-booking-view.png

Searching
---------

Using the prenotazioni_search view it is possible to search
bookings within a given time interval.
You can also filter the results specifying a searchable text,
a gate or a review state.

.. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazioni-search-view.png/image_preview
  :alt: The view of Booking Folder
  :target: http://blog.redturtle.it/pypi-images/rg.prenotazioni/prenotazioni-search-view.png

Notes
=====

**rg.prenotazioni 3.x** has been tested with Plone 4.2 and Plone 4.3 and works with Python 2.7.

**rg.prenotazioni 2.x** has been tested with Plone 4.2 and works with Python 2.6 and 2.7.

**rg.prenotazioni 1.x** has been tested with Plone 3 and works with Python 2.4.

.. Note::
   Version 2.x of rg.prenotazioni is a deep rewrite of version 1.x
   and **we are not providing any migration**... sorry!

TODO
====

* i18n support is uncomplete
* Switch use of session to cookies (**done**)
* Tests!

Credits
=======

Developed with the support of:

* `Unione Reno Galliera`__

  .. image:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/logo-urg.jpg/image_mini
     :alt: Logo Unione Reno Galliera

* `S. Anna Hospital, Ferrara`__

  .. image:: http://www.ospfe.it/ospfe-logo.jpg
     :alt: S. Anna Hospital - logo

* `Comune di Padova`__;

  .. image:: https://raw.githubusercontent.com/PloneGov-IT/pd.prenotazioni/master/docs/logo-comune-pd-150x200.jpg
     :alt: Comune di Padova's logo

All of them supports the `PloneGov initiative`__.

__ http://www.renogalliera.it/
__ http://www.ospfe.it/
__ http://www.padovanet.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
