import urlparse


def add_url_parameter(url, key, value):
    # import debug
    parts = url.split("?")
    base_url = parts[0]
    query = ""
    if len(parts) > 1:
        query = parts[1]

    pairs = [pair.split("=") for pair in query.split("&")]
    querydict = {}
    for pair in pairs:
        pair.append(None)
        querydict[pair[0]] = pair[1]
    querydict[key] = value
    
    query = ""
    for k, v in querydict.items():
        if v:
            query += "&%s=%s" % (k, v)
        else:
            query += "&%s" % k
    return "%s?%s" % (url.split("?")[0], query[1:])
