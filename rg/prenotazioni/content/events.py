# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


def setDataPrenotazione(self):
    """
    """
    request = self.REQUEST
    session = request.SESSION
    data = session.get('data_prenotazione', '')
    session.set('data_prenotazione', '')
    if data:
        data_prenotazione = DateTime(data)
        self.setData_prenotazione(data_prenotazione)
        self.reindexObject()


def sendEmail(self):
    """
    """
    portal = getMultiAdapter((self, self.REQUEST),
                                name=u'plone_portal_state').portal()
    mailFrom = portal.email_from_address
    mailTo = self.aq_parent.getEmail_responsabile()
    mailSubject = "Nuova richiesta prenotazione"
    mailMessage = "E' stata inserita una nuova richiesta prenotazione da %s,\
        <br /> %s <br /> <a href='%s'>Link all richiesta</a>" \
            % (
                self.Title(),
                self.Description(),
                self.absolute_url())

    mailHost = getToolByName(self, 'MailHost')
    mailHost.secureSend(mailMessage, mailTo, mailFrom, subject=mailSubject,
                                subtype='html', charset='utf-8', debug=False)


def afterPrenotazioneCreation(obj, event):
    """
    """
    setDataPrenotazione(obj)
    #sendEmail(object)
