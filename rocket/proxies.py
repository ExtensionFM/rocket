#!/usr/bin/env python

import logging
import sys
import rocket

#########################################
# Namespace management functions ########
#########################################

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

    
def generate_proxies(function_list, doc_fun=None, 
                     gen_namespace_pair=gen_ns_pair_default,
                     logger=logging.getLogger()):
    """Helper function for compiling function_list into runnable code.
    Run immediately after definition.
    """
    logger.debug("Creating rockets %s \n" % function_list )

    proxies = {}
    
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

                # We jsonify the argument if it's a list or a dict. 
                if param_type == rocket.json:
                    body.append('if isinstance(%s, list) or isinstance(%s, dict): %s = json_encode(%s)'
                                % ((param_name,) * 4))

                # Optional variables default to None
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

        (ns_name, ns_title) = gen_namespace_pair(namespace)

        proxy = type('%sProxy' % ns_title, (Proxy, ), methods)
        proxies[proxy.__name__] = proxy
    return proxies


