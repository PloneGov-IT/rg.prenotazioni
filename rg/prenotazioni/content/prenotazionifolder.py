# -*- coding: utf-8 -*-
"""Definition of the PrenotazioniFolder content type
"""
from DateTime import DateTime
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes import atapi
from Products.Archetypes.utils import DisplayList
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.DataGridField import FixedRow
from Products.DataGridField.FixedColumn import Column, FixedColumn
from Products.DataGridField.SelectColumn import SelectColumn
from rg.prenotazioni import prenotazioniMessageFactory as _
from rg.prenotazioni.config import PROJECTNAME
from rg.prenotazioni.content.basefolder import BaseFolder, BaseFolderSchema
from rg.prenotazioni.interfaces import IPrenotazioniFolder
from zope.interface import implements


PrenotazioniFolderSchema = BaseFolderSchema.copy() + atapi.Schema((

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
            description=_("aData_help",
                          default=u"Leave empty, and this Booking Folder will never expire"),  # noqa
            show_hm=False,
        ),
        required=False,
    ),

    DataGridField(
        'settimana_tipo',
        storage=atapi.AnnotationStorage(),
        columns=('giorno', 'inizio_m', 'end_m', 'inizio_p', 'end_p'),
        fixed_rows="vocGiorniSettimana",
        allow_delete=False,
        allow_insert=False,
        allow_reorder=False,
        widget=DataGridWidget(
            label=_(u"Settimana Tipo"),
            description=_(u"Indicare la composizione della settimana tipo"),
            columns={
                "giorno": FixedColumn("Giorno"),
                "inizio_m": SelectColumn("Ora inizio mattina",
                                         vocabulary="vocOreInizio",
                                         default=""),
                "end_m": SelectColumn("Ora fine mattina",
                                      vocabulary="vocOreInizio",
                                      default=""),
                "inizio_p": SelectColumn("Ora inizio pomeriggio",
                                         vocabulary="vocOreInizio",
                                         default=""),
                "end_p": SelectColumn("Ora fine pomeriggio",
                                      vocabulary="vocOreInizio",
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
            description=_(
                'help_holidays',
                u"Indicare i giorni festivi (uno per riga) "
                u"nel formato GG/MM/AAAA. Al posto dell'anno puoi mettere un "
                u"asterisco per indicare un evento che ricorre annualmente."
            ),
        ),
        required=False,
    ),

    atapi.IntegerField(
        'futureDays',
        required=True,
        default=0,
        widget=atapi.IntegerWidget(
            label=_(u'Max days in the future'),
            description=_('futureDays',
                          default=u"Limit booking in the future to an amount "
                                  u"of days in the future starting from "
                                  u"the current day. \n"
                                  u"Keep 0 to give no limits."),
        ),
    ),

    DataGridField(
        'tipologia',
        storage=atapi.AnnotationStorage(),
        columns=('name', 'duration'),
        allow_delete=True,
        allow_insert=True,
        allow_reorder=False,
        widget=DataGridWidget(
            label=_(u"Tipologie di richiesta"),
            description=_('tipologia_help',
                          default=u"Put booking types there (one per line).\n"
                                  u"If you do not provide this field, "
                                  u"not type selection will be available"),
            columns={
                "name": Column(_(u"Typology name"),
                                   required=True,
                                   default=""),
                "duration": SelectColumn(_(u"Duration value"),
                                         vocabulary="vocDurataIncontro",
                                         required=True,
                                         default=""),
            }
        ),
        searchable=True,
        validators=('isColumnFilled', 'isDataGridFilled', ),
        required=True,
    ),

    atapi.LinesField(
        'gates',
        widget=atapi.LinesWidget(
            label=_('gates_label', "Gates"),
            description=_('gates_help',
                          default=u"Put gates here (one per line). "
                                  u"If you do not fill this field, "
                                  u"one gate is assumed"),
        ),
        required=False,
        default=[],
    ),

    atapi.LinesField(
        'unavailable_gates',
        widget=atapi.LinesWidget(
            label=_('unavailable_gates_label', "Unavailable gates"),
            description=_('unavailable_gates_help',
                          default=u'Add a gate here (one per line) if, '
                                  u'for some reason, '
                                  u'it is not be available.'
                                  u'The specified gate will not be taken in to '  # noqa
                                  u'account for slot allocation. '
                                  u'Each line should match a corresponding '
                                  u'line in the "Gates" field'
                          ),
        ),
        required=False,
        default=[],
    ),

    atapi.StringField(
        'email_responsabile',
        required=False,
        widget=atapi.StringWidget(
            label=_(u'Email del responsabile'),
            description=_(u"Inserisci l'indirizzo email del responsabile "
                          "delle prenotazioni"),
            size=50),
        validators=('isEmail',),
    ),

))

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


class PrenotazioniFolder(BaseFolder):

    """Description of the Example Type"""
    implements(IPrenotazioniFolder)

    meta_type = "PrenotazioniFolder"
    schema = PrenotazioniFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    daData = atapi.ATFieldProperty('daData')
    aData = atapi.ATFieldProperty('aData')
    settimana_tipo = atapi.ATFieldProperty('settimana_tipo')
    festivi = atapi.ATFieldProperty('festivi')
    tipologia = atapi.ATFieldProperty('tipologia')

    def vocDurataIncontro(self):
        """
        """
        return DisplayList([(str(x), str(x)) for x in range(10, 95, 5)])

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
                                              'end_m': '',
                                              'inizio_p': '',
                                              'end_p': ''
                                              }))

        return rows

    def vocOreInizio(self):
        """
        """
        hours = ['07', '08', '09', '10', '11', '12', '13',
                 '14', '15', '16', '17', '18', '19', '20']
        minutes = ['00', '15', '30', '45']

        res = DisplayList()
        res.add('', '--:--')
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

    def canSetDefaultPage(self):
        return False

atapi.registerType(PrenotazioniFolder, PROJECTNAME)
