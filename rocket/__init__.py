#! /usr/bin/env python
#
# rocket - implementing with a quickness
#
# This module's design is influenced by the work of 
# Samuel Cormier-Iijima and team on the pyfacebook module.
# http://github.com/sciyoshi/pyfacebook/
#
# Props.

__doc__ = """rocket - implementing api's with a quickness

For more information, see: http://github.com/extensionfm/rocket

Rocket has one external dependency: simplejson

To install simplejson:

    pip install simpljson

Or http://undefined.org/python/#simplejson
"""

import sys
import time
import struct
import urllib
import urllib2
import httplib
import binascii
import urlparse
import mimetypes

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    
RESPONSE_JSON = 'json'
DEFAULT_RESPONSE_FORMAT = RESPONSE_JSON
DEFAULT_REQUEST_METHOD = 'GET'


### Would like a hand making this appengine safe
try:
    from simplejson import dumps as json_encode
    from simplejson import loads as json_decode
except ImportError:
    quit('Rocket requires simplejson')


# create json object for referencing complex structures in function_list
class json(object): pass


########################################
# URL handling #########################
########################################

def urlread(url, data=None, headers={}, method=DEFAULT_REQUEST_METHOD):
    """Takes a url[, data, headers, request method].

    It establishes an httplib.HTTPConnection and allows
    specific HTTP connection types, like POST, PUT, DELETE
    for API interaction.

    POST sends 'application/x-www-form-urlencoded' for it's
    Content-type

    Returns a tuple of (status code, reason, any data read)
    """
    data = urllib.urlencode(data) 

    # encoded_args = unicode_urlencode(encoded_args)

    parsed_url = urlparse.urlparse(url)
    url_path = parsed_url.path
    
    if method == 'GET':
        url_path = '%s?%s' % (url_path, data)
        data = None
    if method == 'POST':
        headers["Content-type"] = "application/x-www-form-urlencoded"
        headers["Accept"] = "text/plain"
        
    c = httplib.HTTPConnection(parsed_url.hostname)
    c.request(method, url_path, body=data, headers=headers)
    r = c.getresponse()

    return (r.status, r.reason, r.read())


def unicode_urlencode(self, params):
    """A unicode aware version of urllib.urlencode."""
    if isinstance(params, dict):
        params = params.items()
    args = [(k, isinstance(v, unicode) and v.encode('utf-8') or v)
            for k, v in params]
    return urllib.urlencode(args)



########################################
# Proxy functions ######################
########################################

class Proxy(object):
    """Represents a namespace of API calls."""

    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __call__(self, method=None, args=None, add_session_args=True):
        # for Django templates, if this object is called without any arguments
        # return the object itself
        if method is None:
            return self

        return self._client('%s.%s' % (self._name, method), args)


def generate_proxies(function_list, doc_fun):
    """Helper function for compiling function_list into runnable code.
    Run immediately after definition.
    """
    for namespace in function_list:
        methods = {}

        for method in function_list[namespace]:
            params = ['self']
            body = ['args = {}']

            method_params = function_list[namespace][method]
            for param_name, param_type, param_options in method_params:
                param = param_name

                for option in param_options:
                    if isinstance(option, tuple) and option[0] == 'default':
                        if param_type == list:
                            param = '%s=None' % param_name
                            body.append('if %s is None: %s = %s'
                                        % (param_name,
                                           param_name,
                                           repr(option[1])))
                        else:
                            param = '%s=%s' % (param_name, repr(option[1]))

                # We only jsonify the argument if it's a list or a dict. 
                if param_type == json:
                    body.append('if isinstance(%s, list) or isinstance(%s, dict): %s = json_encode(%s)'
                                % ((param_name,) * 4))

                # Optional variables default to None
                # Optional case must then be handled.
                if 'optional' in param_options:
                    param = '%s=None' % param_name
                    body.append('if %s is not None: args[\'%s\'] = %s'
                                % (param_name,
                                   param_name,
                                   param_name))
                else:
                    body.append('args[\'%s\'] = %s' % (param_name,
                                                       param_name))

                params.append(param)

            # simple docstring to refer them to web docs for their API
            body.insert(0, doc_fun(namespace, method))
            body.insert(0, 'def %s(%s):' % (method, ', '.join(params)))
            body.append('return self(\'%s\', args)' % method)
            exec('\n    '.join(body))
            methods[method] = eval(method)

        proxy = type('%sProxy' % namespace.title(), (Proxy, ), methods)
        globals()[proxy.__name__] = proxy


class RocketError(Exception):
    """Exception class for errors received from Rocket."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return '%s' % (self.msg)
    

class RocketAPIError(RocketError):
    """Exception class for errors received from the API."""

    def __init__(self, code, msg):
        self.code = code
        super(RocketAPIError, self).__init__(msg)

    def __str__(self):
        return '%s - (code: %s)' % (self.msg, self.code)


class Rocket(object):
    """Provides access to the most features necessary for an API
    implementation. 

    Initialize with api_key and api_secret_key, both available from
    sailthru
    """

    def __init__(self, api_key, api_secret_key, client='rocket',
                 proxy=None, api_url=None, api_url_secure=None):
        """Initializes a new Rocket which provides wrappers for the
        API implementation.
        """
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.proxy = proxy
        self.api_url = api_url
        self.api_url_secure = api_url_secure

        for namespace in self.function_list:
            self.__dict__[namespace] = eval('%sProxy(self, \'%s\')'
                                            % (namespace.title(),
                                               '%s.%s' % (client, namespace)))

            
    def _expand_arguments(self, args):
        """Expands arguments from native type to web friendly type"""
        for arg in args.items():
            if type(arg[1]) == list:
                args[arg[0]] = ','.join(str(a) for a in arg[1])
            elif type(arg[1]) == unicode:
                args[arg[0]] = arg[1].encode("UTF-8")
            elif type(arg[1]) == bool:
                args[arg[0]] = str(arg[1]).lower()
        return args


    def _hash_args(self, args, hash_alg=md5):
        """Hashes arguments by joining key=value pairs, appending a
        secret, and then taking the MD5 hex digest.
        """
        s = ''.join(['%s=%s' % (isinstance(x, unicode)
                                and x.encode("utf-8")
                                or x,
                                isinstance(args[x], unicode)
                                and args[x].encode("utf-8")
                                or args[x])
                     for x in sorted(args.keys())])
        return hash_alg(s).hexdigest()
    

    def _get_sorted_value_hash(self, args, hash_alg=md5):
        """Generates an API signature hash by flattening the arguments
        into a sorted list of values. It then creates the hash by
        entering self.api_secret_key + sorted values into hash_algorithm.

        The default hash algorithm is md5 (which defaults to hashlib.md5).

        Any algorithm may be used as long as it implements hexdigest()
        """
        arranged_args = sorted(self._extract_param_values(args))
        s = self.api_secret_key + ''.join(arranged_args)
        return hash_alg(s).hexdigest()
    

    def _extract_param_values(self, params):
        """Creates a flattened list of values from params dict"""
        values = []
        def inspect(i):
            if type(i) == dict:
                map(inspect, i.values())
            else:
                return values.append(i)
        map(inspect, params.values())
        return values
    

    def _parse_response(self, response, method, format=DEFAULT_RESPONSE_FORMAT):
        """Parses the response according to the given (optional) format,
        which should be 'json'.
        """
        if format == RESPONSE_JSON:
            json = response[2]
            result = json_decode(json)
            self.check_error(result)
        else:
            raise RuntimeError('Invalid format specified.')
        return result


    def __call__(self, function=None, args=None, secure=False,
                 format=DEFAULT_RESPONSE_FORMAT):
        """Mediator for calls to dynamic methods. Constructs environment
        based on arguments and calls appropriate Proxy object for
        function behavior.
        """
        
        # for Django templates, if this object is called without any arguments
        # return the object itself
        if function is None:
            return self

        # Entries in function_list are app_name.[namespace.]function.method
        fun_parts = function.split('.')
        num_parts = len(fun_parts)
        if num_parts < 3:
            raise rocket.RocketError('Incorrect function_list definition')

        obj_name = fun_parts[0]
        # function is everything between 
        function = '.'.join(fun_parts[1:(num_parts-1)])
        method = fun_parts[-1]

        args = self.build_query_args(method, args=args, format=format)

        api_url = self.api_url
        if secure:
            api_url = self.api_url_secure
        query_url = self.gen_query_url(api_url, function, format=format,
                                       get_args=args)

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler(self.proxy)
            opener = urllib2.build_opener(proxy_handler)
            response = opener.open(query_url).read()
        else:
            response = urlread(query_url, data=args, method=method.upper())

        return self._parse_response(response, method)


    def check_error(self, response):
        """Checks if the given Api response is an error, and then raises
        the appropriate exception.
        """
        reason = 'Rocket.check_error method not implemented'
        raise RuntimeError(reason)

    
    def gen_query_url(self, url, function, format=DEFAULT_RESPONSE_FORMAT,
                      get_args=None):
        """Generates URL for request according to structure of IDL.

        Implementation formats worth considering:
            url/function.format
            url/function
        """
        return '%s/%s.%s' % (url, function, format)

    
    def build_query_args(self, method, args=None,
                         format=DEFAULT_RESPONSE_FORMAT,
                         signing_alg=None):
        """Adds to args parameters that are necessary for every call to
        the API.
        """
        if args is None:
            raise RuntimeError('Arguments required for call to '
                               'build_query_args')

        if signing_alg == None:
            signing_alg = self._hash_args

        args = self._expand_arguments(args)
        
        args['api_key'] = self.api_key
        args['format'] = format
        args['sig'] = signing_alg(args)

        return args


