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


import proxies
from auth import sign_args
import http_handling

try:
    from hashlib import md5
except ImportError:
    from md5 import md5



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


#########################################
# Rocket Errors #########################
#########################################

class RocketException(Exception):
    """Exception class for errors received from Rocket."""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return '%s' % (self.msg)
    

#########################################
# Logging context #######################
#########################################

def logging_context(log_stream=sys.stdout, log_level=logging.INFO):
    logger = logging.getLogger("logger_rocket")
    logger.setLevel(log_level)
    
    # set stream from user, user sys.stdout as rocket default
    sh = logging.StreamHandler( log_stream )
    # set the log level requested by user, default is logging.info
    sh.setLevel( log_level )
    formatter = logging.Formatter("%(asctime)s %(process)d %(filename)s %(lineno)d %(levelname)s #rocket| %(message)s") 
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    
    return logger    


#########################################
# The Rocket ############################
#########################################

class Rocket(object):
    """Provides access to most features necessary for an API
    implementation. 

    All configuration options are keywords, since every API is different.
    """

    def __init__(self, function_list,
                 client='rocket', gen_doc_str=None,
                 api_key=None, api_secret_key=None,
                 api_url=None, api_url_secure=None,
                 basic_auth_pair=None, basic_auth_realm=None,
                 web_proxy=None, format=http_handling.DEFAULT_RESPONSE_FORMAT,
                 gen_namespace_pair=proxies.gen_ns_pair_default, 
                 log_stream=sys.stdout, log_level=logging.INFO,
                 *args, **kwargs):
        """Initializes a new Rocket which provides wrappers for the
        API implementation.

        The namespace map saves a namespace as it originally appeared in
        FUNCTIONS
        """
        self.function_list = function_list
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.format = format
        self.web_proxy = web_proxy
        self.api_url = api_url
        self.api_url_secure = api_url_secure
        self.basic_auth_pair = basic_auth_pair
        self.basic_auth_realm = basic_auth_realm
        self.gen_namespace_pair = gen_namespace_pair
        self._log_level=log_level
        self._log_stream=log_stream
        
        logger = logging_context(log_stream=log_stream, log_level=log_level)
        logger.debug("Create rocket: url: %s client %s" % (api_url,client))

        rocket_proxies = proxies.generate_proxies(function_list,
                                                  gen_doc_str,
                                                  logger=logger)

        self.namespace_map = {}
        for namespace in self.function_list:
            (ns_name, ns_title) = self.gen_namespace_pair(namespace)
            proxy_class = rocket_proxies['%sProxy' % ns_title]
            self.__dict__[ns_name] = proxy_class(self,
                                                 '%s.%s' % (client, ns_name))
            self.namespace_map[ns_name] = namespace
            
            
    def _expand_arguments(self, args):
        """Expands arguments from native type to web friendly type
        """
        logger = logging_context(log_stream=self._log_stream, log_level=self._log_level)
        logger.debug("rocket _expand_arguments %s" % args )
        
        for arg in args.items():
            if type(arg[1]) == list:
                args[arg[0]] = ','.join(str(a) for a in arg[1])
            elif type(arg[1]) == unicode:
                args[arg[0]] = arg[1].encode("UTF-8")
            elif type(arg[1]) == bool:
                args[arg[0]] = str(arg[1]).lower()
        return args


    def _parse_response(self, response, method):
        """Parses the response according to the given (optional) format,
        which should be 'json'.
        """
        logger = logging_context(log_stream=self._log_stream, log_level=self._log_level)
        logger.debug("rocket _parse_response, response=%s and method=%s"
                     % (response, method) )
        
        if self.format == http_handling.RESPONSE_JSON:
            json = response[2]
            result = json_decode(json)
            self.check_error(result)
        else:
            logger.critical( response )
            raise RuntimeError('Invalid format specified.')
        return result


    def __call__(self, function=None, args=None, secure=False):
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
            raise rocket.RocketException('Incorrect function_list definition')

        # Break the function name into three parts:
        #     object name, namespace, http connection method
        obj_name = fun_parts[0]
        namespace = '.'.join(fun_parts[1:-1])
        method = fun_parts[-1]
        (ns_fun, ns_title) = self.gen_namespace_pair(namespace)

        args = self.build_query_args(method, args=args)

        api_url = self.api_url
        if secure:
            api_url = self.api_url_secure
        query_url = self.gen_query_url(api_url, ns_fun, 
                                       format=self.format,
                                       method=method,
                                       get_args=args)

        if self.web_proxy:
            web_proxy_handler = urllib2.ProxyHandler(self.web_proxy)
            opener = urllib2.build_opener(web_proxy_handler)
            response = opener.open(query_url).read()
        else:
            response = http_handling.urlread(query_url, data=args,
                                             method=method.upper(),
                                             basic_auth_pair=self.basic_auth_pair,
                                             basic_auth_realm=self.basic_auth_realm,
                                             logger=logging_context())

            if response:
                return self._parse_response(response, method)
            else:
                return None
        
        return response

    
    ########################################
    # Callbacks ############################
    ########################################

    def check_error(self, response):
        """Some API's transmit errors over successful HTTP connections, eg. 200.

        Implement this function to handle parsing a response for errors.
        """
        pass

    
    def gen_query_url(self, url, function, method=None, get_args=None):
        """Generates URL for request according to structure of IDL.

        Implementation formats worth considering:
            url/function.format # self.format
            url/function
        """
        return '%s/%s' % (url, function)

    
    def build_query_args(self, method, args=None,
                         signing_alg=None):
        """Adds to args parameters that are necessary for every call to
        the API.
        """
        if args is None:
            raise RuntimeError('Arguments required for call to '
                               'build_query_args')

        args = self._expand_arguments(args)
        
        if self.format:
            args['format'] = self.format
        
        if self.api_key:
            args['api_key'] = self.api_key

        if self.api_secret_key:
            if signing_alg == None:
                signing_alg = sign_args            
            args['sig'] = signing_alg(args, self.api_secret_key)

        return args


