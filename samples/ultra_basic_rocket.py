#!/usr/bin/env python

try:
    import rocket
except:
    print "fail over to the rocket in the repos struct"
    import sys
    import os
    sys.path.append( os.path.abspath(os.path.join( os.path.dirname(__file__), "../"))  )
    import rocket

FUNCTIONS = {
    'text' : {
        'get' : [
            ("url", str, []),
        ],
    }
}

API_BASE_URL = "http://viewtext.org/api"

# Tell rocket what methods this api has
rocket.generate_proxies(FUNCTIONS, foreign_globals=globals() )


class ViewTest( rocket.Rocket ):
    
    def __init__(self, *args, **kwargs):
        """We instantiate ViewTest with the IDL (FUNCTIONS) as the only required
        argument. 

        ViewText uses http (not https) so we supply an api_url, in addition
        to the IDL defined as FUNCTIONS. api_url_secure could be supplied for
        https support.
        
        The available config options are listed as keywords in Rocket's __init__.
        """
        super(ViewTest, self).__init__( FUNCTIONS, api_url=API_BASE_URL,
                                        *args, **kwargs )
        
    
    def check_error(self, response):
        """Some API's transmit errors over successful HTTP connections, eg. 200.
        Implement this function to handle parsing a successful response for errors.

        We don't need this kind of error checking for viewtext, so pass is used
        """
        pass
            
    ## API query format, how does this API need queries?
    def gen_query_url(self, url, function, **kwargs ):
        """The query url should look like:

            http://viewtext.org/api/text?url=extension.fm&format=json
            
        gen_query_url receives the url and function as below
        
            url = http://viewtext.org/api
            function = text

        To construct this, we can do: '%s/%s' % (url, function)
        That is rocket's default implementation so we can just call:

            super(...).gen_query_url(...)
            
        """
        return super(ViewTest, self).gen_query_url(url, function, **kwargs)
    

if __name__ == "__main__":
    # simple test, scape the test of the extension.fm site, returns json, print to screen
    simple_rocket = ViewTest()
    # actually call the api now
    rocket_response = simple_rocket.text.get("extension.fm")
    print rocket_response
        
