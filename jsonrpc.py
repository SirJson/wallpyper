import sys
import json
import threading
from types import ModuleType

_uid = threading.local()


def nextid():
    if getattr(_uid, "uid", None) is None:
        _uid.tid = str(threading.current_thread().ident)
        _uid.uid = 0
    _uid.uid += 1
    return _uid.tid + str(_uid.uid)


class JsonRPCModule(ModuleType):
    def __repr__(self):
        return self.__name__

    def __getattr__(self, name):
        if 'remote' not in self.__dict__:
            raise RuntimeError('No remote endpoint specified')

        def wrapper(**kwargs):
            payload = {"jsonrpc": "2.0", "method": name}
            if len(kwargs) > 0:
                payload["params"] = kwargs
            payload['id'] = nextid()
            print(json.dumps(payload))
        return wrapper

    def __setattr__(self, name, value):
        if name is 'remote':
            self.__dict__[name] = value
        else:
            raise AttributeError()


sys.modules[__name__].__class__ = JsonRPCModule
