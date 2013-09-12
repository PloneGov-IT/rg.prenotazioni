A **booking product for Plone** which allows to reserve time slots throughout the week.

.. contents::

Introduction
============

This product introduces two new `content type`_ to your Plone site:

.. _content type: http://developer.plone.org/content/types.html

- `Booking`
- `Booking Folder`

Booking content
---------------

**Booking** is a `content type` used to store information about reservation.

| The product interface provides a way to add new booking elements,
| by clicking on one of the plus signs available in the slots calendar
| as shown below:

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-new-booking.png/image_preview
  :alt: The view of Booking Folder

Each booking element once created is storerd into its own **Booking Folder**.


Booking Folder content
----------------------

| **Booking Folder** is a folderish content type which store your **Booking** objects.
| It is therefore possible to have more of an "agenda".

Using rg.prenotazioni
=====================


Creating a new booking folder content
-------------------------------------

| If the product is correctly installed the **booking folder** entry is available on the `add new` action menu.
| Click on it to add a new booking folder content.

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-folder-content-entry.png/image_preview
  :alt: The view of Booking Folder

Saving the form a new booking folder will be created.

Here below the edit page:

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/booking-folder-form.png/image_preview
  :alt: The view of Booking Folder


Since versrion **2.1** new functionalies has been added to the folder configuraion:

- more then one gate can be handled
- booking vacations supports also gateless bookings


Creating a new booking content
------------------------------

| Anonymous and authenticated users are allowed to add new booking content
| by clicking on the plus signs on the default booking folder view.

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/default-view.png/image_preview
  :alt: Link to create new entry

After its creation the slot will be displayed as "busy" for anonymous user
and the slot won't be available anymore.

Back-end user can see and manage the reservation
according with its Plone rights.

Here below a screenshot of the edit page:

.. figure:: http://blog.redturtle.it/pypi-images/rg.prenotazioni/add-bomking-form.png/image_preview
  :alt: The view of Booking Folder

Since versrion **2.1**:
- captcha has been added for anonymous users.
- booking content can be added only from the view folder links.
- booking can't be added in the past anymore.


Workflow
--------

The product comes with its own workflow "prenotazioni_workflow".

| Since versione **2.1** a new states has been added.
| Here below a list of all the states available:

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

Rules are automatically created and enabled. See the Rule control panel to change settings.

There's also a rule that can warn the Booking Folder responsible when new booking are created, but you need to
manually enable it on folders. 


Installation
============
 
Add **rg.prenotazioni** to the egg section of your instance:

::

  [instance]
  eggs=
      ...
      rg.prenotazioni

Notes
=====

**rg.prenotazioni** has been tested only with Plone 3.3 and Plone 4.2.

.. Note::
   Version 2.x of rg.prenotazioni is a deep rewrite of version 1.x and **we are not providing any
   migration**... sorry!

TODO
====

* i18n support is uncomplete
* Switch use of session to cookies
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

All of them supports the `PloneGov initiative`__.

__ http://www.renogalliera.it/
__ http://www.ospfe.it/
__ http://www.plonegov.it/

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/