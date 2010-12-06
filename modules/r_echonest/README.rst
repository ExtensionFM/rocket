r_echonest
==========

r_echonest is a Python library for interfacing with 
`Echonest's API <http://http://developer.echonest.com/docs/v4/>`_

r_echonest is licensed under the `Apache Licence, Version 2.0 
<http://www.apache.org/licenses/LICENSE-2.0.html>`_


Using
-----

Using r_echonest is easy. Install rocket and then r_echonest
from the modules directory included with Rocket. Using it looks
like this:

::

    from r_echonest import EchoNest
    echo_rocket = EchoNest(api_key='N6E4NIOVYMTHNDM8J') # key from their demos
    rocket_response = echo_rocket.artistprofile.get(name="Radiohead")
    

Install
-------

::

    python ./setup.py install

r_echonest depends on Rocket being installed.
http://github.com/ExtensionFM/rocket

pip / easy_install support on the way

James Dennis <james@extension.fm>
