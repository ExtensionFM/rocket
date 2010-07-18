#!/usr/bin/env python

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    

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



