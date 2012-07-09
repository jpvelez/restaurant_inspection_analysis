"""Command line interface to the Yelp Search API."""
"""WORKING NOW"""

import json
import oauth2
import urllib
import urllib2

class YelpApi(object):
    def __init__(self, location):
    # Options: oauth keys and search parameters
        self.consumer_key = '88Ql36BiQPTsKqqUuIgIRA'
        self.consumer_secret = 'd1Q1raKJppyMnDrRlTLj1cj2ygc'
        self.token = 'vcge_k4r6cIFFPTt0AX1Elde6izhLtv0'
        self.token_secret = '5qFxwx4vmMU_86lI6ftxDdFo0Pc'

        self.term = 'restaurants'
        self.offset = ''
        self.limit = '20'
        self.host = 'api.yelp.com'
        self.path = '/v2/search'


    
    def request(self, location):
        """Returns response for API request."""
    
        # Setup URL params from options
        url_params = {}
        url_params['term'] = self.term
        url_params['location'] = location
        url_params['offset'] = self.offset
        url_params['limit'] = self.limit

        # Unsigned URL
        encoded_params = ''
        if url_params:
            encoded_params = urllib.urlencode(url_params)
        url = 'http://%s%s?%s' % (self.host, self.path, encoded_params)
        print 'URL: %s' % (url,)

        # Sign the URL
        consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)
        oauth_request = oauth2.Request('GET', url, {})
        oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                                'oauth_timestamp': oauth2.generate_timestamp(),
                                'oauth_token': self.token,
                                'oauth_self.consumer_key': self.consumer_key})

        token = oauth2.Token(self.token, self.token_secret)
        oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
        signed_url = oauth_request.to_url()
        print 'Signed URL: %s\n' % (signed_url,)

        # Connect
        try:
            conn = urllib2.urlopen(signed_url, None)
            try:
                response = json.loads(conn.read())
            finally:
                conn.close()
        except urllib2.HTTPError, error:
            response = json.loads(error.read())

        return response

#         response = request(self.host, '/v2/search', url_params, self.consumer_key, self.consumer_secret, token, token_secret)
# 
#         print json.dumps(response, sort_keys=True, indent=2)   # pretty prints json response
# 
#         output_file = open('../yelp_restaurants.json', 'w+')   # saves json response
#         json.dump(response, output_file) 
# 
