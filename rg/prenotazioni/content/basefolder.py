# -*- coding: utf-8 -*-
try:
    from plone.app.folder.folder import ATFolder as BaseFolder
    from plone.app.folder.folder import ATFolderSchema as BaseFolderSchema
except ImportError:
    from Products.ATContentTypes.content.folder import ATBTreeFolder as BaseFolder
    from Products.ATContentTypes.content.folder import ATBTreeFolderSchema as BaseFolderSchema

BaseFolderSchema


class BaseNoNavFolder(BaseFolder):

    ''' Like base folder, but it is excluded from navigation
    '''
    exclude_from_nav = True
