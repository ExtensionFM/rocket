


##
# rocket not intalled, adjust path (remove when rocket is recompiled) 10/6/2010
##
import sys
import os
library_files = os.path.abspath(os.path.join( os.path.dirname(__file__), "../"))
sys.path.append(library_files)
# end not installed path adjust



import rocket

#http://viewtext.org/api/text


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
        self.function_list = FUNCTIONS
        # the name of your class, in this case: ViewTest
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
        ## rocket will auto append format=json, (we just say     **kwargs to let rocket handle othe keywords) 
        ## you can override this, see pysailthru example for deeper usage
        return "%s/%s" % ( url, function )
    

        
        
        
#
if __name__ == "__main__":
    simple_rocket = ViewTest()
    rocket_response = simple_rocket.text.get("extension.fm")
    print rocket_response
        