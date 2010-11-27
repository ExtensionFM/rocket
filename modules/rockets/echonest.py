#!/usr/bin/env python

from r_echonest import EchoNest

if __name__ == "__main__":
    # This is the api key from their examples page
    echo_rocket = EchoNest(api_key='N6E4NIOVYMTHNDM8J')

    import pprint

    rocket_response = echo_rocket.artistprofile.get(name="Radiohead")
    pprint.pprint(rocket_response)

    rocket_response = echo_rocket.songsearch.get(title="Karma Police")
    pprint.pprint(rocket_response)
