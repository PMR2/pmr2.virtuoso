from pmr2.layer.utility import ConditionalLayerApplierBase
from .interfaces import ISparqlJsonLayer


class SparqlJsonLayerApplier(ConditionalLayerApplierBase):

    layer = ISparqlJsonLayer

    def condition(self, request):
        return request.get('HTTP_ACCEPT') == 'application/sparql-results+json'
