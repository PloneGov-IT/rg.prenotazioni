# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import WorkflowException


def booking_created(context, event):
    try:
        factory_tool = getToolByName(context, 'portal_factory')
        if not factory_tool.isTemporary(context) and not context._at_creation_flag:
            wtool = getToolByName(context, 'portal_workflow')
            wtool.doActionFor(context, 'submit')
    except WorkflowException:
        pass
