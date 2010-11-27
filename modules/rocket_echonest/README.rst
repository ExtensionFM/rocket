rocket_echonest
===============

rocket_echonest is a Python library for interfacing with 
`Echonest's API <http://http://developer.echonest.com/docs/v4/>`_

rocket_echonest is licensed under the `Apache Licence, Version 2.0 
<http://www.apache.org/licenses/LICENSE-2.0.html>`_


Using
-----

Using rocket_echonest is easy. Install rocket and then rocket_echonest
from the modules directory.

Using looks like this:

::

    from r_echonest import EchoNest
    echo_rocket = EchoNest(api_key='N6E4NIOVYMTHNDM8J')
    rocket_response = echo_rocket.artistprofile.get(name="Radiohead")
    

Install
-------

::

    python ./setup.py install

rocket_echonest depends on Rocket being installed.
http://github.com/ExtensionFM/rocket

pip / easy_install support on the way

James Dennis <james@extension.fm>
