# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from datetime import date, timedelta
from plone.memoize.view import memoize
from rg.prenotazioni.browser.base import BaseView


class View(BaseView):
    ''' Display appointments this week
    '''
    @property
    @memoize
    def translation_service(self):
        ''' The translation_service tool
        '''
        return getToolByName(self.context, 'translation_service')

    @property
    @memoize
    def actual_date(self):
        """ restituisce il nome del mese e l'anno della data in request
        """
        day = self.request.get('data', '')
        if day:
            day_list = day.split('/')
            data = date(int(day_list[2]), int(day_list[1]), int(day_list[0]))
        else:
            data = date.today()
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

    @memoize
    def get_day_ranges(self, day):
        ''' Return the time ranges of this day
        '''
        weekday = day.weekday()
        week_table = self.context.getSettimana_tipo()
        day_table = week_table[weekday]
        return {'morning': (day_table['inizio_m'], day_table['end_m']),
                'afternoon': (day_table['inizio_p'], day_table['end_p'])
                }

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

    def empty_week(self):
        """
        Check if we have an empty week
        """
        for d in self.days():
            if d[0]['inizio_m'] != '0' or d[0]['inizio_p'] != '0':
                return False
        return True

    def isValidDay(self, day):
        """ restituisce true se il giorno è valido
        """
        context = self.context
        festivi = context.getFestivi()
        da_data = context.getDaData().strftime('%Y/%m/%d').split('/')
        a_data = context.getAData() and context.getAData().strftime('%Y/%m/%d').split('/')
        date_dadata = date(int(da_data[0]), int(da_data[1]), int(da_data[2]))
        date_adata = None
        if a_data:
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
        if date_adata and day > date_adata:
            return False

        return True

    @memoize
    def days(self):
        """
        Restituisce i giorni della settimana "customizzata" nel formato
        (dict,datetime.date)
        """
        settimana = self.context.getSettimana_tipo()
        weekday = self.actual_date.weekday()

        res = []
        for x, item in enumerate(settimana):
            if item['inizio_m'] or item['inizio_p']:
                giorno = self.actual_date - timedelta(weekday - x)
                if self.isValidDay(giorno):
                    res.append((item, giorno))
        return res

    def get_booking_url(self, day, period):
        ''' Returns, if possible, the booking URL
        '''
        # we have some conditions to check
        if not self.isValidDay(day):
            return ''
        if not all(self.get_day_ranges(day)[period]):
            return ''
        return ('%s/creaPrenotazione?form.booking_date=%s'
                % (self.context.absolute_url(),
                   str(day)
                   )
                )

    def __call__(self):
        ''' Hide the portlets before serving the template
        '''
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        return super(View, self).__call__()
