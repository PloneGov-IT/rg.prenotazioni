# -*- coding: utf-8 -*-
"""Definition of the PrenotazioniFolder content type
"""
from DateTime import DateTime
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content import folder
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.DataGridField import FixedRow
from Products.DataGridField.FixedColumn import FixedColumn
from Products.DataGridField.SelectColumn import SelectColumn
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.interfaces import IPrenotazioniFolder
from zope.interface import implements


PrenotazioniFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.TextField(
        'descriptionAgenda',
         required=False,
         searchable=True,
         storage=atapi.AnnotationStorage(migrate=True),
         validators=('isTidyHtmlWithCleanup',),
         default_output_type='text/x-html-safe',
         widget=atapi.RichWidget(
                   description=("Inserire il testo di presentazione "
                                "dell'agenda corrente"),
                   label=_(u'Descrizione Agenda', default=u''),
                   rows=10,
                   allow_file_upload=zconf.ATDocument.allow_document_upload),
   ),

    atapi.DateTimeField(
        'daData',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u'Data inizio validità'),
            description=_(u""),
            show_hm=False,
        ),
        required=True,
        default=DateTime(),
    ),

    atapi.DateTimeField(
        'aData',
        storage=atapi.AnnotationStorage(),
        widget=atapi.CalendarWidget(
            label=_(u'Data fine validità'),
            description=_(u""),
            show_hm=False,
        ),
        required=True,
    ),

    atapi.IntegerField(
        'durata',
        storage=atapi.AnnotationStorage(),
        vocabulary="vocDurataIncontro",
        widget=atapi.SelectionWidget(
            label=_(u"Durata incontro"),
            description=_(u"Specificare la durata in minuti"),
        ),
        required=True,
        validators=('isInt'),
    ),

    DataGridField(
        'settimana_tipo',
        storage=atapi.AnnotationStorage(),
        columns=('giorno', 'inizio_m', 'num_m', 'inizio_p', 'num_p'),
        fixed_rows="vocGiorniSettimana",
        allow_delete=False,
        allow_insert=False,
        allow_reorder=False,
        widget=DataGridWidget(
            label=_(u"Settimana Tipo"),
            description=_(u"Indicare la composizione della settimana tipo"),
            columns={
                "giorno": FixedColumn("Giorno"),
                "inizio_m":  SelectColumn("Ora inizio",
                                          vocabulary="vocOreInizio",
                                          default=""),
                "num_m": SelectColumn("Numero appuntamenti",
                                      vocabulary="vocNumeroAppuntamenti",
                                      default=""),
                "inizio_p": SelectColumn("Ora inizio",
                                         vocabulary="vocOreInizio",
                                         default=""),
                "num_p": SelectColumn("Numero appuntamenti",
                                      vocabulary="vocNumeroAppuntamenti",
                                      default=""),
            }
        ),
        required=True,
    ),

    atapi.LinesField(
        'festivi',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"Giorni festivi"),
            description=_(u"Indicare i giorni festivi (una per riga) "
                          u"nel formato gg/mm/aaaa"),
        ),
        required=False,
    ),

    atapi.LinesField(
        'tipologia',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u'Tipologie delle richieste'),
            description=_(u'Inserisci le tipologie (una per riga) '
                          u'delle richieste di prenotazione'),
        ),
        required=True,
    ),

    atapi.StringField(
        'email_responsabile',
        required=True,
        widget=atapi.StringWidget(
            label=_(u'Email del responsabile'),
            description=_(u"Inserisci l'indirizzo email del responsabile "
                           "delle prenotazioni"),
            validator=('isEmail',),
            size=80),
    ),

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

PrenotazioniFolderSchema['title'].storage = atapi.AnnotationStorage()
PrenotazioniFolderSchema['description'].storage = atapi.AnnotationStorage()

PrenotazioniFolderSchema['location'].widget.modes = []
PrenotazioniFolderSchema['location'].schemata = 'default'
PrenotazioniFolderSchema['subject'].widget.modes = []
PrenotazioniFolderSchema['subject'].schemata = 'default'
PrenotazioniFolderSchema['relatedItems'].widget.modes = []
PrenotazioniFolderSchema['relatedItems'].schemata = 'default'
PrenotazioniFolderSchema['language'].widget.modes = []
PrenotazioniFolderSchema['language'].schemata = 'default'
PrenotazioniFolderSchema['effectiveDate'].widget.modes = []
PrenotazioniFolderSchema['effectiveDate'].schemata = 'default'
PrenotazioniFolderSchema['expirationDate'].widget.modes = []
PrenotazioniFolderSchema['expirationDate'].schemata = 'default'
PrenotazioniFolderSchema['creators'].widget.modes = []
PrenotazioniFolderSchema['creators'].schemata = 'default'
PrenotazioniFolderSchema['contributors'].widget.modes = []
PrenotazioniFolderSchema['contributors'].schemata = 'default'
PrenotazioniFolderSchema['rights'].widget.modes = []
PrenotazioniFolderSchema['rights'].schemata = 'default'
PrenotazioniFolderSchema['allowDiscussion'].widget.modes = []
PrenotazioniFolderSchema['allowDiscussion'].schemata = 'default'
PrenotazioniFolderSchema['excludeFromNav'].widget.modes = []
PrenotazioniFolderSchema['excludeFromNav'].schemata = 'default'
PrenotazioniFolderSchema['nextPreviousEnabled'].widget.modes = []
PrenotazioniFolderSchema['nextPreviousEnabled'].schemata = 'default'


class PrenotazioniFolder(folder.ATFolder):
    """Description of the Example Type"""
    implements(IPrenotazioniFolder)

    meta_type = "PrenotazioniFolder"
    schema = PrenotazioniFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    daData = atapi.ATFieldProperty('daData')
    aData = atapi.ATFieldProperty('aData')
    durata = atapi.ATFieldProperty('durata')
    settimana_tipo = atapi.ATFieldProperty('settimana_tipo')
    festivi = atapi.ATFieldProperty('festivi')
    tipologia = atapi.ATFieldProperty('tipologia')

    def vocDurataIncontro(self):
        """
        """
        return [x for x in range(10, 95, 5)]

    def vocGiorniSettimana(self):
        """
        """
        week = ['lunedi', 'martedi', 'mercoledi',
                'giovedi', 'venerdi', 'sabato', 'domenica']
        rows = []
        for giorno in week:
            rows.append(FixedRow(keyColumn="giorno",
                                 initialData={"giorno": giorno,
                                              'inizio_m': '',
                                              'num_m': '',
                                              'inizio_p': '',
                                              'num_p': ''
                                              }))

        return rows

    def vocOreInizio(self):
        """
        """
        hours = ['07', '08', '09', '10', '11', '12', '13',
                 '14', '15', '16', '17', '18', '19', '20']
        minutes = ['00', '15', '30', '45']

        res = DisplayList()
        res.add('0', '--:--')
        for hour in hours:
            for minute in minutes:
                time = hour + ':' + minute
                index_time = hour + minute
                res.add(index_time, time)

        return res

    def vocNumeroAppuntamenti(self):
        """
        """
        res = DisplayList()
        for x in range(0, 21):
            res.add(str(x), str(x))

        return res

atapi.registerType(PrenotazioniFolder, PROJECTNAME)
