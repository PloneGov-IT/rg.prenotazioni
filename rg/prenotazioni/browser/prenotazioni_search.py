# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five.formlib.formbase import PageForm
from plone.app.form.validators import null_validator
from plone.memoize.view import memoize
from rg.prenotazioni import prenotazioniMessageFactory as _
from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Datetime, TextLine


class ISearchForm(Interface):

    """
    Interface for creating a prenotazione
    """
    text = TextLine(
        title=_('label_text', u'Text'),
        default=u'',
    )
    start = Datetime(
        title=_('label_start', u'Start'),
        default=None,
    )
    end = Datetime(
        title=_('label_end', u'End'),
        default=None,
    )


class SearchForm(PageForm):

    """
    """
    implements(ISearchForm)
    template = ViewPageTemplateFile('prenotazioni_search.pt')

    hidden_fields = []

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(ISearchForm)
        return ff

    @action(_('action_search', u'Search'), name=u'search')
    def action_search(self, action, data):
        '''
        Book this resource
        '''

    @action(_(u"action_cancel", default=u"Cancel"),
            validator=null_validator, name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel
        '''
