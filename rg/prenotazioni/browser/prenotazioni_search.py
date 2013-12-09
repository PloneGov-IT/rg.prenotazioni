# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from five.formlib.formbase import PageForm
from plone.app.form.validators import null_validator
from plone.memoize.view import memoize
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.adapters.conflict import IConflictManager
from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Datetime, TextLine, ValidationError
from zope.formlib.form import setUpWidgets


class InvalidDate(ValidationError):
    __doc__ = _('invalid_end:search_date', u"Invalid start or end date")


def check_date(value):
    '''
    Check if the input date is correct
    '''
    if isinstance(value, datetime):
        return True
    raise InvalidDate


class ISearchForm(Interface):

    """
    Interface for creating a prenotazione
    """
    text = TextLine(
        title=_('label_text', u'Text to search'),
        default=u'',
    )
    start = Datetime(
        title=_('label_start', u'Start date '),
        description=_(" format (YYYY-MM-DD)"),
        default=None,
        constraint=check_date,
    )
    end = Datetime(
        title=_('label_end', u'End date'),
        description=_(" format (YYYY-MM-DD)"),
        default=None,
        constraint=check_date,
    )


class SearchForm(PageForm):
    """
    """
    implements(ISearchForm)
    template = ViewPageTemplateFile('prenotazioni_search.pt')
    prefix = ''
    brains = []

    @property
    @memoize
    def form_fields(self):
        '''
        The fields for this form
        '''
        ff = FormFields(ISearchForm)
        return ff

    @property
    @memoize
    def conflict_manager(self):
        '''
        Return the conflict manager for this context
        '''
        return IConflictManager(self.context)

    def get_brains(self, data):
        '''
        The brains for my search
        '''
        if not self.request.form.get('actions.search'):
            return []
        text = data['text']
        start = DateTime(data['start'])
        end = DateTime(data['end'])
        date = {'query': [start, end], 'range': 'min:max'}
        query = {'SearchableText': text,
                 'Date': date,
                 'sort_on': 'Date',
                 'sort_order': 'reverse',
                 'path': '/'.join(self.context.getPhysicalPath())
                 }
        return self.conflict_manager.unrestricted_prenotazioni(**query)

    def validate(self, action, data):
        '''
        Checks if input dates are correct
        '''
        errors = super(SearchForm, self).validate(action, data)
        return errors

    def setUpWidgets(self, ignore_request=False):
        '''
        From zope.formlib.form.Formbase.
        '''
        self.adapters = {}
        fieldnames = [x.__name__ for x in self.form_fields]
        data = {}
        for key in fieldnames:
            value = self.request.form.get(key)
            if value is not None and not value == u'':
                data[key] = value
                self.request[key] = value

        self.widgets = setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters, ignore_request=ignore_request,
            data=data)

    @action(_('action_search', u'Search'), name=u'search')
    def action_search(self, action, data):
        '''
        Search in prenotazioni SearchableText
        '''
        self.brains = self.get_brains(data)

    @action(_(u"action_cancel", default=u"Cancel"),
            validator=null_validator, name=u'cancel')
    def action_cancel(self, action, data):
        '''
        Cancel and go back to the week view
        '''
        target = self.context.absolute_url()
        return self.request.response.redirect(target)
