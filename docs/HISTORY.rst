Changelog
=========

0.8 - ????-??-??
----------------

* Make the SPARQL query box taller
* Export of the RDF graph captured by Virtuoso for the relevant exposure
  annotation from Virtuoso via RDFXML and JSON-LD.
* Make available the exposure rdf export as a note, though made more
  prominently available as a tool for the exposure, to better address
  the use case where the metadata is declared as an additional exposure
  file (though likely hidden from navigation).

0.7 - 2020-10-19
----------------

* Apply a workaround to ensure parent object is accessible from the
  indexer, to avoid spurious indexing errors.
* Provide support for JSON-LD.
* Bump version of python-virutoso to ensure more correct unicode support
* Implement chunking of sparql inserts to limit the size of the graph
  being passed in at a time.

0.6 - 2017-06-28
----------------

* Objects also need the URI normalization that subjects got, as it is
  possible for files to have local references.  Apply this to predicates
  also as the operation only works on relative URIs.

0.5 - 2016-03-08
----------------

* Free form SPARQL query, done within a restricted manner to ensure the
  terms return all correlate to an object within the CMS for permission
  checking.

0.4 - 2015-05-29
----------------

* Fix a major issue with xml conversion to n3 not being properly encoded.
* Fix for issues where newer versions of sqlalchemy raises an exception
  if a query returns nothing.

0.3 - 2015-03-19
----------------

* Include support of webservices through ``pmr2.json``.
* Other minor fixes.

0.2 - 2014-08-14
----------------

* Virtuoso Client through the JSON interface.
* Subscriber to push events to enable automatic exporting of previously
  specified metadata files of a given workspace into the RDF store (i.e.
  reindexing).
* Improved how the triples are indexed so that the objects that provided
  them can be better tracked.
* ExposureFile type for metadata

  - This can force the anchored file to be hidden from navigational
    elements in Plone.

0.1 - 2014-04-03
----------------

* Initial release of interaction with the Virtuoso RDF store from PMR.

