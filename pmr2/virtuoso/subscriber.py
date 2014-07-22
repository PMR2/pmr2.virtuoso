import logging

import zope.component

from pmr2.app.workspace.interfaces import IWorkspace
from pmr2.app.workspace.interfaces import IWorkspaceModifiedEvent
from pmr2.virtuoso.interfaces import IWorkspaceRDFIndexer

logger = logging.getLogger(__name__)

@zope.component.adapter(IWorkspace, IWorkspaceModifiedEvent)
def reindex_workspace_rdf(workspace, event):
    try:
        zope.component.getAdapter(workspace, IWorkspaceRDFIndexer)()
    except Exception as e:
        logger.exception('reindex_workspace_rdf subscriber fault')
