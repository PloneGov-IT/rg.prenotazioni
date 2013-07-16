# -*- coding: utf-8 -*-
"""Main product initializer
"""
from Products.Archetypes import atapi
from Products.CMFCore import utils
from datetime import datetime, timedelta
from logging import getLogger
from os import environ
from rg.prenotazioni import config
from zope.i18nmessageid import MessageFactory
import pytz


prenotazioniMessageFactory = MessageFactory('rg.prenotazioni')
prenotazioniLogger = getLogger('rg.prenotazioni')


def get_environ_tz(default=pytz.utc):
    '''
    Return the environ specified timezone or utc
    '''
    TZ = environ.get('TZ', '')
    if not TZ:
        return default
    return pytz.timezone(TZ)

TZ = get_environ_tz()


def tznow():
    ''' Return a timezone aware now
    '''
    return datetime.now(TZ)


def time2timedelta(value):
    '''
    Transform the value in a timedelta object
    value is supposed to be in the format HH(.*)MM
    '''
    hours, minutes = map(int, (value[0:2], value[-2:]))
    return timedelta(hours=hours, minutes=minutes)


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    # Retrieve the content types that have been registered with Archetypes
    # This happens when the content type is imported and the registerType()
    # call in the content type's module is invoked. Actually, this happens
    # during ZCML processing, but we do it here again to be explicit. Of
    # course, even if we import the module several times, it is only run
    # once.

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types. The initialization process takes
    # care of registering low-level Zope 2 factories, including the relevant
    # add-permission. These are listed in config.py. We use different
    # permissions for each content type to allow maximum flexibility of who
    # can add which content types, where. The roles are set up in rolemap.xml
    # in the GenericSetup profile.

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types=(atype,),
            permission=config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors=(constructor,),
            ).initialize(context)
