from hashlib import md5
import json


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj


def listhash(obj):
    if isinstance(obj, list):
        return md5(json.dumps(obj).encode('utf-8')).hexdigest()
    else:
        raise TypeError
