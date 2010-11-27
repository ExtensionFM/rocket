rocket_sailthru
===============

rocket_sailthru is a Python library for interfacing with 
`Sailthru's API <http://docs.sailthru.com/api>`_

rocket_sailthru is licensed under the `Apache Licence, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_


Using
-----

Using rocket_sailthru is easy. Install rocket and then rocket_sailthru
from the modules directory.

Then, it's as simple as:

::

    from r_sailthru import Sailthru
    
    if __name__ == '__main__':
        api_key = ''
        api_secret_key = ''
    
        template_name = 'welcome template'
        email_address = 'ih@ve.one'
    
        sailthru = Sailthru(api_key=api_key, api_secret_key=api_secret_key)
    
        send_id = sailthru.send.post(template_name, email_address)
        print send_id
    

Install
-------

::

    python ./setup.py install

rocket_sailthru depends on Rocket being installed.
http://github.com/ExtensionFM/rocket

pip / easy_install support on the way

James Dennis <james@extension.fm>
