r_twitter
==============

r_twitter is a Python library for interfacing with the `Twitter API
<http://apiwiki.twitter.com/w/page/22554679/Twitter-API-Documentation>`_

r_twitter is licensed under the `Apache Licence, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_


Using
-----

r_twitter is not a complete twitter implementation at this time. 

Searching twitter is implemented and I use it frequently. That looks
like:

::

    from r_twitter import Twitter

    twitter = Twitter()

    search_query = '@j2labs'
    response_dict = twitter.search.get(search_query)

    print 'TWEETS:'
    for tweet in response_dict['results']:
        print '  %s: %s' % (tweet['from_user'], tweet['text'])


Install
-------

::

    python ./setup.py install

r_twitter depends on Rocket being installed.
http://github.com/ExtensionFM/rocket

pip / easy_install support on the way

James Dennis <james@extension.fm>
