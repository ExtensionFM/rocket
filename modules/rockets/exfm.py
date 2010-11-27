#! /usr/bin/env python

from r_exfm import EXFM

# This is a glimpse at the API. Perhaps you're interested in helping us document it?

if __name__ == "__main__":
    e = EXFM()
    print e.userprofileget.get('j2d2')
    print e.usernotedget.get('j2d2')
