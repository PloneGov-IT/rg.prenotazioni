# -*- coding: utf-8 -*-
from rg.prenotazioni.adapters.booker import IBooker


def reallocate_gate(obj):
    '''
    We have to reallocate the gate for this object
    '''
    container = obj.object.getPrenotazioniFolder()
    booking_date = obj.object.getData_prenotazione()
    new_gate = IBooker(container).get_available_gate(booking_date)
    obj.object.setGate(new_gate)


def reallocate_container(obj):
    '''
    If we moved Prenotazione to a new week we should move it
    '''
    container = obj.object.getPrenotazioniFolder()
    IBooker(container).fix_container(obj.object)
