# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFPlone import PloneMessageFactory as __
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from five.formlib.formbase import PageForm
from plone import api
from plone.app.form.validators import null_validator
from plone.app.search.browser import quote_chars
from plone.memoize.view import memoize
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.adapters.conflict import IConflictManager
from zope.formlib.form import FormFields, action
from zope.interface import Interface
from zope.interface.declarations import implements
from zope.schema import Choice, Datetime, TextLine, ValidationError
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
        required=False,
    )
    review_state = Choice(
        title=__("State"),
        default='',
        required=False,
        source='rg.prenotazioni.booking_review_states'
    )
    gate = Choice(
        title=_("label_gate", u"Gate"),
        default='',
        required=False,
        source='rg.prenotazioni.gates'
    )
    start = Datetime(
        title=_('label_start', u'Start date '),
        description=_(" format (YYYY-MM-DD)"),
        default=None,
        constraint=check_date,
        required=False,
    )
    end = Datetime(
        title=_('label_end', u'End date'),
        description=_(" format (YYYY-MM-DD)"),
        default=None,
        constraint=check_date,
        required=False,
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

    @property
    @memoize
    def prenotazioni_week_view(self):
        '''
        Return the conflict manager for this context
        '''
        return api.content.get_view('prenotazioni_week_view',
                                    self.context,
                                    self.request)

    def get_query(self, data):
        ''' The query we requested
        '''
        query = {
            'sort_on': 'Date',
            'sort_order': 'reverse',
            'path': '/'.join(self.context.getPhysicalPath())
        }
        if data.get('text'):
            query['SearchableText'] = quote_chars(data['text'].encode('utf8'))
        if data.get('review_state'):
            query['review_state'] = data['review_state']
        if data.get('gate'):
            query['Subject'] = "Gate: %s" % data['gate'].encode('utf8')
        start = data['start']
        end = data['end']
        if start and end:
            query['Date'] = {'query': [DateTime(start), DateTime(end) + 1],
                             'range': 'min:max'}
        elif start:
            query['Date'] = {'query': DateTime(start), 'range': 'min'}
        elif end:
            query['Date'] = {'query': DateTime(end) + 1, 'range': 'max'}
        return query

    def get_brains(self, data):
        '''
        The brains for my search
        '''
        if not self.request.form.get('actions.search'):
            return []
        query = self.get_query(data)
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
            form_value = self.request.form.get(key)
            if form_value is not None and not form_value == u'':
                field = self.form_fields[key].field
                if isinstance(field, Choice):
                    try:
                        data[key] = (field.bind(self.context).vocabulary
                                     .getTermByToken(form_value).value)
                    except LookupError:
                        data[key] = form_value
                else:
                    data[key] = form_value
                self.request[key] = form_value

        self.widgets = setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, adapters=self.adapters, ignore_request=ignore_request,
            data=data)
        self.widgets['gate']._messageNoValue = ""
        self.widgets['review_state']._messageNoValue = ""

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

    def extra_script(self):
        ''' The scripts needed for the search
        '''
        view = api.content.get_view(
            'rg.prenotazioni.dateinput.conf.js',
            self.context,
            self.request,
        )
        return view.render() + view.mark_with_class(['#start', '#end'])
