# -*- coding: utf-8 -*-
from Products.Archetypes import atapi
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.content.basefolder import BaseNoNavFolder, BaseFolderSchema
from rg.prenotazioni.interfaces.prenotazioniweek import IPrenotazioniWeek
from zope.interface import implements


PrenotazioniWeekSchema = BaseFolderSchema.copy()


class PrenotazioniWeek(BaseNoNavFolder):

    """Prenotazioni week folder"""
    implements(IPrenotazioniWeek)

    meta_type = "PrenotazioniWeek"
    schema = PrenotazioniWeekSchema


atapi.registerType(PrenotazioniWeek, PROJECTNAME)
