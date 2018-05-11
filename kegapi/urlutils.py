from urllib.parse import urlencode


def build_uri(uri, d={'db': 'pubmed', 'retmode': 'json'}, is_base=False):
    """
    Build an uri starting from a base and with an initial data dict to be encoded
    :param uri: the string to pass
    :param d: the dictionary to encode
    :param is_base: if it's base, adds a ?, else &
    :return:
    """
    if is_base:
        return uri + '?' + urlencode(d)
    else:
        return uri + '&' + urlencode(d)
