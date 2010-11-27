#! /usr/bin/env python
#
# twilio with rocket

from r_twilio import Twilio

if __name__ == '__main__':
    api_key = ''
    api_secret_key = ''
    basic_auth_realm='Twilio API'
    basic_auth_pair = (api_key, api_secret_key)

    twilio = Twilio(api_key=api_key, api_secret_key=api_secret_key,
                    basic_auth_pair=basic_auth_pair,
                    basic_auth_realm=basic_auth_realm)    

    to_number = '123-123-1234'
    from_number = '123-123-1234'
    body = 'a little texty text'

    response = twilio.SMSMessages.post(To=to_number,
                                       From=from_number,
                                       Body=body)
    print response

