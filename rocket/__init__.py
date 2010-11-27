#!/usr/bin/env python

__doc__ = """rocket - implementing api's with a quickness

For more information, see: http://github.com/extensionfm/rocket
"""

__all__ = [ 'rocket', 'proxies', 'http_handlers', 'auth' ]


import sys
import logging

from http_handling import RocketAPIException
from rocket import Rocket, json
from rocket import RocketException
