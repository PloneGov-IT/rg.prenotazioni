# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter, getUtility
from DateTime import DateTime

def setDataPrenotazione(self):
    """
    """
    request = self.REQUEST
    session = request.SESSION
    data = session.get('data_prenotazione','')
    session.set('data_prenotazione','')
    if data:
        data_prenotazione = DateTime(data)
        self.setData_prenotazione(data_prenotazione)
        self.reindexObject()

def afterPrenotazioneCreation(object,event):
    """
    """
    setDataPrenotazione(object)