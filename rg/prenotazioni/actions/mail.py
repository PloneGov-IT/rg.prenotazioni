# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.interfaces import ISiteRoot
from collective.contentrules.mailfromfield.actions.mail import (
    IMailFromFieldAction, MailActionExecutor as BaseExecutor)
from plone.contentrules.rule.interfaces import IExecutable
from rg.prenotazioni.content.prenotazione import Prenotazione
from zope.component._declaration import adapts
from zope.interface import Interface
from zope.interface.declarations import implements


class MailActionExecutor(BaseExecutor):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(ISiteRoot, IMailFromFieldAction, Interface)

    def get_mapping(self):
        '''Return a mapping that will replace markers in the template
        extended with the markers:
         - ${gate}
         - ${date}
         - ${subject}
         - ${time}
         - ${type}
        '''
        mapping = super(MailActionExecutor, self).get_mapping()
        event_obj = self.event.object

        if not isinstance(event_obj, Prenotazione):
            return mapping

        mapping['gate'] = event_obj.getGate() or ''
        mapping['subject'] = event_obj.Description() or ''
        mapping['type'] = event_obj.getTipologia_prenotazione() or ''

        event_obj_date = event_obj.Date()
        if not event_obj_date:
            return mapping

        date = DateTime(event_obj.Date())
        plone = self.context.restrictedTraverse('@@plone')
        mapping.update({"date": plone.toLocalizedTime(date),
                        "time": plone.toLocalizedTime(date, time_only=True),
                        })
        return mapping
