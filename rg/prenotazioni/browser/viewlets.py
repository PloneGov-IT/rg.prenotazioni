# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common
from zope.component import getMultiAdapter


class SpostaPrenotazioneViewlet(common.ViewletBase):
    render = ViewPageTemplateFile('spostaprenotazione.pt')

    def update(self):
        # set here the values that you need to grab from the template.
        # stupid example:
        pass

    def display(self):
        """
        la viewlet non deve essere visualizzata quando:
            non sono loggato
            in sessione esiste UID
        """
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u"plone_portal_state")
        if self.portal_state.anonymous():
            return False
        if self.context.REQUEST.SESSION.get('UID', ''):
            return False

        return True


class AnnullaSpostaPrenotazioneViewlet(common.ViewletBase):
    render = ViewPageTemplateFile('annullaspostaprenotazione.pt')

    def update(self):
        # set here the values that you need to grab from the template.
        # stupid example:
        pass

    def display(self):
        """
        la viewlet non deve essere visualizzata quando:
            in sessione non esiste UID
        """

        if self.context.REQUEST.SESSION.get('UID', ''):
            return True
        else:
            return False
