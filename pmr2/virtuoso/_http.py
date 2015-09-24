from collections import namedtuple

MediaType = namedtuple('MediaType', ['type', 'q', 'params'])

def _sorter(mediatype):
    if mediatype.type == '*/*':
        v = 0
    elif mediatype.type.endswith('/*'):
        v = 1
    else:
        v = 2 + len(mediatype.params)
    return mediatype.q, v

def parse_accept(accept_header):
    """
    Parse a given accept header and return the list in the order of
    precedence.
    """

    results = []
    items = accept_header.split(',')
    for i in items:
        mediadef = i.strip().split(';')
        media_type = mediadef.pop(0)
        params = {k: v for k, v in (m.strip().split('=', 1) for m in mediadef)}
        q = params.pop('q', '1')
        results.append(MediaType(media_type, q, params))
    return sorted(results, key=_sorter, reverse=True)
