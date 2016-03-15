# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize


class ConfView(BrowserView):
    '''
    '''
    date_formats = {
        'it': "dd/mm/yyyy"
    }

    template = """
    (function() {
        if (
            jQuery.tools === undefined ||
            jQuery.tools.dateinput === undefined
        ) {
            return;
        }
        jQuery.tools.dateinput.localize("%(language)s", {
            months: "%(monthnames)s",
            shortMonths: "%(shortmonths)s",
            days: "%(days)s",
            shortDays: "%(shortdays)s",
        });
        jQuery.tools.dateinput.conf.lang = "%(language)s";
        jQuery.tools.dateinput.conf.format = "%(display_format)s";
        jQuery.tools.dateinput.conf.firstDay = %(first_day)s;
    })();
    """

    @property
    @memoize
    def configuration(self):
        ''' Configure jquerytools dateutil
        '''
        language = getattr(self.request, 'LANGUAGE', 'en')
        display_format = self.date_formats.get(language, 'yyyy-mm-dd')
        calendar = self.request.locale.dates.calendars['gregorian']
        # We have to sort the days: sun goes first
        monday_sunday = calendar.getDayNames()
        mon_sun = calendar.getDayAbbreviations()
        day_order = [x % 7 for x in range(-1, 6)]
        return {
            'language': language,
            'display_format': display_format,
            'first_day': calendar.week.get('firstDay', 1),
            'monthnames': ','.join(calendar.getMonthNames()),
            'shortmonths': ','.join(calendar.getMonthAbbreviations()),
            'days': ','.join([monday_sunday[x] for x in day_order]),
            'shortdays': ','.join([mon_sun[x] for x in day_order]),
        }

    def mark_with_class(self, selectors, klass="rg-dateinput"):
        ''' Mark some fields with a class in order for dateutil widget
        to be applied
        '''
        return "\n".join([
            "jQuery('%s').addClass('%s');" % (s, klass) for s in selectors
        ])

    def render(self):
        ''' Render the template
        '''
        return self.template % self.configuration

    def __call__(self):
        ''' Render the template
        '''
        self.request.response.setHeader('content-type',
                                        'text/javascript;;charset=utf-8')
        return self.render()
