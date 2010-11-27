#! /usr/bin/env python
#
# sailthru - implementing with a quickness

from r_sailthru import Sailthru

if __name__ == '__main__':
    api_key = ''
    api_secret_key = ''

    email = 'ih@ve.one'

    sailthru = Sailthru(api_key=api_key, api_secret_key=api_secret_key)

    email_info = sailthru.email.get(email)
    print email_info

