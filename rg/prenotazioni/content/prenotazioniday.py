# -*- coding: utf-8 -*-
from Products.Archetypes import atapi
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.content.basefolder import BaseNoNavFolder, BaseFolderSchema
from rg.prenotazioni.interfaces import IPrenotazioniDay
from zope.interface import implements

PrenotazioniDaySchema = BaseFolderSchema.copy()


class PrenotazioniDay(BaseNoNavFolder):

    """Prenotazioni day folder"""
    implements(IPrenotazioniDay)

    meta_type = "PrenotazioniDay"
    schema = PrenotazioniDaySchema

atapi.registerType(PrenotazioniDay, PROJECTNAME)
