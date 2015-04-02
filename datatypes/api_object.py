import os, sys; sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import jsonpickle
import re

##############################################################################
#
##############################################################################

jsonpickle.set_preferred_backend('json')

for encoder in ('json', 'simplejson', 'demjson'):
    jsonpickle.set_encoder_options(encoder, sort_keys=True, indent=4)

##############################################################################
#
##############################################################################

class ApiObject(object):
    _re_encode = re.compile('"py/object"\\s*:\\s*"datatypes\\.api_object\\.([^"]*)"', flags=re.I)
    _re_decode = re.compile('"object"\\s*:\\s*"([^"]*)"', flags=re.I)

    def __new__(cls, json=None):
        return cls.decode(json) if json else object.__new__(cls)

    def encode(self):
        json = jsonpickle.encode(self)
        return self._re_encode.sub('"object": "\\1"', json)

    @classmethod
    def decode(cls, json):
        json = cls._re_decode.sub('"py/object": "datatypes.api_object.\\1"', json)
        return jsonpickle.decode(json)

    def __str__(self):
        return self.encode()
