import csv
import json

yelp_data = open('yelp_restaurants_0-500.json')

result_list = []
for response in yelp_data:
    result = []
    last_inspection_status = response['inspection_restaurant']['inspection_status']
    yelp_rating = response['businesses'][0]['rating']
    result.append( # response id, name, inspection, rating, lat/long
    result_list.append(result)

    csv.writer(result_list) # maybe do this in the for loop


