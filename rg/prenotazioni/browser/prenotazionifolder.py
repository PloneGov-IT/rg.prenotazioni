# -*- coding: utf-8 -*-
"""Define a browser view for the PrenotazioniFolder content type. In the FTI
configured in profiles/default/types/*.xml, this is being set as the default
view of that content type.
"""
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import timedelta, date


class PrenotazioniFolderView(BrowserView):
    """Default view of a PrenotazioniFolder
    """

    __call__ = ViewPageTemplateFile('prenotazionifolder.pt')

    def days(self):
        """
        Restituisce i giorni della settimana "customizzata" nel formato
        (dict,datetime.date)
        """
        settimana = self.context.getSettimana_tipo()
        data = self.context.REQUEST.get('data', '')
        if data:
            data_list = data.split('/')
            anno = int(data_list[2])
            mese = int(data_list[1])
            giorno = int(data_list[0])
            #giorno=date(2002, 12, 31)
            day = date(anno, mese, giorno)
        else:
            day = date.today()

        weekday = day.weekday()

        res = []
        for x in (range(len(settimana))):
            item = settimana[x]
            diff = weekday - x
            if item['inizio_m'] or item['inizio_p']:
                giorno = day - timedelta(days=diff)
                if self.isValidDay(giorno):
                    res.append((item, giorno))
        return res

    def slots(self, day):
        """ restituisce gli slot disponibili nel giorno indicato
        """
        m = int(day['num_m'])
        p = int(day['num_p'])
        return ([x for x in range(0, m)], [x for x in range(0, p)])

    def getTime(self, day, slot, pm):
        """ restituisce l'ora associata allo slot indicato del giorno
        """
        durata = self.context.getDurata()
        minuti = timedelta(minutes=durata * slot,)
        inizio_m = day['inizio_m']
        inizio_p = day['inizio_p']

        if inizio_m != '0':
            inizio_m_minuti = int(inizio_m[2:4])
            inizio_m_ore = int(inizio_m[0:2])
            inizio_m_time = timedelta(hours=inizio_m_ore,
                                      minutes=inizio_m_minuti,)

        if inizio_p != '0':
            inizio_p_minuti = int(inizio_p[2:4])
            inizio_p_ore = int(inizio_p[0:2])
            inizio_p_time = timedelta(hours=inizio_p_ore,
                                      minutes=inizio_p_minuti,)

        if pm == 'm':
            new_timedelta = inizio_m_time + minuti
        elif pm == 'p':
            new_timedelta = inizio_p_time + minuti

        secondi = new_timedelta.seconds
        ore = secondi / 3600
        minuti = (secondi % 3600) / 60

        return str(ore).zfill(2) + ':' + str(minuti).zfill(2)

    def getPrenotazione(self, day, orario):
        """ restituisce le prenotazioni fissate per il giorno e l'ora indicati
        """
        pc = getToolByName(self.context, 'portal_catalog', None)
        giorno = DateTime(day.strftime('%Y/%m/%d') + ' ' + orario + ':00')
        prenotazioni = pc.unrestrictedSearchResults(
                           portal_type='Prenotazione',
                           getData_prenotazione=giorno,
                           path='/'.join(self.context.getPhysicalPath()
                       )
        )
        if prenotazioni:
            return prenotazioni[0]

        return False

    def displayAggiungiPrenotazione(self, prenotazione):
        """
        """
        if not prenotazione:
            return True
        return False

    def displayPrenotazione(self, prenotazione, member):
        """
        """
        if prenotazione and member.has_permission('Modify portal content',
                                                  self.context):
            return True
        return False

    def uidSpostaAppuntamento(self):
        """
        Se nella request esiste il parametro UID allora si tratta di uno
        spostamento
        """
        res = False
        uid = self.context.REQUEST.SESSION.get('UID', '')
        if uid:
            res = uid

        return res

    def displaySlotOccupato(self, prenotazione, member):
        """
        """
        if prenotazione and not member.has_permission('Modify portal content',
                                                      self.context):
            return True
        return False

    def spanRow(self, day):
        """ restituisce lo span nel caso in cui ci sia orario continuato
        """
        if day['inizio_p'] != '0':
            return 1
        return 2

    def requestData(self):
        """ restituisce il nome del mese e l'anno della data in request
        """
        day = self.context.REQUEST.get('data', '')
        if day:
            day_list = day.split('/')
            data = date(int(day_list[2]), int(day_list[1]), int(day_list[0]))
        else:
            data = date.today()

        return data

    def prevNextWeek(self):
        """ restituisce la data +/- 7
        """
        data = self.requestData()
        lastdata = data - timedelta(days=7)
        nextdata = data + timedelta(days=7)

        return (lastdata.strftime('%d/%m/%Y'), nextdata.strftime('%d/%m/%Y'))

    def isValidDay(self, day):
        """ restituisce true se il giorno è valido
        """
        festivi = self.context.getFestivi()
        da_data = self.context.getDaData().strftime('%Y/%m/%d').split('/')
        a_data = self.context.getAData().strftime('%Y/%m/%d').split('/')
        date_dadata = date(int(da_data[0]), int(da_data[1]), int(da_data[2]))
        date_adata = date(int(a_data[0]), int(a_data[1]), int(a_data[2]))

        res = []

        for festivo in festivi:
            festivo_list = festivo.split('/')
            if len(festivo_list) == 3:
                gg = festivo_list[0]
                mm = festivo_list[1]
                anno = festivo_list[2]
                res.append(date(int(anno), int(mm), int(gg)))

        if day in res:
            return False
        if day < date_dadata:
            return False
        if day > date_adata:
            return False

        return True


class CreatePrenotazione(BrowserView):
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args):
        data = self.request.get('data_prenotazione', '')
        self.request.SESSION.set('data_prenotazione', data)
        self.request.RESPONSE.redirect("createObject?type_name=Prenotazione")


class MovePrenotazione(BrowserView):
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args):
        uid = self.request.get('UID', '')
        self.request.SESSION.set('UID', uid)
        pu = getToolByName(self.context, 'plone_utils')
        msg = 'Seleziona la data nella quale spostare l\'appuntamento'
        pu.addPortalMessage(msg)
        self.request.RESPONSE.redirect(self.context.absolute_url())


class SavePrenotazione(BrowserView):
    """
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args):
        data = self.request.get('data_prenotazione', '')
        uid = self.request.SESSION.get('UID', '')
        self.request.SESSION.set('UID', '')
        pc = getToolByName(self.context, 'portal_catalog')
        pu = getToolByName(self.context, 'plone_utils')
        if uid:
            appuntamenti = pc(portal_type='Prenotazione', UID=uid)
            if appuntamenti:
                appuntamento = appuntamenti[0]
                obj = appuntamento.getObject()
                data_prenotazione = DateTime(data)
                obj.setData_prenotazione(data_prenotazione)
                obj.reindexObject()
                msg = ('Appuntamento spostato correttamente.')
            else:
                msg = ('Problemi con lo spostamento. '
                       'Contatta l\'amministratore.')
            pu.addPortalMessage(msg)
        self.request.RESPONSE.redirect(self.context.absolute_url())


class CancelSpostamento(BrowserView):
    """ cancella il valore di UID dalla sessione
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, *args):
        self.request.SESSION.set('UID', '')
        self.request.RESPONSE.redirect(self.context.absolute_url())
