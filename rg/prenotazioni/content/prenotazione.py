# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import base, schemata
from Products.Archetypes import atapi
from Products.Archetypes.ExtensibleMetadata import _zone
from Products.CMFCore import permissions
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.config import PROJECTNAME
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
        searchable=True,
        default='',
    ),
    atapi.StringField(
        'telefono',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_("Phone number"),
        ),
        searchable=True,
        default='',
    ),
    atapi.StringField(
        'mobile',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_("mobile", u"Mobile number"),
        ),
        searchable=True,
        default='',
    ),
    atapi.StringField(
        'tipologia_prenotazione',
        storage=atapi.AnnotationStorage(),
        vocabulary_factory='rg.prenotazioni.tipologies',
        widget=atapi.SelectionWidget(
            label=_(u"booking tipology"),
        ),
        searchable=True,
        default='',
    ),
    atapi.DateTimeField(
        'data_prenotazione',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Booking date'),
            visible={'edit': 'hidden', 'view': 'visible'},
        ),
        required=True,
    ),
    atapi.StringField(
        'azienda',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Company"),
            description=_(u"Inserisci la denominazione dell'azienda "
                          u"del richiedente"),
        ),
        default='',
        searchable=True,
    ),
    atapi.StringField(
        'gate',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Gate"),
            description=_(u"Sportello a cui presentarsi"),
        ),
        searchable=True,
        default='',
    ),
    atapi.DateTimeField(
        'data_scadenza',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Expiration date booking'),
            visible={'edit': 'hidden', 'view': 'visible'},
        ),
        required=True,
    ),
    atapi.TextField(
        'staff_notes',
        default='',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(migrate=True),
        allowable_content_types=('text/plain',),
        widget=atapi.TextAreaWidget(
            label=_(
                'staff_notes_label',
                u"Staff notes"
            )
        ),
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

    def getDuration(self):
        ''' Return current duration
        '''
        start = self.getData_prenotazione()
        end = self.getData_scadenza()
        if start and end:
            return end - start
        else:
            return 1

    def Subject(self):
        """ Reuse plone subject to do something useful
        """
        subject = set(self.getField('subject').get(self))
        subject.add('Gate: %s' % self.getGate())
        return sorted(subject)

atapi.registerType(Prenotazione, PROJECTNAME)
