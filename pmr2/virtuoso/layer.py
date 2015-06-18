from pmr2.layer.utility import ConditionalLayerApplierBase
from .interfaces import ISparqlJsonLayer


class SparqlJsonLayerApplier(ConditionalLayerApplierBase):

    def condition(self, request):
        if request.get('HTTP_ACCEPT') == 'application/sparql-results+json':
            return ISparqlJsonLayer
