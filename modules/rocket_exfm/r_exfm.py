#! /usr/bin/env python


__doc__ = """Python bindings for the ExtensionFM public API"""

import rocket
from rocket.proxies import gen_ns_pair_multi_delim
import logging
import traceback

"""Samples: http://api.extension.fm/v1/user/profile.get?owner=j2d2
http://api.extension.fm/v1/user/noted.get?owner=j2d2&start=0&count=3"""


VERSION = '0.1'
#API_URL = 'http://api.extension.fm/v1/user'
API_URL = 'http://api.extension.fm/v1.1'
API_URL_SECURE = None

## TODO, Find these docs..
def _get_api_docstring(namespace, function):
    return '"""No docs yet"""'



# IDL for the API

FUNCTIONS = {
    "user/profile.get" : {
        'get': [
            ('owner', str, []),
        ],
    },
    "user/noted.get" : {
        'get' : [
            ('owner', str, []),
            ('start', int, ['optional']),
            ('count', int, ['optional']),            
        ],
    },
}

 
class EXFM(rocket.Rocket):
    def __init__(self, *args, **kwargs):
        self.function_list = FUNCTIONS
        super(EXFM, self).__init__(FUNCTIONS,
                                   client='exfm', api_url=API_URL,
                                   gen_doc_str=_get_api_docstring,
                                   gen_namespace_pair=gen_ns_pair_multi_delim,
                                   *args, **kwargs)
        
    def check_error(self, response):
        """Checks if the given API response is an error, and then raises
        the appropriate exception.
        """
        if type(response) is dict and response.has_key('status_code'):
            if response['status_code'] != 200:
                raise rocket.RocketAPIException(response['status_code'],
                                                response['status_text'])

        
    def gen_query_url(self, url, function, format=None, method=None, get_args=None):
        """I am totally cheating here, like really cheating. rocket seems to freak
        with the exfm api profile.get throws back crypt 'Profle' is not defined
        exception (assuming b/c the periods?)
        
        Look for more examples of rocket, need a quick start 
        """
        function = self.namespace_map[function]
        return '%s/%s' % (url, function)    
