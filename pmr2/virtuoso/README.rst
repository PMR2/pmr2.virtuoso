PMR2 Virtuoso Support
=====================

This module provides a way to connect the virtuoso RDF datastore into
PMR2 to enable better indexing and searching capabilities for the model
metadata.

Once this module is installed correctly, the connection string can be
acquired by acquiring the PMR2 global settings utility and then adapting
it to the local item::

    >>> import zope.component
    >>> from pmr2.app.settings.interfaces import IPMR2GlobalSettings
    >>> gs = zope.component.getUtility(IPMR2GlobalSettings)
    >>> vs = zope.component.getAdapter(gs, name=u'pmr2_virtuoso')
    >>> print vs.source
    virtuoso://dba:dba@VOS
