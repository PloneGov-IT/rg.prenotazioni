from Products.CMFPlone.utils import safe_unicode
from plone.indexer.decorator import indexer
from rg.prenotazioni.content.prenotazione import IPrenotazione


@indexer(IPrenotazione)
def SearchableText_prenotazione(obj):
    if obj.subject:
        subject = u' '.join(
            [safe_unicode(s) for s in obj.subject]
        )
    else:
        subject = u''

    return u' '.join((
        safe_unicode(obj.id),
        safe_unicode(obj.title) or u'',
        safe_unicode(obj.description) or u'',
        safe_unicode(obj.email or u''),
        safe_unicode(obj.telefono or u''),
        safe_unicode(obj.mobile or u''),
        safe_unicode(obj.tipologia_prenotazione or u''),
        safe_unicode(obj.azienda or u''),
        safe_unicode(obj.gate or u''),
        safe_unicode(obj.staff_notes or u''),
        subject
    ))


@indexer(IPrenotazione)
def Subject_prenotazione(obj):
    subject = list(obj.subject)
    subject.append('Gate: %s' % obj.getGate())
    return sorted(subject)

