#! /usr/bin/env python

from r_exfm import EXFM
import logging

logging.basicConfig(level=logging.DEBUG)

# This is a glimpse at the API. Perhaps you're interested in helping us document it?

if __name__ == "__main__":
    e = EXFM()
    print 'j2d2\'s user profile:\n\n  %s\n' % (e.userprofileget.get('j2d2'))
    print 'j2d2\'s most recent noted:\n\n  %s\n' % (e.usernotedget.get(owner='j2d2', count=1, start=0))
