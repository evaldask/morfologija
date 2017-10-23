from fn.iters import head

first = head


class UnknownField(Exception): pass

def assign(obj, data, fields, ignore=None):
    keys = set()
    for k, v in fields:
        keys.add(k)
        setattr(obj, k.replace('-', '_'), data.get(k, v))
    keys.update(ignore or [])
    diff = set(data).difference(keys)
    if diff:
        raise UnknownField(
            'Unknown fields: %s in %r' % (', '.join(diff), data)
        )


def getnested(d, keys, default=None):
    for k in keys:
        if k in d:
            d = d[k]
        else:
            return default
    return d
