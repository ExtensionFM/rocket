#! /usr/bin/env python
#
# sailthru - implementing with a quickness


__doc__ = """Python bindings for the Sailthru API
(rocket_sailthru - courtesy of ExtensionFM)

For more information, see

Home Page: http://github.com/extensionfm/rocket_sailthru
Developer: http://docs.sailthru.com/api
"""

import rocket
from rocket.auth import sign_sorted_values

########################################
# Settings #############################
########################################

VERSION = '0.1'

API_URL = 'http://api.sailthru.com'
API_URL_SECURE = None

API_DOCSTRING = '"""Sailthru call. See http://docs.sailthru.com/api/%s#%s-mode"""'

def _get_api_docstring(namespace, function):
    """The sailthru api docs are stored such that the namespace has
    a url and each function is listed sequentially on the namespace doc.
    """
    return API_DOCSTRING % (namespace, function)


########################################
# API implementation details ###########
########################################

# IDL for the API
FUNCTIONS = {
    'email': {
        'get': [
            ('email', str, []),
        ],
        'post': [
            ('email', str, []),
            ('verified', int, ['optional']),
            ('optout', str, ['optional']),
            ('vars', rocket.json, ['optional']),
            ('lists', rocket.json, ['optional']),
            ('templates', rocket.json, ['optional']),
            ('send', str, ['optional']),
            ('send_vars', rocket.json, ['optional']),
        ],
    },
    'send': {
        'get': [
            ('send_id', str, []),
        ],
        'post': [
            ('template', str, []),
            ('email', str, []),
            ('vars', rocket.json, ['optional']),
            ('schedule_time', str, ['optional']),
            ('options', rocket.json, ['optional']),
        ],
        'delete': [
            ('send_id', str, []),
        ],
    },
    'blast': {
        'get': [
            ('blast_id', str, []),
        ],
        'post': [
            ('name', str, []),
            ('list', str, []),
            ('schedule_time', str, ['optional']),
            ('from_name', str, ['optional']),
            ('from_email', str, ['optional']),
            ('subject', str, ['optional']),
            ('content_html', str, ['optional']),
            ('content_text', str, ['optional']),
            ('blast_id', int, ['optional']),
            ('copy_blast', int, ['optional']),
            ('copy_template', str, ['optional']),
            ('replyto', str, ['optional']),
            ('report_email', str, ['optional']),
            ('is_link_tracking', int, ['optional']),
            ('is_google_analytics', int, ['optional']),
            ('is_public', int, ['optional']),
            ('suppress_list', str, ['optional']),
            ('test_vars', rocket.json, ['optional']),
            ('email_hour_range', int, ['optional']),
            ('abtest', int, ['optional']),
            ('test_percent', int, ['optional']),
            ('data_feed_url', str, ['optional']),
        ],
    },
    'template': {
        'get': [
            ('template', str, []),
            ('sample', str, ['optional']),
            ('from_name', str, ['optional']),
            ('from_email', str, ['optional']),
            ('subject', str, ['optional']),
            ('content_html', str, ['optional']),
            ('content_text', str, ['optional']),
            ('is_link_tracking', int, ['optional']),
            ('is_google_analytics', int, ['optional']),
        ],
        'post': [
            ('template', str, []),
            ('sample', str, ['optional']),
        ],
    },
    'list': {
        'get': [
            ('list', str, []),
        ],
        'post': [
            ('list', str, []),
            ('emails', list, []),
        ],
        'delete': [
            ('list', str, []),
        ],
    },
    'contacts': {
        'post': [
            ('email', str, []),
            ('password', str, []),
            ('names', int, ['optional']),
        ],
    },
    'content': {
        'post': [
            ('title', str, []),
            ('url', str, []),
            ('date', str, ['optional']),
            ('tags', list, ['optional']),
            ('date', rocket.json, ['optional']),
        ],
    },
    'alert': {
        'get': [
            ('email', str, []),
        ],
        'post': [
            ('email', str, []),
            ('type', str, []),
            ('when', str, []),
            ('match', rocket.json, ['optional']),
            ('min', rocket.json, ['optional']),
            ('max', rocket.json, ['optional']),
            ('tags', rocket.json, ['optional']),
        ],
        'delete': [
            ('email', str, []),
            ('alert_id', str, []),
        ],
    },
    'stats': {
        'get': [
            ('stat', str, []),
            ('list', str, ['optional']),
            ('date', str, ['optional']),
        ],
    },
    'purchase': {
        'post': [
            ('email', str, []),
            ('items', rocket.json, []),
            ('incomplete', int, ['optional']),
            ('message_id', int, ['optional']),
        ],
    },
}


########################################
# API class implementation #############
########################################

class Sailthru(rocket.Rocket):
    """Provides access to the Sailthru API.

    Initialize with api_key and api_secret_key, both available from
    sailthru
    """
    def __init__(self, *args, **kwargs):
        super(Sailthru, self).__init__(FUNCTIONS, api_url=API_URL,
                                       *args, **kwargs)

    def check_error(self, response):
        """Checks if the given API response is an error, and then raises
        the appropriate exception.
        """
        if type(response) is dict and response.has_key('error'):
            raise rocket.RocketAPIException(response['error'], response['errormsg'])


    def build_query_args(self, *args, **kwargs):
        """Overrides Rocket's build_query_arg to set signing_alg to
        sign_sorted_values
        """
        return super(Sailthru, self).build_query_args(signing_alg=sign_sorted_values,
                                                      *args, **kwargs)
    
        
    def gen_query_url(self, url, function, format=None, method=None, get_args=None):
        """Sailthru urls look like 'url/function'.

        Example: http://api.sailthru.com/email
        """
        return '%s/%s' % (url, function)

