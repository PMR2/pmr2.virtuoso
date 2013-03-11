from urllib import unquote_plus, quote, quote_plus, splitquery

def quote_url(url):
    target, q = splitquery(unquote_plus(url))
    if q is None:
        return quote(target, safe=':/')
    return quote(target, safe=':/') + '?' + quote_plus(q, '=+')
