#!/usr/bin/env python

import rocket
from rocket.auth import sign_sorted_values
from rocket.proxies import gen_ns_pair_multi_delim

FUNCTIONS = {
    'artist/audio' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
        ],
    },
    'artist/biographies' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
            ("license", list, ['optional']),
        ],
    },
    'artist/blogs' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
            ("high_relevance", bool, ['optional']),
        ],
    },
    'artist/familiarity' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
        ],
    },
    'artist/hotttnesss' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("type", str, ['optional']),
        ],
    },
    'artist/images' : {
        'get' : [
            ("id", str, []),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
            ("license", str, ['optional']),
        ],
    },
    'artist/news' : {
        'get' : [
            ("id", str, []),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
            ("high_relevance", bool, ['optional']),
        ],
    },
    'artist/profile' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("bucket", str, ['optional']),
        ],
    },
    'artist/reviews' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
        ],
    },
    'artist/search' : {
        'get' : [
            ("results", int, ['optional']),
            ("bucket", str, ['optional']),
            ("limit", int, ['optional']),
            ("name", str, ['optional']),
            ("description", str, ['optional']),
            ("fuzzy_match", bool, ['optional']),
            ("max_familiarity", int, ['optional']),
            ("min_familiarity", int, ['optional']),
            ("max_hotttnesss", int, ['optional']),
            ("min_hotttnesss", int, ['optional']),
            ("sort", str, ['optional']),
        ],
    },
    'artist/songs' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
        ],
    },
    'artist/similar' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("min_results", int, ['optional']),
            ("start", int, ['optional']),
            ("bucket", str, ['optional']),
            ("max_familiarity", int, ['optional']),
            ("min_familiarity", int, ['optional']),
            ("max_hotttnesss", int, ['optional']),
            ("min_hotttnesss", int, ['optional']),
            ("reverse", bool, ['optional']),
            ("limit", bool, ['optional']),
            ("seed_catalog", bool, ['optional']),            
        ],
    },
    'artist/terms' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("sort", bool, ['optional']),            
        ],
    },
    'artist/top_hottt' : {
        'get' : [
            ("results", int, ['optional']),
            ("start", int, ['optional']),
            ("bucket", str, ['optional']),
            ("limit", bool, ['optional']),            
        ],
    },
    'artist/top_terms' : {
        'get' : [
            ("results", int, ['optional']),
        ],
    },
    'artist/urls' : {
        'get' : [
            ("id", str, ['optional']),
        ],
    },
    'artist/urls' : {
        'get' : [
            ("id", str, ['optional']),
        ],
    },
    'artist/video' : {
        'get' : [
            ("id", str, ['optional']),
            ("name", str, ['optional']),
            ("results", int, ['optional']),
            ("start", int, ['optional']),
        ],
    },
    'song/search' : {
        'get' : [
            ("title", str, ['optional']),
            ("artist", str, ['optional']),
            ("combined", str, ['optional']),
            ("description", str, ['optional']),            
            ("artist_id", str, ['optional']),            
            ("results", int, ['optional']),
            ("max_tempo", int, ['optional']),
            ("min_tempo", int, ['optional']),
            ("max_duration", int, ['optional']),
            ("min_duration", int, ['optional']),
            ("max_loudness", int, ['optional']),
            ("min_loudness", int, ['optional']),
            ("max_familiarity", int, ['optional']),
            ("artist_min_familiarity", int, ['optional']),
            ("max_hotness", int, ['optional']),
            ("min_hotness", int, ['optional']),
            ("max_longitude", int, ['optional']),
            ("min_longitude", int, ['optional']),
            ("max_latitude", int, ['optional']),
            ("min_latitude", int, ['optional']),
            ("max_danceability", int, ['optional']),
            ("min_danceability", int, ['optional']),
            ("max_energy", int, ['optional']),
            ("min_energy", int, ['optional']),
            ("mode", int, ['optional']),            
            ("key", str, ['optional']),            
            ("bucket", str, ['optional']),            
            ("sort", str, ['optional']),            
            ("limit", bool, ['optional']),
        ],
    },
    'song/profile' : {
        'get' : [
            ("bucket", str, ['optional']),            
            ("limit", bool, ['optional']),
        ],
    },
    # 'song/identify' # TODO this one is more involved
    # 'track/analyze'
    'track/profile' : {
        'get' : [
            ("id", str, ['optional']),
            ("md5", str, ['optional']),
            ("bucket", str, ['optional']),            
        ],
    },
    # 'track/upload'
    'playlist/static' : {
        'get' : [
            ("type", str, ['optional']),
            ("artist_pick", str, ['optional']),
            ("variety", int, ['optional']),
            ("artist_id", str, ['optional']),
            ("artist", str, ['optional']),
            ("artist_seed_catalog", str, ['optional']),
            ("song_id", str, ['optional']),
            ("description", str, ['optional']),
            ("results", int, ['optional']),
            ("max_tempo", int, ['optional']),
            ("min_tempo", int, ['optional']),
            ("max_duration", int, ['optional']),
            ("min_duration", int, ['optional']),
            ("max_loudness", int, ['optional']),
            ("min_loudness", int, ['optional']),
            ("max_danceability", int, ['optional']),
            ("min_danceability", int, ['optional']),
            ("max_energy", int, ['optional']),
            ("min_energy", int, ['optional']),
            ("artist_max_familiarity", int, ['optional']),
            ("artist_min_familiarity", int, ['optional']),
            ("song_max_hotttnesss", int, ['optional']),
            ("song_min_hotttnesss", int, ['optional']),
            ("max_latitude", int, ['optional']),
            ("min_latitude", int, ['optional']),
        ],
    },
}

API_BASE_URL = "http://developer.echonest.com/api/v4"


class EchoNest( rocket.Rocket ):
    def __init__(self, *args, **kwargs):
        super(EchoNest, self).__init__(FUNCTIONS,
                                       api_url=API_BASE_URL,
                                       gen_namespace_pair=gen_ns_pair_multi_delim,
                                       *args, **kwargs )
    
    def check_error(self, response):
        pass

    def gen_query_url(self, url, function, **kwargs ):
        return '%s/%s' % (url, self.namespace_map[function])
    

if __name__ == "__main__":
    echo_rocket = EchoNest(api_key='N6E4NIOVYMTHNDM8J')

    import pprint

    rocket_response = echo_rocket.artistprofile.get(name="Radiohead")
    pprint.pprint(rocket_response)

    rocket_response = echo_rocket.songsearch.get(title="Karma Police")
    pprint.pprint(rocket_response)
