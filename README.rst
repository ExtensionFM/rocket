======
Rocket
======

Rocket is a library for quickly implementing a client-side API. 

Rocket is licensed under the `Apache Licence, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_


Features
========

Rocket uses an interface description language, specified by Rocket implementors,
to generate Python code that implements each API call. 

Rocket is designed to help programmers focus on the details of an API
implementation, rather than the details of implementing an API.

If a remote API consists of only one namespace, called 'email', which goes over
HTTP POST and takes two arguments email and vars, with vars being optional,
your API implementation will look close to this.

::

    FUNCTIONS = {
        'email': {
            'post': [
                ('email', str, []),
                ('vars', rocket.json, ['optional']),
            ],
        }

That's as minimal as I've been able to get for describing an API. Perhaps
a different structure could be used, but the idea remains the same. To
describe the API in a language agnostic way and generate code that implements
it. 

Sometimes there are slight differences in how an API works, such as how a
each request is signed. There are two functions for use here _hash_args
and _get_sorted_value_hash. Please read your API's documentation to 
determine which one to use, if you need one, or please extend Rocket.


Modules
=======

Rocket comes with multiple API implementations, but they are not installed
by default. Currently packaged: Twilio, Sailthru, Echonest, Twitter, Exfm.

Each module has a setup.py for installing but Rocket doesn't install them
by default.

As bare-bones Rocket is available in modules/rocket_simple.


Code generation using proxies
=============================

Rocket has a module called proxies which contain some functions for
generating callable objects that process inputs in a somewhat generic
manner. Rocket uses this module for processing the FUNCTIONS Map (IDL)
into real Python objects. These objects get mapped to a subclass of
Rocket during __init__() to create the runnable implementation.

The gist of this mechanism is that the Proxy's represent a namespace
which has implementations of http protocol methods. The namespace 'email'
with 'post' method details is turned into the class EmailProxy with a
function 'post' that takes one argument 'email' and has a keyword 
argument that defaults to None, since it's optional, but takes a json
structure for encoding.

The Rocket itself is what maps this data into http calls. Rocket then
parses the response and attempts to return real python objects representing
the data. It throws a RocketAPIException in the event it can't do so.

See rocket.proxies.py for more information. 


Http handling
=============

Rocket's http_handling.py module contains a few functions for handling
rocket's http interactions. The main function here is urlread() which
takes some arguments for tweaking the call, like which http method
(GET, POST, DELETE) to use or if basic_auth should be turned on.

Functionality for file handling will be in there soon but is not complete.


Auth
====

Auth currently contains some functions for signing API requests and
basic_auth. For request signatures, sign_args and sign_sorted_values 
are available. Often enough a timestamp can be used to limit the 
lifespan of the signature.

sign_args takes the request arguments, the secret key and a hashing
algorithm (defaults to md5). This algorithm concatenates strings of
the arguments, like arg1=val1arg2=val2, and generates the key like:

::
  
    # get string of args like 'arg1=val1arg2=val2'
    s = _join_kv_pairs(args, hash_alg=hash_alg)
    # note: this algorithm *postfixes* s with the key
    hash_input = s + api_secret_key
    return hash_alg(hash_input).hexdigest()

sign_sorted_values is similar, but it's signature string is a sorted
list of the request's values, like 'avalue1value2zebra1' and prefixes
this string with the secret key for it's signature.

Each API is different. :)

::

    # extact flattened list of values found in args
    values = _extract_param_values(args)
    arranged_args = sorted(values)
    s = ''.join(arranged_args)
    # note: this algorithm *prefixes* s with the key
    hash_input = api_secret_key + s 
    return hash_alg(hash_input).hexdigest()


Callbacks
=========

To implement a Rocket you subclass Rocket and then make use of callbacks
to adjust functionality. Most common are adjustments to how query urls are
made, how errors are handled when you receive http 200 responses regardless
of errors or how query arguments are handled before you send them to the
remote source.

rocket_sailthru is a good example of how check_error, build_query_args and
gen_query_url can be used. Here is how each one works.

::

    def check_error(self, response):
        """Checks if the given API response is an error, and then raises
        the appropriate exception.
        """
        if type(response) is dict and response.has_key('error'):
            raise rocket.RocketAPIException(response['error'], response['errormsg'])

We see that check_error receives a response, which was parsed from json 
into a python dict called response. We found that it had an error key,
so we raise an exception containing the error info found in the dict.

::

    def build_query_args(self, *args, **kwargs):
        """Overrides Rocket's build_query_arg to set signing_alg to
        sign_sorted_values
        """
        return super(Sailthru, self).build_query_args(signing_alg=sign_sorted_values,
                                                      *args, **kwargs)

The sailthru API requires signing our requests, but Rocket makes no
assumptions on signing by default. We override build_query_args to
call build_query_args with sign_sorted_values for it's signing
algorithm. sign_sorted_values, along with some other choices, are
implemented in Rocket's auth module.

::

    def gen_query_url(self, url, function, format=None, method=None, get_args=None):
        """Sailthru urls look like 'url/function'.

        Example: http://api.sailthru.com/email
        """
        return '%s/%s' % (url, function)

The callback handles the data known about the call and generates the
URL string that handles the call. Each API is different here, so this
callback allows the flexibility of looking at the relevant information
and generating what you think it is.

Sometimes namespaces are complicated and instead of being simple like
'email' they have some complexity like 'group/subgroup.method'. Rocket
handles this by offering additional functions to handle how that string
is translated into dynamics objects.

Let's look at one: rocket.proxies import gen_ns_pair_multi_delim.

:: 

    def gen_ns_pair_multi_delim(ns, delims=['\/', '\.']):
        """..."""
        def title_if_lower(nnss):
            if not nnss.isupper():
                return nnss.title()
            return nnss
    
        groups = re.split('|'.join(delims), ns) 
        ns_fun = ''.join(groups)
        ns_title = ''.join([title_if_lower(g) for g in groups])
        return (ns_fun, ns_title)

    
The purpose of this function is to generate namespace keys from the
string found in the FUNCTIONS list. If we see 'SMS/Messages', like 
found in rocket_twilio, we translate this to 'SMSMessages' and 
'SMSMessages' which are then used for twilio.SMSMessages.post(...)
and 'SMSMessagesProxy', as attached to the Rocket.

Often enough, you won't need these overrides, but you'll be happy 
rocket handles a few of them easily when they come up.


Install It
==========

::

    python ./setup.py install

pip / easy_install support on the way


Author
======

James Dennis <james@extension.fm>
