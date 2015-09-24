from pmr2.layer.utility import ConditionalLayerApplierBase
from .interfaces import ISparqlJsonLayer
from .http import parse_accept


class SparqlJsonLayerApplier(ConditionalLayerApplierBase):

    layer = ISparqlJsonLayer

    def condition(self, request):
        acceptable = (
            'application/sparql-results+json',
            'application/json',
        )

        accepts = parse_accept(request.get('HTTP_ACCEPT', ''))
        for a in accepts:
            if a[0] in acceptable:
                request.response.setHeader('Content-Type', a[0])
                return True

        return False
