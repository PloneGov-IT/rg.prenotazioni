from plone.dexterity.browser.add import DefaultAddForm as BaseAddForm
from plone.dexterity.browser.add import DefaultAddView as BaseAddView
from plone.dexterity.browser.edit import DefaultEditForm as BaseEdit
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from zope.interface import classImplements
from z3c.form import button
from plone.dexterity.i18n import MessageFactory as _dmf
from rg.prenotazioni import _
from zope.interface import Invalid
from z3c.form.interfaces import WidgetActionExecutionError
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.events import AddCancelledEvent
from plone.dexterity.events import AddCancelledEvent
from plone.dexterity.events import EditCancelledEvent
from plone.dexterity.events import EditFinishedEvent
from zope.event import notify
from z3c.form.interfaces import DISPLAY_MODE
from collective.z3cform.datagridfield import BlockDataGridFieldFactory
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile as Z3VPTF  # noqa
import re


class DefaultEditForm(BaseEdit):
    """
    """
    def updateWidgets(self):
        super(DefaultEditForm, self).updateWidgets()
        # XXX day name should be only readable
        self.widgets['settimana_tipo'].columns[0]['mode'] = DISPLAY_MODE
        self.widgets['settimana_tipo'].allow_insert = False
        self.widgets['settimana_tipo'].allow_delete = False
        self.widgets['settimana_tipo'].allow_append = False
        self.widgets['settimana_tipo'].allow_reorder = False

    def datagridUpdateWidgets(self, subform, widgets, widget):
        if 'giorno' in widgets.keys():
            widgets['giorno'].template = Z3VPTF('templates/custom_dgf_input.pt')

    @button.buttonAndHandler(_dmf(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return


        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _dmf(u"Changes saved"), "info")
        self.request.response.redirect(self.nextURL())
        notify(EditFinishedEvent(self.context))

    @button.buttonAndHandler(_dmf(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _dmf(u"Edit cancelled"), "info")
        self.request.response.redirect(self.nextURL())
        notify(EditCancelledEvent(self.context))


DefaultEditView = layout.wrap_form(DefaultEditForm)
classImplements(DefaultEditView, IDexterityEditForm)


class DefaultAddForm(BaseAddForm):
    """
    """
    def updateWidgets(self):
        super(DefaultAddForm, self).updateWidgets()
        # XXX day name should be only readable
        self.widgets['settimana_tipo'].columns[0]['mode'] = DISPLAY_MODE
        self.widgets['settimana_tipo'].allow_insert = False
        self.widgets['settimana_tipo'].allow_delete = False
        self.widgets['settimana_tipo'].allow_append = False
        self.widgets['settimana_tipo'].allow_reorder = False

    def datagridUpdateWidgets(self, subform, widgets, widget):
        if 'giorno' in widgets.keys():
            widgets['giorno'].template = Z3VPTF('templates/custom_dgf_input.pt')


    @button.buttonAndHandler(_dmf('Save'), name='save')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return


        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(
                self.success_message, "info"
            )

    @button.buttonAndHandler(_dmf(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _dmf(u"Add New Item operation cancelled"), "info"
        )
        self.request.response.redirect(self.nextURL())
        notify(AddCancelledEvent(self.context))


    def nextURL(self):
        return self.context.absolute_url()


class DefaultAddView(BaseAddView):

    form = DefaultAddForm

