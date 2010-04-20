# -*- coding: utf-8 -*-
"""Definition of the Prenotazione content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from Products.Archetypes.utils import DisplayList
from Acquisition import aq_chain

from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.interfaces import IPrenotazione, IPrenotazioniFolder
from rg.prenotazioni.config import PROJECTNAME

PrenotazioneSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        'tipologia_prenotazione',
        storage = atapi.AnnotationStorage(),
        vocabulary = 'getElencoTipologie',
        widget = atapi.SelectionWidget(
            label = _(u"Tipologia della prenotazione"),
            description = _(u""),
        ),
        required=False,
    ),

    atapi.DateTimeField(
        'data_prenotazione',
        storage = atapi.AnnotationStorage(),
        widget = atapi.CalendarWidget(
            label = _(u'Data prenotazione'),
            description = _(u""),
            visible = {'edit':'invisible','view':'visible'},
        ),
        required = False,
    ),

    atapi.StringField(
        'azienda',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = _(u"Azienda"),
            description = _(u"Inserisci la denominazione dell'azienda del richiedente"),
        ),
        required = False,
    ),

    atapi.StringField(
        'telefono',
        storage = atapi.AnnotationStorage(),
        widget = atapi.StringWidget(
            label = _(u"Telefono"),
            description = _(u"Inserisci un recapito telefonico"),
        ),
        required = False,
    ),

    atapi.StringField(
        'email',
        storage = atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label="email",
            validator=('isEmail',),
        ),
        required = True,
    ),
))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PrenotazioneSchema['title'].storage = atapi.AnnotationStorage()
PrenotazioneSchema['title'].widget.label = _(u"Nome e Cognome")
PrenotazioneSchema['title'].widget.description = _(u"")
PrenotazioneSchema['description'].storage = atapi.AnnotationStorage()
PrenotazioneSchema['description'].isMetadata = False
PrenotazioneSchema['description'].widget.label = _(u"Oggetto")
PrenotazioneSchema['description'].widget.description = _(u"")

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

    meta_type = "Prenotazione"
    schema = PrenotazioneSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    def getPrenotazioniFolder(self):
        """Ritornal'oggetto prenotazioni folder"""

        for parent in aq_chain(self):
            if IPrenotazioniFolder.providedBy(parent):
                return parent
        raise Exception(
            "Could not find Prenotazioni Folder in acquisition chain of %r" %
            self)

    def getElencoTipologie(self):
        """ restituisce l'elenco delle tipologie sulla folder padre
        """
        elenco_tipologie = DisplayList()
        items = self.getPrenotazioniFolder().getTipologia()
        for item in items:
            elenco_tipologie.add(item, item)
        return elenco_tipologie

    def getEmailResponsabile(self):
        """
        """
        parent = self.aq_inner.aq_parent
        email = parent.getEmail_responsabile()

        return email

atapi.registerType(Prenotazione, PROJECTNAME)
