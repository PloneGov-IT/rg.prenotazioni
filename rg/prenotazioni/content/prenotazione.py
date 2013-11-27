# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import base, schemata
from Products.Archetypes import atapi
from Products.Archetypes.ExtensibleMetadata import _zone
from Products.CMFCore import permissions
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.event import booking_created
from rg.prenotazioni.interfaces import IPrenotazione, IPrenotazioniFolder
from zope.interface import implements


OVERBOOKED_MESSAGE = _('overbook_message',
                       default=u"Siamo spiacenti, "
                       u"è già stato preso un appuntamento "
                       u"nella stessa fascia oraria, "
                       u"premere il pulsante "
                       u"ANNULLA per effettuare una nuova richiesta di "
                       u"prenotazione")


PrenotazioneSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.StringField(
        'email',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label="email",
            validator=('isEmail',),
        ),
        required=True,
    ),
    atapi.StringField(
        'telefono',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Telefono"),
            description=_(u"Numero di telefono fisso"),
        ),
        required=False,
    ),
    atapi.StringField(
        'mobile',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Mobile"),
            description=_(u"Numero di cellulare"),
        ),
        required=False,
    ),
    atapi.StringField(
        'tipologia_prenotazione',
        storage=atapi.AnnotationStorage(),
        vocabulary_factory='rg.prenotazioni.tipologies',
        widget=atapi.SelectionWidget(
            label=_(u"Tipologia della prenotazione"),
        ),
        required=False,
    ),
    atapi.DateTimeField(
        'data_prenotazione',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Data prenotazione'),
            visible={'edit': 'hidden', 'view': 'visible'},
        ),
        required=True,
    ),
    atapi.StringField(
        'azienda',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Azienda"),
            description=_(u"Inserisci la denominazione dell'azienda "
                          u"del richiedente"),
        ),
        required=False,
    ),
    atapi.StringField(
        'gate',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Sportello"),
            description=_(u"Sportello a cui presentarsi"),
        ),
        required=False,
    ),
    atapi.DateTimeField(
        'data_scadenza',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Data scadenza prenotazione'),
            visible={'edit': 'hidden', 'view': 'visible'},
        ),
        required=True,
    ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PrenotazioneSchema['title'].storage = atapi.AnnotationStorage()
PrenotazioneSchema['title'].widget.label = _(u"Nome e Cognome")
PrenotazioneSchema['title'].widget.description = _(u"")
PrenotazioneSchema['title'].searchable = True

PrenotazioneSchema['description'].storage = atapi.AnnotationStorage()
PrenotazioneSchema['description'].isMetadata = False
PrenotazioneSchema['description'].widget.label = _(u"Oggetto")
PrenotazioneSchema['description'].widget.description = _(u"")
PrenotazioneSchema['description'].searchable = True

PrenotazioneSchema['location'].widget.modes = []
PrenotazioneSchema['location'].schemata = 'default'
PrenotazioneSchema['subject'].widget.modes = []
PrenotazioneSchema['subject'].schemata = 'default'
PrenotazioneSchema['relatedItems'].widget.modes = []
PrenotazioneSchema['relatedItems'].schemata = 'default'
PrenotazioneSchema['language'].widget.modes = []
PrenotazioneSchema['language'].schemata = 'default'
PrenotazioneSchema['effectiveDate'].widget.modes = []
PrenotazioneSchema['effectiveDate'].schemata = 'default'
PrenotazioneSchema['expirationDate'].widget.modes = []
PrenotazioneSchema['expirationDate'].schemata = 'default'
PrenotazioneSchema['creators'].widget.modes = []
PrenotazioneSchema['creators'].schemata = 'default'
PrenotazioneSchema['contributors'].widget.modes = []
PrenotazioneSchema['contributors'].schemata = 'default'
PrenotazioneSchema['rights'].widget.modes = []
PrenotazioneSchema['rights'].schemata = 'default'
PrenotazioneSchema['allowDiscussion'].widget.modes = []
PrenotazioneSchema['allowDiscussion'].schemata = 'default'
PrenotazioneSchema['excludeFromNav'].widget.modes = []
PrenotazioneSchema['excludeFromNav'].schemata = 'default'


class Prenotazione(base.ATCTContent):

    """Description of the Example Type"""
    implements(IPrenotazione)

    security = ClassSecurityInfo()

    meta_type = "Prenotazione"
    schema = PrenotazioneSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    exclude_from_nav = True

    def getPrenotazioniFolder(self):
        """Ritorna l'oggetto prenotazioni folder"""

        for parent in self.aq_chain:
            if IPrenotazioniFolder.providedBy(parent):
                return parent
        raise Exception("Could not find Prenotazioni Folder "
                        "in acquisition chain of %r" % self)

    def getEmailResponsabile(self):
        """
        """
        return self.getPrenotazioniFolder().getEmail_responsabile()

    security.declareProtected(permissions.View, 'Date')

    def Date(self, zone=None):
        """
        Dublin Core element - default date
        """
        # Return reservation date
        if zone is None:
            zone = _zone
        data_prenotazione = self.getField('data_prenotazione').get(self)
        if data_prenotazione:
            return data_prenotazione.toZone(zone).ISO()

    def _postCopy(self, container, op=0):
        '''
        Customizing the method from CopySupport.py

        Called after the copy is finished to fire the automatic transition.
        The op var is 0 for a copy, 1 for a move.

        The original method does nothing
        '''
        booking_created(self, None)
        return super(Prenotazione, self)._postCopy(container, op)

atapi.registerType(Prenotazione, PROJECTNAME)
