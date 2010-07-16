======
Rocket
======

Rocket is a library for quickly implementing a client-side API. 

Rocket is licensed under the `Link Apache Licence, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_


Features
========

It uses an interface description language, specified by API implementors,
to generate Python code that implements each API call. 

Rocket is designed to help programmers focus on the details of an API
implementation, rather than the details of implementing an API.

If a remote API consists of only one function, called 'email', which goes over
HTTP POST and takes two arguments email and vars, which vars being optional,
your API implementation will look close to this.

::

FUNCTIONS = {
    'email': {
        'post': [
            ('email', str, []),
            ('vars', rocket.json, ['optional']),
        ],
    }

That's all the code required. Sometimes there are slight differences in
how an API works, such as how a reques is signed. There are two functions
for use here _hash_args and _get_sorted_value_hash. Please read your API's
documentation to determine which one to use, if you need one, or please
write your own and send me a copy for inclusion.


Install It
==========

::

    python ./setup.py install

pip support on the way


Author
======

James Dennis <<james@extension.fm>>
