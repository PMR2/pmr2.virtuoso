# CellML specific


def importExposureFilesRdf(context):
    sources = []

    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog(
        pmr2_review_state='published',
        portal_type='ExposureFile',
        Subject='CellML Model',
    )

    for b in brains:
        bo = b.getObject()
        es = zope.component.getAdapter(bo, IExposureSourceAdapter)
        e, w, p = es.source()
        try:
            if w is None:
                raise TypeError("%s cannot be adapted to workspace" % bo)
            source = '%s/%s/%s/%s/%s' % (
                portal_url, w.absolute_url(), 'pmr2_rdf', e.commit_id, p)
            sources.append(source)
        except:
            logger.error('fail to acquire workspace file', exc_info=1)
