from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.interface import implements


class IMovedPrenotazione(IObjectEvent):

    """Marker interface for prenotazione that is moved"""


class MovedPrenotazione(ObjectEvent):

    """Event fired when a prenotazione that is moved"""
    implements(IMovedPrenotazione)

    def __init__(self, obj):
        super(MovedPrenotazione, self).__init__(obj)
