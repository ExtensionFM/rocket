#! /usr/bin/env python
#
# twilio - implementing with a quickness


__doc__ = """Python bindings for the Twilio API
(pytwilio - courtesy of ExtensionFM)

For more information, see

Home Page: http://github.com/extensionfm/pytwilio
Developer: http://docs.twilio.com/api
"""

import rocket
from rocket.auth import sign_sorted_values
from rocket.proxies import gen_ns_pair_slash_delim

gen_namespace_pair = gen_ns_pair_slash_delim

########################################
# Settings #############################
########################################

VERSION = '0.1'

# %s to make room for basic_auth_string
API_URL = None
API_URL_SECURE = 'https://api.twilio.com/2010-04-01'

API_DOCSTRING = '"""Twilio call. http://www.twilio.com/docs/api/2010-04-01/rest/"""'

def _get_api_docstring(namespace, function):
    """The twilio api docs are stored with algorithmically unfriendly
    paths. 
    """
    return API_DOCSTRING 


########################################
# API implementation details ###########
########################################

# IDL for the API
FUNCTIONS = {
    'SMS/Messages': {
        'post': [
            ('From', str, []),
            ('To', str, []),
            ('Body', str, []),
            ('statusCallback', str, ['optional']),
        ],
    },
}


########################################
# API class implementation #############
########################################

class Twilio(rocket.Rocket):
    """Provides access to the Twilio API.

    Initialize with api_key and api_secret_key, both available from
    twilio
    """
    def __init__(self, *args, **kwargs):
        super(Twilio, self).__init__(FUNCTIONS, client='twilio',
                                     api_url=API_URL_SECURE,
                                     gen_namespace_pair=gen_namespace_pair,
                                     *args, **kwargs)

    def check_error(self, response):
        """Checks if the given API response is an error, and then raises
        the appropriate exception.
        """
        pass
    

    def build_query_args(self, *args, **kwargs):
        """Overrides Rocket's build_query_arg to set signing_alg to
        sign_sorted_values
        """
        return super(Twilio, self).build_query_args(signing_alg=sign_sorted_values,
                                                      *args, **kwargs)
    
        
    def gen_query_url(self, url, function, format=None, method=None, get_args=None):
        """Twilio urls look like 'url/function'.

        Example: http://api.twilio.com/email
        """
        function = self.namespace_map[function]
        query_url = '%s/Accounts/%s/%s' % (url, self.api_key, function)
        if format:
            query_url = '%s.%s' % (query_url, format)
        return query_url


if __name__ == '__main__':
    api_key = ''
    api_secret_key = ''
    basic_auth_realm='Twilio API'
    basic_auth_pair = (api_key, api_secret_key)

    twilio = Twilio(api_key, api_secret_key,
                    gen_namespace_pair=gen_ns_pair_slash_delim,
                    basic_auth_pair=basic_auth_pair,
                    basic_auth_realm=basic_auth_realm)    

    to_number = '123-123-1234'
    from_number = '123-123-1234'
    body = 'a little texty text'

    response = twilio.SMSMessages.post(To=to_number,
                                       From=from_number,
                                       Body=body)
    print response
