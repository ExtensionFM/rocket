rocket_twilio
=============

rocket_twilio is a Python library for interfacing with the `Twilio API
<http://docs.twilio.com/api>`_

rocket_twilio is licensed under the `Apache Licence, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_


Using
-----

rocket_twilio is not a complete implementation at this time. I don't
think it would be a challenge to complete the API but I haven't had
time yet. Patches welcome!

Anyway, using SMS/Message, which is implemented looks like this:

::

    from r_twilio import Twilio

    api_key = ''
    api_secret_key = ''
    basic_auth_realm='Twilio API'
    basic_auth_pair = (api_key, api_secret_key)

    twilio = Twilio(api_key=api_key,
                    api_secret_key=api_secret_key,
                    basic_auth_pair=basic_auth_pair,
                    basic_auth_realm=basic_auth_realm)    

    to_number = '123-123-1234'
    from_number = '123-123-1234'
    body = 'a little texty text'

    response = twilio.SMSMessages.post(To=to_number,
                                       From=from_number,
                                       Body=body)

Install
-------

::

    python ./setup.py install

rocket_twilio depends on Rocket being installed.
http://github.com/ExtensionFM/rocket

pip / easy_install support on the way

James Dennis <james@extension.fm>
