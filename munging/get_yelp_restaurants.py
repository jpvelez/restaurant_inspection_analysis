import sqlite3
import json
import oauth2
import urllib
import urllib2

# Load randomized recent restaurant inspections. Restaurant names and addresses will be used to query yelp api.
conn = sqlite3.connect('../data/food_inspections.db')
c = conn.cursor()
c.execute('SELECT * FROM inspections_clean_restaurants_recent_normalized_randomized')

inspections = c.fetchall()

# Set oauth keys and search parameters
consumer_key = '88Ql36BiQPTsKqqUuIgIRA'
consumer_secret = 'd1Q1raKJppyMnDrRlTLj1cj2ygc'
token = 'vcge_k4r6cIFFPTt0AX1Elde6izhLtv0'
token_secret = '5qFxwx4vmMU_86lI6ftxDdFo0Pc'

offset = ''
limit = '10'
host = 'api.yelp.com'

json_output = open('../data/yelp_restaurants.json', 'w+')   # saves json response

# Try to fetch yelp data for each restaurant in recent inspection dataset
for rest in inspections[1900:2100]:

    # Setup restaurant name and location
    name = rest[2]
    address = rest[6]
    inspection_id = rest[0] 
    location = address + ", Chicago, IL"

    if not name:
        print 'restaurant name required'
    if not location:
        print 'restaurant location required'

    # Setup URL params using restaurant name/location and search parameters defined above
    url_params = {}

    if name:
        url_params['term'] = name
    if location:
        url_params['location'] = location
    if offset:
        url_params['offset'] = offset
    if limit:
        url_params['limit'] = limit


    def request(host, path, url_params, consumer_key, consumer_secret, token, token_secret):
        """Returns response for API request."""

        # Unsigned URL
        encoded_params = ''
        if url_params:
            encoded_params = urllib.urlencode(url_params)
        url = 'http://%s%s?%s' % (host, path, encoded_params)
        print 'URL: %s' % (url,)

        # Sign the URL
        consumer = oauth2.Consumer(consumer_key, consumer_secret)
        oauth_request = oauth2.Request('GET', url, {})
        oauth_request.update({'oauth_nonce': oauth2.generate_nonce(),
                                'oauth_timestamp': oauth2.generate_timestamp(),
                                'oauth_token': token,
                                'oauth_consumer_key': consumer_key})
        token = oauth2.Token(token, token_secret)
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


    # Query the api
    response = request(host, '/v2/search', url_params, consumer_key, consumer_secret, token, token_secret)

    # Associate inspected restaurant used to call api with api response
    inspection_restaurant = {}
    inspection_restaurant['name'] = name
    inspection_restaurant['address'] = address
    inspection_restaurant['inspection_id'] = inspection_id
    response['inspection_restaurant'] = inspection_restaurant

    # Print response + associated restaurant
    print json.dumps(response, sort_keys=True, indent=2)   

    # Save response + associated restaurant to output file (data/yelp_restaurants.json)
    json.dump(response, json_output)
    json_output.write("\n")



