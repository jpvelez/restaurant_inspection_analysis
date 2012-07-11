"""Gets restaurants from Yelp Search API for every neighborhood."""

import json
import oauth2
import urllib
import urllib2

nabe_list = ["Albany Park", "Andersonville", "Archer Heights", "Ashburn", "Auburn Gresham", "Austin", 
            "Avalon Park", "Avondale", "Back of the Yards", "Belmont Central", "Beverly", "Brainerd", 
            "Bridgeport", "Brighton Park", "Bronzeville", "Bucktown", "Burnside", "Cabrini-Green", 
            "Calumet Heights", "Canaryville", "Chatham", "Chicago Lawn", "Chinatown", "Clearing", 
            "Cragin", "DePaul", "Douglas", "Dunning", "East Garfield Park", "East Side", "Edgewater", 
            "Edison Park", "Englewood", "Forest Glen", "Fulton Market", "Gage Park", "Galewood", 
            "Garfield Ridge", "Gold Coast", "Goose Island", "Grand Boulevard", "Greater Grand Crossing", 
            "Greektown", "Hegewisch", "Hermosa", "Humboldt Park", "Hyde Park", "Irving Park", 
            "Jefferson Park", "Jeffery Manor", "Kenwood", "Lakeview", "Lawndale", "Lincoln Park", 
            "Lincoln Square", "Little Village", "Logan Square", "Magnificent Mile", "Marquette Park", 
            "McKinley Park", "Montclare", "Morgan Park", "Mount Greenwood", "Near North Side", 
            "Near Southside", "Near West Side", "New City", "Noble Square", "North Center", "North Park", 
            "Norwood Park", "Oakland", "O'Hare", "Old Town", "Pilsen", "Portage Park", "Printer's Row", 
            "Pullman", "Ravenswood", "River East", "River North", "River West", "Riverdale", "Rogers Park", 
            "Roscoe Village", "Roseland", "Sauganash", "Scottsdale", "South Chicago", "South Deering", 
            "South Loop", "South Shore", "Streeterville", "The Loop", "Tri-Taylor", "Ukrainian Village", 
            "University Village", "Uptown", "Washington Heights", "Washington Park", "West Elsdon", 
            "West Englewood", "West Garfield Park", "West Lawn", "West Loop", "West Pullman", "West Rogers Park", 
            "Wicker Park", "Woodlawn", "Wrigleyville"] 

# Options: oauth keys and search parameters
consumer_key = '88Ql36BiQPTsKqqUuIgIRA'
consumer_secret = 'd1Q1raKJppyMnDrRlTLj1cj2ygc'
token = 'vcge_k4r6cIFFPTt0AX1Elde6izhLtv0'
token_secret = '5qFxwx4vmMU_86lI6ftxDdFo0Pc'

term = 'restaurants'
offset = ''
limit = '20'
host = 'api.yelp.com'

json_output = open('../yelp_restaurants.json', 'w+')   # saves json response

for nabe in nabe_list:

    # Set the location based on user input
    location = nabe + ", Chicago, IL"

    if not location:
        print 'location required'

    # Setup URL params from options
    url_params = {}

    if term:
        url_params['term'] = term
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

        print 'GOT HERE'
        print 'token:', token, 'consumer_key:', consumer_key
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

    response['neighborhood'] = nabe   # add neighborhood to response dict to make it easier to summarize nabe totals

    # Display and save response data
    print json.dumps(response, sort_keys=True, indent=2)   # pretty prints json response

    json.dump(response, json_output)   # dumps data to output file 
    json_output.write("\n")

