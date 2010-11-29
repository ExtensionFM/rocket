#!/usr/bin/env python

# search twitter with rocket

from r_twitter import Twitter

if __name__ == '__main__':
    search_query = '@j2labs'

    twitter = Twitter()

    response_dict = twitter.search.get(search_query)
    print 'TWEETS:'
    for r in response_dict['results']:
        print '  %s: %s' % (r['from_user'], r['text'])
