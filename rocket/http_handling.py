#!/usr/bin/env python

import logging
import sys
import urllib
import urllib2
import httplib


RESPONSE_JSON = 'json'
DEFAULT_RESPONSE_FORMAT = RESPONSE_JSON
DEFAULT_REQUEST_METHOD = 'GET'


class RocketAPIException(Exception):
    """Exception class for errors received from the API."""

    def __init__(self, code, msg):
        self.code = code
        super(RocketAPIException, self).__init__(msg)

    def __str__(self):
        return '%s - (code: %s)' % (self.msg, self.code)


########################################
# URL handling #########################
########################################


def urlread(url, data=None, headers={}, method=DEFAULT_REQUEST_METHOD,
            basic_auth_pair=None, basic_auth_realm=None,
            logger=logging.getLogger()):
    """Takes a url[, data, headers, request method].

    It establishes an httplib.HTTPConnection and allows
    specific HTTP connection types, like POST, PUT, DELETE
    for API interaction.

    # commenting out a comment (so meta)
    # POST sends 'application/x-www-form-urlencoded' for it's
    # Content-type

    Returns a tuple of (status code, reason, any data read)
    """
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
        # commenting out the code the commented comment comments on
        #if method == 'POST':
        #    req.add_header('Content-type', "application/x-www-form-urlencoded")
        #    req.add_header('Accept', "text/plain")
        open_req.http_method = method
    except urllib2.HTTPError, http_e:
        print 'HTTP E: %s' % http_e
        raise RocketAPIException( http_e.code,  http_e )
    except urllib2.URLError,e:
        logger.warn("Connection error %s" % e)
        raise RocketAPIError(None, e )
    except Exception,e:
        logger.critical("uknown error %s" % e )
        raise 
        
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
# File handling functions ##############
########################################

def encode_multipart_formdata(self, fields, files):
    """Encodes a multipart/form-data message to upload an image."""
    boundary = '-------tHISiStheMulTIFoRMbOUNDaRY'
    crlf = '\r\n'
    l = []

    for (key, value) in fields:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"' % str(key))
        l.append('')
        l.append(str(value))
    for (filename, value) in files:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; filename="%s"' % (str(filename), ))
        l.append('Content-Type: %s' % self.__get_content_type(filename))
        l.append('')
        l.append(value.getvalue())
    l.append('--' + boundary + '--')
    l.append('')
    body = crlf.join(l)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body

