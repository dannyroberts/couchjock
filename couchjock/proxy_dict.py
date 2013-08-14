from jsonobject.base import SimpleDict


class ProxyDict(SimpleDict):
    def __init__(self, parent, *args, **kwargs):
        super(ProxyDict, self).__init__(*args, **kwargs)
        self.parent = parent

    def __setitem__(self, key, value):
        self.parent[key] = value
