# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from datetime import date, timedelta
from plone import api
from plone.memoize.view import memoize
from rg.prenotazioni.browser.base import BaseView
from rg.prenotazioni.browser.interfaces import IDontFollowMe
from urllib import urlencode
from zope.interface.declarations import implements


class View(BaseView):
    ''' Display appointments this week
    '''
    implements(IDontFollowMe)

    @property
    @memoize
    def translation_service(self):
        ''' The translation_service tool
        '''
        return getToolByName(self.context, 'translation_service')

    @property
    @memoize
    def localized_time(self):
        ''' Facade for context/@@plone/toLocalizedTime
        '''
        return api.content.get_view('plone',
                                    self.context,
                                    self.request).toLocalizedTime

    def DT2time(self, value):
        '''
        Converts a DateTime in to a localized time
        :param value: a DateTime object
        '''
        return self.localized_time(value, time_only=True)

    @property
    @memoize
    def user_can_manage(self):
        ''' States if the authenticated user can manage this context
        '''
        if api.user.is_anonymous():
            return False
        permissions = api.user.get_permissions(obj=self.context)
        return permissions.get('Modify portal content', False)

    @property
    @memoize
    def periods(self):
        ''' Return the periods
        '''
        if self.user_can_manage:
            return ('morning', 'afternoon', 'stormynight')
        else:
            return ('morning', 'afternoon')

    @property
    @memoize
    def actual_date(self):
        """ restituisce il nome del mese e l'anno della data in request
        """
        day = self.request.get('data', '')
        try:
            day_list = day.split('/')
            data = date(int(day_list[2]), int(day_list[1]), int(day_list[0]))
        except (ValueError, IndexError):
            data = self.prenotazioni.conflict_manager.today
        return data

    @property
    @memoize
    def actual_week_days(self):
        """ The days in this week
        """
        actual_date = self.actual_date
        weekday = actual_date.weekday()
        monday = actual_date - timedelta(weekday)
        return [monday + timedelta(x) for x in range(0, 7)]

    @property
    @memoize
    def actual_translated_month(self):
        ''' The translated Full name of this month
        '''
        return self.translation_service.month(self.actual_date.month)

    @property
    @memoize
    def prev_week(self):
        """ The actual date - 7 days
        """
        return (self.actual_date - timedelta(days=7)).strftime('%d/%m/%Y')

    @property
    @memoize
    def next_week(self):
        """ The actual date + 7 days
        """
        return (self.actual_date + timedelta(days=7)).strftime('%d/%m/%Y')

    @property
    @memoize
    def prev_week_url(self):
        """ The link to the previous week
        """
        qs = {'data': self.prev_week}
        qs.update(self.prenotazioni.remembered_params)
        return "%s?%s" % (self.request.getURL(), urlencode(qs))

    @property
    @memoize
    def next_week_url(self):
        """ The link to the next week
        """
        qs = {'data': self.next_week}
        qs.update(self.prenotazioni.remembered_params)
        return "%s?%s" % (self.request.getURL(), urlencode(qs))

    def __call__(self):
        ''' Hide the portlets before serving the template
        '''
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        return super(View, self).__call__()
