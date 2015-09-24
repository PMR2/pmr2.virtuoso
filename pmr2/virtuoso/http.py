# Not sure exactly where will this helper module be placed, but
# I don't want it duplicated here quite just yet.
try:
    from pmr2.json.http import parse_accept
except ImportError:
    from ._http import parse_accept
