# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope.component import adapts
from zope.interface import implements, Interface


class ISendEmailAction(Interface):
    """Interface for the configurable aspects of a send email action.
    """


class SendEmailAction(SimpleItem):
    """The actual persistent implementation of the action element.
    """
    implements(ISendEmailAction, IRuleElementData)

    element = 'rg.prenotazioni.actions.SendEmail'
    summary = "Send Email to prenotazioni owner"


class SendEmailActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, ISendEmailAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        urltool = getToolByName(aq_inner(self.context), "portal_url")
        portal = urltool.getPortalObject()
        email_charset = portal.getProperty('email_charset')
        # individuo la mail
        mTo = obj.getEmail()
        mFrom = obj.getEmailResponsabile()

        messaggio = """
La sua richiesta di prenotazione è stata confermata per il giorno %s alle ore %s.

Tipologia: %s

Oggetto:
%s
        """ % (
        obj.getData_prenotazione().strftime("%d/%m/%Y"),
        obj.getData_prenotazione().strftime("%H:%M"),
        obj.getTipologia_prenotazione(),
        obj.Description(),
        )

        subject = unicode("Conferma prenotazione ", 'UTF-8')
        mailhost = getToolByName(portal, 'MailHost')
        try:
            # sending mail in Plone 4
            mailhost.send(messaggio, mto=mTo, mfrom=mFrom,
                    subject=subject, charset=email_charset,
                    msg_type='text/plain')
        except:
            #sending mail in Plone 3
            mailhost.secureSend(messaggio, mTo, mFrom,
                    subject=subject, subtype='plain',
                    charset=email_charset, debug=False)

        return True

