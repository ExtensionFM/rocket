#!/usr/bin/env python

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    
import logging
import sys
    

########################################
# Key signing functions ################
########################################


def _join_kv_pairs(args, hash_alg=md5):
    """Joins key-value pairs for hash algorithms"""
    s = ''.join(['%s=%s' % (isinstance(x, unicode)
                            and x.encode("utf-8")
                            or x,
                            isinstance(args[x], unicode)
                            and args[x].encode("utf-8")
                            or args[x])
                 for x in sorted(args.keys())])
    return s


def _extract_param_values(params):
    """Creates a flattened list of values from params dict"""
    values = []
    def inspect(i):
        if type(i) == dict:
            map(inspect, i.values())
        else:
            return values.append(i)
    map(inspect, params.values())
    return values


def sign_args(args, api_secret_key, hash_alg=md5):
    """Generates an API signature by joining 'key=value' pairs,
    appending a secret, and then returns hash_alg.hexdigest().

        hash_alg(kv_pairs + secret).hexdigest()
    """
    s = _join_kv_pairs(args, hash_alg=hash_alg)
    # note: this algorithm postfixes s with the key
    hash_input = s + api_secret_key
    return hash_alg(hash_input).hexdigest()


def sign_sorted_values(args, api_secret_key, hash_alg=md5):
    """Generates an API signature by flattening the arguments
    into a sorted list of values. It then creates the hash by
    entering self.api_secret_key + sorted values into hash_alg().

    The default hash algorithm is md5 (which defaults to hashlib.md5).

    Any algorithm may be used as long as it implements hexdigest()
    """
    values = _extract_param_values(args)
    arranged_args = sorted(values)
    s = ''.join(arranged_args)
    # note: this algorithm prefixes s with the key
    hash_input = api_secret_key + s
    return hash_alg(hash_input).hexdigest()



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

#######################################################
# Namespace generation functions.                     #
#######################################################

def gen_ns_pair_default(ns):
    """A namespace pair represents the name of the object a programmer
    interacts with (first part) and a titled version of that name for
    use with object creation.

        rocket.(first part).function()
    """
    return (ns.lower(), ns.title())


def gen_ns_pair_slash_delim(ns):
    """Similar to gen_ns_pair_default but allows a '/' in the namespace
    field. If any of the split segments consist entirely of upper case
    letters, they stay upper case. They are title()'d otherwise to
    create a usual looking object name.

    SMS/Messages => ('SMSMessages', 'SMSMessages')
      or
    user/noted   => ('usernoted', 'UserNoted')

    returns ('dynamic function name', 'dynamic class name')
    """
    def title_if_lower(nnss):
        if not nnss.isupper():
            return nnss.title()
        return nnss
    
    n_parts = ns.split('/')
    ns_fun = ''.join(n_parts)
    ns_title = ''.join([title_if_lower(n) for n in n_parts])
    return (ns_fun, ns_title)



##

def r_log(log_stream=sys.stdout,log_level=logging.INFO):

    logger = logging.getLogger("logger_rocket")
    #lowest lever the logger can tolerate, set to debug
    logger.setLevel(logging.DEBUG)
    
    # set stream from user, user sys.stdout as rocket default
    ch = logging.StreamHandler( log_stream )
    # set the log level requested by user, default is logging.info
    ch.setLevel( log_level )
    formatter = logging.Formatter("%(asctime)s %(process)d %(filename)s %(lineno)d %(levelname)s #rocket| %(message)s") 
    ch.setFormatter(formatter)
    logger.addHandler(ch)        
    
    return logger



