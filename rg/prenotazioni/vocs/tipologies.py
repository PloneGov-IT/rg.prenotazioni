# -*- coding: utf-8 -*-
from zope.interface.declarations import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


class TipologiesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        '''
        Return all the tipologies defined in the PrenotazioniFolder
        '''
        tipologies = context.getTipologia()
        return SimpleVocabulary([SimpleTerm(tipology.decode('utf8'),
                                            str(i),
                                            tipology.decode('utf8'))
                                 for i, tipology
                                 in enumerate(tipologies)])

TipologiesVocabularyFactory = TipologiesVocabulary()
