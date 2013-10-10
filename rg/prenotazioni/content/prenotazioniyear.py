# -*- coding: utf-8 -*-
from Products.Archetypes import atapi
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.content.basefolder import BaseNoNavFolder, BaseFolderSchema
from rg.prenotazioni.interfaces import IPrenotazioniYear
from zope.interface import implements

PrenotazioniYearSchema = BaseFolderSchema.copy()


class PrenotazioniYear(BaseNoNavFolder):

    """Prenotazioni year folder"""
    implements(IPrenotazioniYear)

    meta_type = "PrenotazioniYear"
    schema = PrenotazioniYearSchema

atapi.registerType(PrenotazioniYear, PROJECTNAME)
