# -*- coding: utf-8 -*-
from rg.prenotazioni.browser.base import BaseView


class View(BaseView):
    ''' Display appointments this week
    '''
    def __call__(self):
        ''' Hide the portlets before serving the template
        '''
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        return super(View, self).__call__()
