# -*- coding: utf-8 -*-
from rg.prenotazioni.content.prenotazione import Prenotazione
from zope.interface.declarations import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class TipologiesVocabulary(object):
    implements(IVocabularyFactory)

    def get_tipologies(self, context):
        ''' Return the tipologies in the PrenotazioniFolder
        '''
        if isinstance(context, Prenotazione):
            context = context.getPrenotazioniFolder()
        return context.getTipologia()

    def tipology2term(self, idx, tipology):
        '''
        '''
        name = tipology.get('name', '').decode('utf8')
        duration = str(tipology.get('duration', ''))
        if not duration:
            title = name
        else:
            title = u"%s [%s min]" % (name, duration)
        return SimpleTerm(title, str(idx), title)

    def get_terms(self, context):
        ''' The vocabulary terms
        '''
        return [self.tipology2term(idx, tipology)
                for idx, tipology
                in enumerate(self.get_tipologies(context))]

    def __call__(self, context):
        '''
        Return all the tipologies defined in the PrenotazioniFolder
        '''
        return SimpleVocabulary(self.get_terms(context))

TipologiesVocabularyFactory = TipologiesVocabulary()
