#! /usr/bin/env python
#
# r_twitter

__doc__ = """Python bindings for the Twitter API
(r_twitter - courtesy of ExtensionFM)

For more information, see

Home Page: nuttin yet.
Developer: http://twitterapi.pbworks.com/
"""

import rocket
from rocket.auth import sign_sorted_values

########################################
# Settings #############################
########################################

VERSION = '0.1'

API_URL = 'http://search.twitter.com'
API_URL_SECURE = None

API_DOCSTRING = '"""See http://twitterapi.pbworks.com/Twitter-Search-API-Method:-%s"""'

def _get_api_docstring(namespace, function):
    """Print a link to the documentation based on namespace (like search)
    """
    return API_DOCSTRING % (namespace)


########################################
# API implementation details ###########
########################################

# IDL for the API
FUNCTIONS = {
    'search': {
        'get': [
            ('q', str, []),
        ],
    },
}


########################################
# API class implementation #############
########################################

class Twitter(rocket.Rocket):
    """Provides access to the Twitter API.
    """
    def __init__(self, *args, **kwargs):
        super(Twitter, self).__init__(FUNCTIONS, client='twitter',
                                      gen_doc_str=_get_api_docstring,
                                      api_url=API_URL,
                                      *args, **kwargs)

    def check_error(self, response):
        """Checks if the given API response is an error, and then raises
        the appropriate exception.
        """
        if type(response) is dict and response.has_key('error'):
            raise rocket.RocketAPIError(response['error'], response['errormsg'])


    def build_query_args(self, *args, **kwargs):
        """Overrides Rocket's build_query_arg to set signing_alg to
        sign_sorted_values
        """
        return super(Twitter, self).build_query_args(signing_alg=sign_sorted_values,
                                                     *args, **kwargs)
    
        
    def gen_query_url(self, url, function, format=None, get_args=None, **kwargs):
        """Twitter urls look like 'url/function.format'.

        Example: http://search.twitter.com/search.json?q=@j2labs
        """
        return '%s/%s.%s' % (url, function, format)


if __name__ == '__main__':
    search_query = '@j2labs'

    twitter = Twitter()

    response_dict = twitter.search.get(search_query)
    print 'TWEETS:'
    for r in response_dict['results']:
        print '  %s: %s' % (r['from_user'], r['text'])
