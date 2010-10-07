#! /usr/bin/env python
#
# rocket - implementing with a quickness
#
# This module's design is influenced by the work of 
# Samuel Cormier-Iijima and team on the pyfacebook module.
# http://github.com/sciyoshi/pyfacebook/
#
# Props.

import sys
import time
import struct
import urllib
import urllib2
import httplib
import binascii
import urlparse
import mimetypes
import logging


from utils import sign_args
from utils import gen_ns_pair_default
from utils import r_log

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    
RESPONSE_JSON = 'json'
DEFAULT_RESPONSE_FORMAT = RESPONSE_JSON
DEFAULT_REQUEST_METHOD = 'GET'


### Would like a hand making this appengine safe
try:
    from json import dumps as json_encode
    from json import loads as json_decode
except ImportError:
    try:
        from simplejson import dumps as json_encode
        from simplejson import loads as json_decode
    except ImportError:
        quit('Rocket requires json support')


# create json object for referencing complex structures in function_list
class json(object): pass


########################################
# URL handling #########################
########################################

def encode_auth_pair(basic_auth_pair):
    """Base64 encodes a username and password delimited by ':'.
    It then returns 'Basic EnCoDedStriNG.
    """
    if basic_auth_pair:
        import base64
        unencoded = '%s:%s' % basic_auth_pair
        ba_str = base64.encodestring(unencoded)[:-1]
        return 'Basic %s ' % ba_str


def urlread(url, data=None, headers={}, method=DEFAULT_REQUEST_METHOD,
            basic_auth_pair=None, basic_auth_realm=None, log_stream=sys.stderr, log_level=logging.DEBUG):
    """Takes a url[, data, headers, request method].

    It establishes an httplib.HTTPConnection and allows
    specific HTTP connection types, like POST, PUT, DELETE
    for API interaction.

    POST sends 'application/x-www-form-urlencoded' for it's
    Content-type

    Returns a tuple of (status code, reason, any data read)
    """
    logger = r_log( log_stream=log_stream, log_level=log_level )
    if data is not None:
        data = urllib.urlencode(data)

    # encoded_args = unicode_urlencode(encoded_args)
    
    if method == 'GET':
        if data is not None:
            url = '%s?%s' % (url, data)
            logger.debug("Make %s connection to %s" % ( method, data ) )
        data = None

    if basic_auth_pair:
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm=basic_auth_realm,
                                  uri=url,
                                  user=basic_auth_pair[0],
                                  passwd=basic_auth_pair[1])
        opener = urllib2.build_opener(auth_handler)
        # ...and install it globally so it can be used with urlopen.
        urllib2.install_opener(opener)

    request = urllib2.Request(url, data)
    try:
        open_req = urllib2.urlopen(request)
        #if method == 'POST':
        #    req.add_header('Content-type', "application/x-www-form-urlencoded")
        #    req.add_header('Accept', "text/plain")
        open_req.http_method = method
    except urllib2.HTTPError, http_e:
        raise RocketAPIError( http_e.code,  http_e )
    except urllib2.URLError,e:
        logger.warn("Connection error %s" % e)
        raise RocketError( e )
    except Exception,e:
        logger.critical("uknown error %s" % e )
        raise RocketError( e )        
        
    return (open_req.code, open_req.msg, open_req.read())  
    #return (r.status, r.reason, r.read())



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

    def __init__(self, client, name, gen_namespace_pair=gen_ns_pair_default):
        self._client = client
        self._name = name
        self.gen_namespace_pair = gen_namespace_pair

    def __call__(self, method=None, args=None, add_session_args=True):
        # for Django templates, if this object is called without any arguments
        # return the object itself
        if method is None:
            return self

        return self._client('%s.%s' % (self._name, method), args)

    
def generate_proxies(function_list, doc_fun=None, foreign_globals={},
                     gen_namespace_pair=gen_ns_pair_default, log_stream=sys.stdout, log_level=logging.INFO):
    """Helper function for compiling function_list into runnable code.
    Run immediately after definition.
    """
    logger = r_log( log_stream=log_stream, log_level=log_level )
    logger.debug("Creating rockets %s \n" % function_list )
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
            if doc_fun:
                body.insert(0, doc_fun(namespace, method))
            body.insert(0, 'def %s(%s):' % (method, ', '.join(params)))
            body.append('return self(\'%s\', args)' % method)
            exec('\n    '.join(body))
            methods[method] = eval(method)

        # Sometimes namespaces need calm down a little bit
        (ns_name, ns_title) = gen_namespace_pair(namespace)

        proxy = type('%sProxy' % ns_title, (Proxy, ), methods)
        globals()[proxy.__name__] = proxy
        foreign_globals[proxy.__name__] = proxy


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
    """Provides access to most features necessary for an API
    implementation. 

    Initialize with api_key and api_secret_key, both available from
    sailthru
    """

    def __init__(self, api_key=None, api_secret_key=None, client='rocket',
                 proxy=None, api_url=None, api_url_secure=None,
                 basic_auth_pair=None, basic_auth_realm=None,
                 gen_namespace_pair=gen_ns_pair_default, 
                 log_stream=sys.stdout, 
                 log_level=logging.INFO
                 ):
        """Initializes a new Rocket which provides wrappers for the
        API implementation.

        The namespace map saves a namespace as it originally appeared in FUNCTIONS
        """
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.proxy = proxy
        self.api_url = api_url;
        self.api_url_secure = api_url_secure
        self.basic_auth_pair = basic_auth_pair
        self.basic_auth_realm = basic_auth_realm
        self.gen_namespace_pair = gen_namespace_pair
        self.namespace_map = {}
        self._log_level=log_level
        self._log_stream=log_stream
        
        
        logger = r_log()
        logger.debug("Create rocket: url: %s client %s" % (api_url,client) )



        for namespace in self.function_list:
            (ns_name, ns_title) = self.gen_namespace_pair(namespace)
            self.__dict__[ns_name] = eval('%sProxy(self, \'%s\')'
                                          % (ns_title,
                                             '%s.%s' % (client, ns_name)))
            self.namespace_map[ns_name] = namespace
            
            
    def _expand_arguments(self, args):
        """Expands arguments from native type to web friendly type"""

        logger = r_log()
        logger.debug("rocket _expand_arguments %s" % args )
        for arg in args.items():
            if type(arg[1]) == list:
                args[arg[0]] = ','.join(str(a) for a in arg[1])
            elif type(arg[1]) == unicode:
                args[arg[0]] = arg[1].encode("UTF-8")
            elif type(arg[1]) == bool:
                args[arg[0]] = str(arg[1]).lower()
        return args


    def _parse_response(self, response, method, format=DEFAULT_RESPONSE_FORMAT):
        """Parses the response according to the given (optional) format,
        which should be 'json'.
        """
        logger = r_log()
        logger.debug("rocket _parse_response, response=%s and method=%s" % (response, method) )
        if format == RESPONSE_JSON:
            json = response[2]
            result = json_decode(json)
            self.check_error(result)
        else:
            logger.critical( response )
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

        # Entries in function_list are app_name.[namespace]function.method
        fun_parts = function.split('.')
        num_parts = len(fun_parts)
        if num_parts < 3:
            raise rocket.RocketError('Incorrect function_list definition')

        obj_name = fun_parts[0]
        namespace = fun_parts[1]
        method = fun_parts[2]
        (ns_fun, ns_title) = self.gen_namespace_pair(namespace)

        args = self.build_query_args(method, args=args, format=format)

        api_url = self.api_url
        if secure:
            api_url = self.api_url_secure
        query_url = self.gen_query_url(api_url, ns_fun, format=format,
                                       method=method, get_args=args)

        if self.proxy:
            proxy_handler = urllib2.ProxyHandler(self.proxy)
            opener = urllib2.build_opener(proxy_handler)
            response = opener.open(query_url).read()
        else:

            response = urlread(query_url, data=args, method=method.upper(),
                           basic_auth_pair=self.basic_auth_pair,
                           basic_auth_realm=self.basic_auth_realm,
                           log_level=self._log_level,
                           log_stream=self._log_stream)
        
            if response:
                return self._parse_response(response, method)
            else:
                return None
        
        return response


    def check_error(self, response):
        """Checks if the given Api response is an error, and then raises
        the appropriate exception.
        """
        reason = 'Rocket.check_error method not implemented'
        raise RuntimeError(reason)

    
    def gen_query_url(self, url, function, format=DEFAULT_RESPONSE_FORMAT,
                      method="get", get_args=None):
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



        args = self._expand_arguments(args)
        
        if self.api_key:
            args['api_key'] = self.api_key
        args['format'] = format
        
        if self.api_key and self.api_secret_key:
            
            if signing_alg == None:
                signing_alg = sign_args            
            
            args['sig'] = signing_alg(args, self.api_secret_key)

        return args


