## Script (Python) "validate_integrity"
##title=Validate Integrity
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage

request = context.REQUEST
errors = {}
errors = context.validate(REQUEST=request, errors=errors, data=1, metadata=0)

if errors:
    message = _(u'Please correct the indicated errors.')
    addStatusMessage(request, message, type='error')
    return state.set(status='failure', errors=errors)
else:
    # Custom validation for prenotazioni
    context_type = getattr(context, 'portal_type', None)
    if context_type and context_type == 'Prenotazione':
        url = context.aq_parent.absolute_url()
        data = context.getData_prenotazione().strftime('%d/%m/%Y')
        try:
            context.portal_workflow.doActionFor(context, 'submit')
        except:
            pass
        context.plone_utils.addPortalMessage(_(u'Richiesta prenotazione effettuata correttamente'))
        state.setNextAction('redirect_to:string:' + url +'?data='+data)
        return state.set(status='created')
    # Procede with statndard messages
    message = _(u'Changes saved.')
    addStatusMessage(request, message)
    return state.set(status='success')
