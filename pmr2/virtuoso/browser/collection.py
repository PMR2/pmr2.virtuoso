import json

from pmr2.virtuoso.browser import workspace

from pmr2.json.collection.mixin import JsonCollectionFormMixin


class WorkspaceRDFInfoEditForm(JsonCollectionFormMixin,
        workspace.WorkspaceRDFInfoEditForm):
    pass
