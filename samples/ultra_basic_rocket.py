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

# tell rocket what methods this api has
rocket.generate_proxies(FUNCTIONS, foreign_globals=globals() )


class ViewTest( rocket.Rocket ):
    
    def __init__(self, *args, **kwargs):
        # give rocket some api 'functions' 
        # this is formatted in the gen_query_url
        self.function_list = FUNCTIONS
        # the name of your class, in this case: ViewTest
        # you can configure a lot more, see pysailthru for more usage
        super(ViewTest, self).__init__( api_url=API_BASE_URL, *args, **kwargs )
        
    
    ## API Error responses: define a behavior for errors:
    def check_error(self, response):
        """Checks if the given API response is an error, and then raises
        the appropriate exception.
        """
        if type(response) is dict and response.has_key('error'):
            raise rocket.RocketAPIError(response['error'], response['errormsg'])
            
    ## API query format, how does this API need queries?
    def gen_query_url(self, url, function, **kwargs ):
        ## http://viewtext.org/api/text?url=extension.fm&format=json
        ## for this example
        ## url = http://viewtext.org/api
        ## function = text
        ## rocket will auto append format=json, (we just say **kwargs to let rocket handle other keywords) 
        ## you can override this, see pysailthru example for deeper usage
        return "%s/%s" % ( url, function )
    

if __name__ == "__main__":
    # simple test, scape the test of the extension.fm site, returns json, print to screen
    simple_rocket = ViewTest()
    # actually call the api now
    rocket_response = simple_rocket.text.get("extension.fm")
    print rocket_response
        