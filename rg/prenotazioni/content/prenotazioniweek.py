# -*- coding: utf-8 -*-
from Products.Archetypes import atapi
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.interfaces.prenotazioniweek import IPrenotazioniWeek
from zope.interface import implements

try:
    from plone.app.folder.folder import ATFolder as BaseFolder
    from plone.app.folder.folder import ATFolderSchema as BaseFolderSchema
except ImportError:
    from Products.ATContentTypes.content.folder import ATBTreeFolder as BaseFolder
    from Products.ATContentTypes.content.folder import ATBTreeFolderSchema as BaseFolderSchema

PrenotazioniWeekSchema = BaseFolderSchema.copy()


class PrenotazioniWeek(BaseFolder):
    """Prenotazioni week folder"""
    implements(IPrenotazioniWeek)

    meta_type = "PrenotazioniWeek"
    schema = PrenotazioniWeekSchema

atapi.registerType(PrenotazioniWeek, PROJECTNAME)
